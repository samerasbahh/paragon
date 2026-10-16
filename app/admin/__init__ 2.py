"""Admin panel: login, dashboard and editors for every part of the site."""
import csv
import io
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from functools import wraps

from flask import (Blueprint, Response, abort, current_app, flash, g, redirect, render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_

from ..content import (HERO_SLOTS, ICON_NAMES, SETTINGS_SCHEMA, delete_photo_files, make_og, process_image, process_logo,
                       set_setting, slugify)
from ..extensions import db
from ..models import (Block, Client, ContractType, Inquiry, Item, Photo, Project, Sector, Service, Setting, Stat, User)

admin = Blueprint("admin", __name__, template_folder="../templates/admin")

ITEM_GROUPS = {  # group: (title, has_text, has_icon, has_link, help)
    "hero_chips": ("Home: header badges", False, True, False, "Small badges under the home page header buttons."),
    "ticker": ("Home: scrolling words", False, False, False, "Words that scroll along the bottom of the home page header."),
    "stages": ("Delivery stages", False, True, False, "The numbered steps on the Home and About pages."),
    "about_values": ("About: what drives us", True, True, False, "Cards in the 'What drives us' section of the About page."),
    "about_sectors": ("About: sector tags", False, False, True, "Tags under the About intro. Link = sector key to filter projects (e.g. residential)."),
    "ws_why": ("Workshops: why us", True, True, False, "The 'Why us' cards on the Workshops page."),
    "contact_checks": ("Contact form: key points", False, True, False, "Bullet points beside every contact form. Simple HTML like <b> is allowed."),
}

PAGE_LABELS = {
    "nav": "Menu", "ui": "Buttons & labels", "footer": "Footer", "home": "Home page", "about": "About page",
    "services": "Services page", "projects": "Projects page", "project": "Project pages", "clients": "Clients page",
    "workshops": "Workshops page", "contact": "Contact page", "contact_block": "Contact section",
    "form": "Contact form", "cta": "Call-to-action band", "clients_block": "Clients section", "stats": "Numbers bar",
    "seo": "Search engines", "404": "Not-found page",
}


@admin.before_request
def set_admin_lang():
    g.lang = "en"


@admin.context_processor
def admin_ctx():
    unread = Inquiry.query.filter_by(is_read=False).count() if current_user.is_authenticated else 0
    return dict(unread_count=unread, ITEM_GROUPS=ITEM_GROUPS, PAGE_LABELS=PAGE_LABELS, ICON_NAMES=ICON_NAMES)


def f(name, default=""):
    return (request.form.get(name) or default).strip()


def set_bilingual(obj, *fields):
    for fld in fields:
        setattr(obj, f"{fld}_en", f(f"{fld}_en"))
        setattr(obj, f"{fld}_ar", f(f"{fld}_ar"))


def to_int(value, default=0):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def all_photos():
    return Photo.query.order_by(Photo.gallery, Photo.project_id, Photo.position).all()


def save_photo_uploads(field, gallery, project=None, folder="uploads/photos"):
    added = 0
    files = [fs for fs in request.files.getlist(field) if fs and fs.filename]
    start = (max([ph.position for ph in project.photos], default=0) + 1) if project else \
        (db.session.query(func.max(Photo.position)).filter_by(gallery=gallery).scalar() or 0) + 1
    for i, fs in enumerate(files):
        try:
            data = process_image(fs, folder)
        except Exception:
            flash(f"Could not read “{fs.filename}”. Please upload JPG, PNG or WebP images.", "error")
            continue
        ph = Photo(gallery=gallery, position=start + i, **data)
        if project is not None:
            project.photos.append(ph)
        else:
            db.session.add(ph)
        added += 1
    return added


def update_photo_rows(photos):
    """Apply alt text / order / delete edits submitted for a list of photos."""
    removed = 0
    for ph in list(photos):
        if request.form.get(f"ph-{ph.id}-delete"):
            delete_photo_files(ph)
            db.session.delete(ph)
            removed += 1
            continue
        ph.alt_en = f(f"ph-{ph.id}-alt_en")
        ph.alt_ar = f(f"ph-{ph.id}-alt_ar")
        ph.position = to_int(request.form.get(f"ph-{ph.id}-position"), ph.position)
    return removed


# --------------------------------------------------------------------------- auth
_failures = defaultdict(deque)


def _locked(ip):
    q = _failures[ip]
    now = time.time()
    while q and now - q[0] > 900:
        q.popleft()
    return len(q) >= 5


@admin.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    if request.method == "POST":
        if _locked(ip):
            flash("Too many failed attempts. Please wait 15 minutes and try again.", "error")
            return render_template("admin/login.html"), 429
        user = User.query.filter(func.lower(User.email) == f("email").lower()).first()
        if user and user.active and user.check_password(request.form.get("password", "")):
            login_user(user, remember=bool(request.form.get("remember")))
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            nxt = request.args.get("next", "")
            return redirect(nxt if nxt.startswith("/admin") else url_for("admin.dashboard"))
        _failures[ip].append(time.time())
        flash("Incorrect email or password.", "error")
    return render_template("admin/login.html")


@admin.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "ok")
    return redirect(url_for("admin.login"))


@admin.route("/")
@login_required
def dashboard():
    stats = dict(
        projects=Project.query.count(), published=Project.query.filter_by(published=True).count(),
        photos=Photo.query.count(), clients=Client.query.count(), services=Service.query.count(),
        inquiries=Inquiry.query.count(), unread=Inquiry.query.filter_by(is_read=False).count(),
    )
    recent = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(6).all()
    updated = Project.query.order_by(Project.updated_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent=recent, updated=updated)


# --------------------------------------------------------------------------- projects
@admin.route("/projects")
@login_required
def projects():
    q = request.args.get("q", "").strip()
    sector = request.args.get("sector", "")
    query = Project.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Project.name_en.ilike(like), Project.name_ar.ilike(like), Project.slug.ilike(like),
                                 Project.location_en.ilike(like)))
    if sector:
        query = query.join(Sector).filter(Sector.key == sector)
    rows = query.order_by(Project.position, Project.id).all()
    return render_template("admin/projects.html", rows=rows, q=q, sector=sector, sectors=Sector.query.order_by(Sector.position).all())


@admin.route("/projects/order", methods=["POST"])
@login_required
def projects_order():
    for p in Project.query.all():
        if f"pos-{p.id}" in request.form:
            p.position = to_int(request.form.get(f"pos-{p.id}"), p.position)
            p.published = bool(request.form.get(f"pub-{p.id}"))
            p.featured = bool(request.form.get(f"feat-{p.id}"))
    db.session.commit()
    flash("Project order and visibility saved.", "ok")
    return redirect(url_for("admin.projects"))


@admin.route("/projects/new", methods=["GET", "POST"])
@admin.route("/projects/<int:pid>", methods=["GET", "POST"])
@login_required
def project_edit(pid=None):
    p = db.session.get(Project, pid) if pid else None
    if pid and p is None:
        abort(404)
    if request.method == "POST":
        is_new = p is None
        if is_new:
            p = Project(position=(db.session.query(func.max(Project.position)).scalar() or 0) + 1)
        set_bilingual(p, "name", "location", "date_text", "description", "seo_title", "seo_desc")
        if not p.name_en:
            flash("The English project name is required.", "error")
            db.session.rollback()
            return redirect(request.url)
        slug = slugify(f("slug") or p.name_en)
        with db.session.no_autoflush:
            clash = Project.query.filter(Project.slug == slug, Project.id != (p.id or 0)).first()
        if clash:
            slug = f"{slug}-{int(time.time()) % 10000}"
        p.slug = slug
        db.session.add(p)
        p.sector_id = to_int(f("sector_id")) or None
        p.contract_id = to_int(f("contract_id")) or None
        p.year = to_int(f("year")) or None
        p.month = to_int(f("month")) or None
        p.status = "ongoing" if f("status") == "ongoing" else "done"
        p.auto_intro = bool(request.form.get("auto_intro"))
        p.published = bool(request.form.get("published"))
        p.featured = bool(request.form.get("featured"))
        p.featured_position = to_int(f("featured_position"), 0)
        ids = [to_int(x) for x in request.form.getlist("client_ids")]
        p.clients = Client.query.filter(Client.id.in_(ids)).all() if ids else []
        db.session.flush()
        removed = update_photo_rows(p.photos)
        added = save_photo_uploads("photos", "project", p, folder=f"uploads/projects/{p.slug}")
        db.session.flush()
        cover = to_int(f("cover_id"))
        p.cover_id = cover if cover and any(ph.id == cover for ph in p.photos) else (p.photos[0].id if p.photos else None)
        db.session.commit()
        make_og(p.cover_photo, p.slug)
        msg = "Project created." if is_new else "Project saved."
        if added:
            msg += f" {added} photo(s) uploaded."
        if removed:
            msg += f" {removed} photo(s) deleted."
        flash(msg, "ok")
        return redirect(url_for("admin.project_edit", pid=p.id))
    return render_template("admin/project_edit.html", p=p, sectors=Sector.query.order_by(Sector.position).all(),
                           contracts=ContractType.query.order_by(ContractType.position).all(),
                           clients=Client.query.order_by(Client.position).all())


@admin.route("/projects/<int:pid>/delete", methods=["POST"])
@login_required
def project_delete(pid):
    p = db.session.get(Project, pid) or abort(404)
    for ph in p.photos:
        delete_photo_files(ph)
    p.cover_id = None
    db.session.flush()
    db.session.delete(p)
    db.session.commit()
    flash("Project deleted.", "ok")
    return redirect(url_for("admin.projects"))


# --------------------------------------------------------------------------- clients
@admin.route("/clients", methods=["GET", "POST"])
@login_required
def clients():
    rows = Client.query.order_by(Client.position, Client.id).all()
    if request.method == "POST":
        for c in rows:
            c.position = to_int(request.form.get(f"pos-{c.id}"), c.position)
            c.published = bool(request.form.get(f"pub-{c.id}"))
        db.session.commit()
        flash("Client order saved.", "ok")
        return redirect(url_for("admin.clients"))
    return render_template("admin/clients.html", rows=rows)


@admin.route("/clients/new", methods=["GET", "POST"])
@admin.route("/clients/<int:cid>", methods=["GET", "POST"])
@login_required
def client_edit(cid=None):
    c = db.session.get(Client, cid) if cid else None
    if cid and c is None:
        abort(404)
    if request.method == "POST":
        if c is None:
            c = Client(position=(db.session.query(func.max(Client.position)).scalar() or 0) + 1)
        set_bilingual(c, "name")
        if not c.name_en:
            flash("The English client name is required.", "error")
            db.session.rollback()
            return redirect(request.url)
        key = slugify(f("key") or c.name_en)
        with db.session.no_autoflush:
            if Client.query.filter(Client.key == key, Client.id != (c.id or 0)).first():
                key = f"{key}-{int(time.time()) % 10000}"
        c.key = key
        db.session.add(c)
        c.published = bool(request.form.get("published"))
        ids = [to_int(x) for x in request.form.getlist("project_ids")]
        c.projects = Project.query.filter(Project.id.in_(ids)).all() if ids else []
        logo = request.files.get("logo")
        if logo and logo.filename:
            try:
                c.logo_path = process_logo(logo, key)
            except Exception:
                flash("Could not read the logo file. Please upload PNG, JPG or WebP.", "error")
        db.session.commit()
        flash("Client saved.", "ok")
        return redirect(url_for("admin.client_edit", cid=c.id))
    return render_template("admin/client_edit.html", c=c, projects=Project.query.order_by(Project.position).all())


@admin.route("/clients/<int:cid>/delete", methods=["POST"])
@login_required
def client_delete(cid):
    c = db.session.get(Client, cid) or abort(404)
    db.session.delete(c)
    db.session.commit()
    flash("Client deleted.", "ok")
    return redirect(url_for("admin.clients"))


# --------------------------------------------------------------------------- services
@admin.route("/services", methods=["GET", "POST"])
@login_required
def services():
    rows = Service.query.order_by(Service.position, Service.id).all()
    if request.method == "POST":
        for sv in rows:
            sv.position = to_int(request.form.get(f"pos-{sv.id}"), sv.position)
            sv.published = bool(request.form.get(f"pub-{sv.id}"))
        db.session.commit()
        flash("Service order saved.", "ok")
        return redirect(url_for("admin.services"))
    return render_template("admin/services.html", rows=rows)


@admin.route("/services/new", methods=["GET", "POST"])
@admin.route("/services/<int:sid>", methods=["GET", "POST"])
@login_required
def service_edit(sid=None):
    sv = db.session.get(Service, sid) if sid else None
    if sid and sv is None:
        abort(404)
    if request.method == "POST":
        if sv is None:
            sv = Service(position=(db.session.query(func.max(Service.position)).scalar() or 0) + 1)
        set_bilingual(sv, "title", "short", "text", "features", "extra_link")
        if not sv.title_en:
            flash("The English title is required.", "error")
            db.session.rollback()
            return redirect(request.url)
        slug = slugify(f("slug") or sv.title_en)
        with db.session.no_autoflush:
            if Service.query.filter(Service.slug == slug, Service.id != (sv.id or 0)).first():
                slug = f"{slug}-{int(time.time()) % 10000}"
        sv.slug = slug
        db.session.add(sv)
        sv.icon = f("icon") if f("icon") in ICON_NAMES else "pen"
        sv.extra_link_url = f("extra_link_url")
        sv.published = bool(request.form.get("published"))
        uploaded = request.files.get("photo_upload")
        if uploaded and uploaded.filename:
            data = process_image(uploaded, "uploads/library")
            ph = Photo(gallery="library", **data)
            db.session.add(ph)
            db.session.flush()
            sv.photo_id = ph.id
        else:
            sv.photo_id = to_int(f("photo_id")) or None
        db.session.commit()
        flash("Service saved.", "ok")
        return redirect(url_for("admin.service_edit", sid=sv.id))
    return render_template("admin/service_edit.html", sv=sv, photos=all_photos())


@admin.route("/services/<int:sid>/delete", methods=["POST"])
@login_required
def service_delete(sid):
    sv = db.session.get(Service, sid) or abort(404)
    db.session.delete(sv)
    db.session.commit()
    flash("Service deleted.", "ok")
    return redirect(url_for("admin.services"))


# --------------------------------------------------------------------------- sectors & contract types
@admin.route("/sectors", methods=["GET", "POST"])
@login_required
def sectors():
    rows = Sector.query.order_by(Sector.position).all()
    if request.method == "POST":
        action = f("action")
        if action == "add":
            key = slugify(f("new_key") or f("new_name_en"))
            if not f("new_name_en"):
                flash("Enter the new sector's English name.", "error")
            elif Sector.query.filter_by(key=key).first():
                flash("A sector with that key already exists.", "error")
            else:
                db.session.add(Sector(key=key, name_en=f("new_name_en"), name_ar=f("new_name_ar"), position=len(rows) + 1))
                db.session.commit()
                flash("Sector added.", "ok")
            return redirect(url_for("admin.sectors"))
        for sec in rows:
            if request.form.get(f"del-{sec.id}"):
                if Project.query.filter_by(sector_id=sec.id).count():
                    flash(f"“{sec.name_en}” still has projects, so it was not deleted.", "error")
                else:
                    db.session.delete(sec)
                continue
            sec.name_en = f(f"name_en-{sec.id}")
            sec.name_ar = f(f"name_ar-{sec.id}")
            sec.position = to_int(f(f"pos-{sec.id}"), sec.position)
            sec.cover_id = to_int(f(f"cover-{sec.id}")) or None
        db.session.commit()
        flash("Sectors saved.", "ok")
        return redirect(url_for("admin.sectors"))
    return render_template("admin/sectors.html", rows=rows, photos=all_photos(),
                           contracts=ContractType.query.order_by(ContractType.position).all())


@admin.route("/contracts", methods=["POST"])
@login_required
def contracts():
    rows = ContractType.query.order_by(ContractType.position).all()
    if f("action") == "add":
        key = slugify(f("new_key") or f("new_name_en"))
        if f("new_name_en") and not ContractType.query.filter_by(key=key).first():
            db.session.add(ContractType(key=key, name_en=f("new_name_en"), name_ar=f("new_name_ar"), position=len(rows) + 1))
            db.session.commit()
            flash("Contract type added.", "ok")
        else:
            flash("Enter a new, unique contract type name.", "error")
        return redirect(url_for("admin.sectors"))
    for c in rows:
        if request.form.get(f"cdel-{c.id}"):
            if Project.query.filter_by(contract_id=c.id).count():
                flash(f"“{c.name_en}” is used by projects, so it was not deleted.", "error")
            else:
                db.session.delete(c)
            continue
        c.name_en = f(f"cname_en-{c.id}")
        c.name_ar = f(f"cname_ar-{c.id}")
        c.position = to_int(f(f"cpos-{c.id}"), c.position)
    db.session.commit()
    flash("Contract types saved.", "ok")
    return redirect(url_for("admin.sectors"))


# --------------------------------------------------------------------------- numbers & lists
@admin.route("/stats", methods=["GET", "POST"])
@login_required
def stats():
    rows = Stat.query.order_by(Stat.position).all()
    if request.method == "POST":
        for st in rows:
            if request.form.get(f"del-{st.id}"):
                db.session.delete(st)
                continue
            st.number = to_int(f(f"number-{st.id}"), st.number)
            st.suffix = f(f"suffix-{st.id}")[:8]
            st.label_en = f(f"label_en-{st.id}")
            st.label_ar = f(f"label_ar-{st.id}")
            st.position = to_int(f(f"pos-{st.id}"), st.position)
        if f("new_label_en"):
            db.session.add(Stat(number=to_int(f("new_number")), suffix=f("new_suffix")[:8], label_en=f("new_label_en"),
                                label_ar=f("new_label_ar"), position=len(rows) + 1))
        db.session.commit()
        flash("Numbers saved.", "ok")
        return redirect(url_for("admin.stats"))
    return render_template("admin/stats.html", rows=rows)


@admin.route("/lists/<group>", methods=["GET", "POST"])
@login_required
def lists(group):
    if group not in ITEM_GROUPS:
        abort(404)
    title, has_text, has_icon, has_link, help_text = ITEM_GROUPS[group]
    rows = Item.query.filter_by(group=group).order_by(Item.position, Item.id).all()
    if request.method == "POST":
        for it in rows:
            if request.form.get(f"del-{it.id}"):
                db.session.delete(it)
                continue
            it.title_en = f(f"title_en-{it.id}")
            it.title_ar = f(f"title_ar-{it.id}")
            it.text_en = f(f"text_en-{it.id}")
            it.text_ar = f(f"text_ar-{it.id}")
            it.icon = f(f"icon-{it.id}")
            it.link = f(f"link-{it.id}")
            it.position = to_int(f(f"pos-{it.id}"), it.position)
        if f("new_title_en"):
            db.session.add(Item(group=group, title_en=f("new_title_en"), title_ar=f("new_title_ar"), text_en=f("new_text_en"),
                                text_ar=f("new_text_ar"), icon=f("new_icon"), link=f("new_link"), position=len(rows) + 1))
        db.session.commit()
        flash("List saved.", "ok")
        return redirect(url_for("admin.lists", group=group))
    return render_template("admin/lists.html", group=group, title=title, has_text=has_text, has_icon=has_icon,
                           has_link=has_link, help_text=help_text, rows=rows)


# --------------------------------------------------------------------------- page texts
@admin.route("/texts")
@login_required
def texts():
    q = request.args.get("q", "").strip()
    pages = db.session.query(Block.page, func.count(Block.key)).group_by(Block.page).all()
    order = list(PAGE_LABELS)
    pages.sort(key=lambda r: (order.index(r[0]) if r[0] in order else 99, r[0]))
    results = []
    if q:
        like = f"%{q}%"
        results = Block.query.filter(or_(Block.en.ilike(like), Block.ar.ilike(like), Block.key.ilike(like))).order_by(Block.page, Block.position).limit(200).all()
    return render_template("admin/texts.html", pages=pages, q=q, results=results)


@admin.route("/texts/<page>", methods=["GET", "POST"])
@login_required
def texts_page(page):
    rows = Block.query.filter_by(page=page).order_by(Block.position, Block.key).all()
    if not rows:
        abort(404)
    if request.method == "POST":
        for blk in rows:
            if f"en-{blk.key}" in request.form:
                if request.form.get(f"reset-{blk.key}"):
                    blk.en, blk.ar = blk.default_en, blk.default_ar
                else:
                    blk.en = request.form.get(f"en-{blk.key}", "").strip()
                    blk.ar = request.form.get(f"ar-{blk.key}", "").strip()
        db.session.commit()
        flash("Texts saved. Changes are live on the website.", "ok")
        return redirect(url_for("admin.texts_page", page=page))
    return render_template("admin/texts_page.html", page=page, rows=rows)


# --------------------------------------------------------------------------- images: page photos, workshops gallery, library
@admin.route("/images", methods=["GET", "POST"])
@login_required
def images():
    if request.method == "POST":
        added = save_photo_uploads("library_upload", "library", folder="uploads/library")
        for key, _label in HERO_SLOTS:
            if f"slot-{key}" in request.form:
                set_setting(key, f(f"slot-{key}"))
        db.session.commit()
        from ..content import photo_by_path
        for key, og in (("hero_home", "home"), ("hero_services", "services"), ("hero_projects", "projects"),
                        ("hero_workshops", "workshops"), ("hero_contact", "contact")):
            row = db.session.get(Setting, key)
            if row and row.en:
                make_og(photo_by_path(row.en), og)
        flash("Page photos saved." + (f" {added} photo(s) added to the library." if added else ""), "ok")
        return redirect(url_for("admin.images"))
    current = {k: (db.session.get(Setting, k).en if db.session.get(Setting, k) else "") for k, _ in HERO_SLOTS}
    return render_template("admin/images.html", slots=HERO_SLOTS, current=current, photos=all_photos())


@admin.route("/workshops", methods=["GET", "POST"])
@login_required
def workshops():
    photos = Photo.query.filter_by(gallery="workshops").order_by(Photo.position).all()
    if request.method == "POST":
        removed = update_photo_rows(photos)
        added = save_photo_uploads("photos", "workshops", folder="uploads/workshops")
        db.session.commit()
        flash(f"Workshop gallery saved. {added} added, {removed} deleted.", "ok")
        return redirect(url_for("admin.workshops"))
    return render_template("admin/workshops.html", photos=photos)


@admin.route("/library/<int:phid>/delete", methods=["POST"])
@login_required
def library_delete(phid):
    ph = db.session.get(Photo, phid) or abort(404)
    if ph.gallery != "library":
        abort(400)
    in_use = Service.query.filter_by(photo_id=ph.id).count() + Sector.query.filter_by(cover_id=ph.id).count() + \
        Setting.query.filter_by(en=ph.path).count()
    if in_use:
        flash("That photo is in use on the site, so it was not deleted.", "error")
    else:
        delete_photo_files(ph)
        db.session.delete(ph)
        db.session.commit()
        flash("Photo deleted.", "ok")
    return redirect(url_for("admin.images"))


# --------------------------------------------------------------------------- settings
@admin.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        for _group, fields in SETTINGS_SCHEMA:
            for key, _label, bilingual, _help in fields:
                set_setting(key, f(f"{key}_en"), f(f"{key}_ar") if bilingual else "")
        db.session.commit()
        flash("Settings saved.", "ok")
        return redirect(url_for("admin.settings"))
    values = {row.key: row for row in Setting.query.all()}
    mail_ok = bool(current_app.config.get("MAIL_SERVER"))
    return render_template("admin/settings.html", schema=SETTINGS_SCHEMA, values=values, mail_ok=mail_ok)


# --------------------------------------------------------------------------- inquiries
@admin.route("/inquiries")
@login_required
def inquiries():
    show = request.args.get("show", "all")
    query = Inquiry.query
    if show == "unread":
        query = query.filter_by(is_read=False)
    rows = query.order_by(Inquiry.created_at.desc()).all()
    return render_template("admin/inquiries.html", rows=rows, show=show)


@admin.route("/inquiries/<int:iid>", methods=["GET", "POST"])
@login_required
def inquiry_view(iid):
    inq = db.session.get(Inquiry, iid) or abort(404)
    if request.method == "POST":
        if f("action") == "delete":
            db.session.delete(inq)
            db.session.commit()
            flash("Inquiry deleted.", "ok")
            return redirect(url_for("admin.inquiries"))
        inq.is_read = f("action") != "unread"
        db.session.commit()
        return redirect(url_for("admin.inquiries"))
    if not inq.is_read:
        inq.is_read = True
        db.session.commit()
    return render_template("admin/inquiry.html", inq=inq)


@admin.route("/inquiries.csv")
@login_required
def inquiries_csv():
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Date", "Name", "Email", "Phone", "Location", "Service", "Details", "Language"])
    for i in Inquiry.query.order_by(Inquiry.created_at.desc()).all():
        w.writerow([i.created_at.strftime("%Y-%m-%d %H:%M") if i.created_at else "", i.name, i.email, i.phone, i.location,
                    i.service, i.details, i.lang])
    return Response("﻿" + buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=paragon-inquiries.csv"})


# --------------------------------------------------------------------------- users
@admin.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if request.method == "POST":
        email = f("email").lower()
        pw = request.form.get("password", "")
        if "@" not in email or len(pw) < 10:
            flash("Enter a valid email and a password of at least 10 characters.", "error")
        elif User.query.filter(func.lower(User.email) == email).first():
            flash("A user with that email already exists.", "error")
        else:
            u = User(email=email, name=f("name"))
            u.set_password(pw)
            db.session.add(u)
            db.session.commit()
            flash(f"Admin user {email} added.", "ok")
        return redirect(url_for("admin.users"))
    return render_template("admin/users.html", rows=User.query.order_by(User.created_at).all())


@admin.route("/users/<int:uid>", methods=["POST"])
@login_required
def user_update(uid):
    u = db.session.get(User, uid) or abort(404)
    action = f("action")
    active_admins = User.query.filter_by(active=True).count()
    if action == "toggle":
        if u.id == current_user.id:
            flash("You can't deactivate your own account.", "error")
        elif u.active and active_admins <= 1:
            flash("At least one active admin is required.", "error")
        else:
            u.active = not u.active
            flash(f"{u.email} is now {'active' if u.active else 'deactivated'}.", "ok")
    elif action == "password":
        pw = request.form.get("password", "")
        if len(pw) < 10:
            flash("Passwords need at least 10 characters.", "error")
        else:
            u.set_password(pw)
            flash(f"Password updated for {u.email}.", "ok")
    elif action == "delete":
        if u.id == current_user.id:
            flash("You can't delete your own account.", "error")
        elif u.active and active_admins <= 1:
            flash("At least one active admin is required.", "error")
        else:
            db.session.delete(u)
            flash("User deleted.", "ok")
    db.session.commit()
    return redirect(url_for("admin.users"))


@admin.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        if not current_user.check_password(request.form.get("current", "")):
            flash("Your current password is incorrect.", "error")
        elif len(request.form.get("new", "")) < 10:
            flash("The new password needs at least 10 characters.", "error")
        elif request.form.get("new") != request.form.get("confirm"):
            flash("The new passwords don't match.", "error")
        else:
            current_user.set_password(request.form["new"])
            current_user.name = f("name") or current_user.name
            db.session.commit()
            flash("Password changed.", "ok")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/account.html")
