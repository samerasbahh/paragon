"""Public website routes (English at /, Arabic at /ar/), sitemap, robots and the contact API."""
import time
from collections import defaultdict, deque
from urllib.parse import urlparse

from flask import Blueprint, abort, current_app, g, jsonify, redirect, render_template, request, url_for, Response

from .content import (U, abs_url, img_abs, lang, project_url, published_projects, s_raw)
from .extensions import csrf, db
from .mailer import send_inquiry_email
from .models import Client, ContractType, Inquiry, Item, Photo, Project, Sector, Service, Stat

public = Blueprint("public", __name__)
site = Blueprint("site", __name__)


@public.before_request
def set_lang():
    g.lang = "ar" if request.blueprint == "public_ar" else "en"


def _common():
    sectors = Sector.query.order_by(Sector.position).all()
    return dict(
        sectors=sectors,
        stats=Stat.query.order_by(Stat.position).all(),
        services=Service.query.filter_by(published=True).order_by(Service.position).all(),
        clients=Client.query.filter_by(published=True).order_by(Client.position).all(),
    )


def items(group):
    return Item.query.filter_by(group=group).order_by(Item.position, Item.id).all()


def render(template, cur, **ctx):
    data = _common()
    data.update(ctx)
    return render_template(template, cur=cur, items=items, **data)


# --------------------------------------------------------------------------- pages
@public.route("/")
def home():
    projects = published_projects()
    featured = sorted([p for p in projects if p.featured], key=lambda p: (p.featured_position, p.position))
    return render("public/home.html", "index.html", projects=projects, featured=featured)


@public.route("/index.html")
def index_html():
    return redirect(U(""), 301)


@public.route("/about.html")
def about():
    return render("public/about.html", "about.html")


@public.route("/services.html")
def services_page():
    return render("public/services.html", "services.html", projects=published_projects())


@public.route("/projects.html")
def projects():
    return render("public/projects.html", "projects.html", projects=published_projects(),
                  contracts=ContractType.query.order_by(ContractType.position).all())


@public.route("/projects/<slug>.html")
def project(slug):
    p = Project.query.filter_by(slug=slug).first()
    if p is None or (not p.published and not _is_admin()):
        abort(404)
    projects = published_projects()
    others = [q for q in projects if q.id != p.id]
    if p in projects:
        i = projects.index(p)
        prev_p, next_p = projects[i - 1], projects[(i + 1) % len(projects)]
    else:
        prev_p = next_p = others[0] if others else p
    related = [q for q in others if q.sector_id == p.sector_id][:3]
    related += [q for q in others if q not in related][:3 - len(related)]
    return render("public/project.html", project_url(p), p=p, prev_p=prev_p, next_p=next_p, related=related,
                  projects=projects)


@public.route("/clients.html")
def clients():
    return render("public/clients.html", "clients.html", projects=published_projects())


@public.route("/workshops.html")
def workshops():
    photos = Photo.query.filter_by(gallery="workshops").order_by(Photo.position).all()
    wm = [p for p in published_projects() if p.contract and p.contract.key == "wm"]
    return render("public/workshops.html", "workshops.html", photos=photos, wm_projects=wm)


@public.route("/contact.html")
def contact():
    return render("public/contact.html", "contact.html")


# Addresses used by the previous website
@public.route("/services-nueva.html")
@public.route("/services-nueva")
def old_services():
    return redirect(U("services.html"), 301)


@public.route("/project-gallery-page-nueva.html")
@public.route("/project-gallery-page-nueva")
def old_projects():
    return redirect(U("projects.html"), 301)


@public.route("/get-a-quote-nueva.html")
@public.route("/get-a-quote-nueva")
def old_contact():
    return redirect(U("contact.html"), 301)


def _is_admin():
    from flask_login import current_user
    return current_user.is_authenticated


# --------------------------------------------------------------------------- sitemap / robots
@site.route("/sitemap.xml")
def sitemap():
    pages = ["index.html", "about.html", "services.html", "projects.html", "clients.html", "workshops.html", "contact.html"]
    projects = published_projects()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" '
           'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']

    def entry(path, lng, pri, imgs=""):
        return (f'<url><loc>{abs_url(path, lng)}</loc>'
                f'<xhtml:link rel="alternate" hreflang="en" href="{abs_url(path, "en")}"/>'
                f'<xhtml:link rel="alternate" hreflang="ar" href="{abs_url(path, "ar")}"/>'
                f'<xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(path, "en")}"/>'
                f'<priority>{pri}</priority>{imgs}</url>')

    for pg in pages:
        pri = "1.0" if pg == "index.html" else ("0.9" if pg in ("projects.html", "services.html") else "0.7")
        for lng in ("en", "ar"):
            out.append(entry(pg, lng, pri))
    for p in projects:
        imgs = "".join(f"<image:image><image:loc>{img_abs(ph)}</image:loc></image:image>" for ph in p.photos)
        for lng in ("en", "ar"):
            out.append(entry(project_url(p), lng, "0.7", imgs))
    out.append("</urlset>")
    return Response("\n".join(out), mimetype="application/xml")


@site.route("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {current_app.config['SITE_URL']}sitemap.xml\n"
    return Response(body, mimetype="text/plain")


# --------------------------------------------------------------------------- contact form API
_hits = defaultdict(deque)


def _rate_limited(ip, limit=5, window=600):
    q = _hits[ip]
    now = time.time()
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= limit:
        return True
    q.append(now)
    return False


def _same_origin():
    src = request.headers.get("Origin") or request.headers.get("Referer") or ""
    if not src:
        return True
    host = urlparse(src).netloc
    return host == request.host or host == urlparse(current_app.config["SITE_URL"]).netloc


@site.route("/api/inquiry", methods=["POST"])
@csrf.exempt  # public form: protected by same-origin check, honeypot and rate limiting
def inquiry():
    data = request.get_json(silent=True) or request.form
    if not _same_origin():
        return jsonify(success=False, message="Bad origin"), 400
    if (data.get("_honey") or "").strip():
        return jsonify(success=True)  # silently drop bots
    ip = (request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0]).strip()
    if _rate_limited(ip):
        return jsonify(success=False, message="Too many requests"), 429
    name = (data.get("name") or "").strip()[:160]
    email = (data.get("email") or "").strip()[:255]
    if not name or "@" not in email:
        return jsonify(success=False, message="Name and email are required"), 400
    inq = Inquiry(name=name, email=email, phone=(data.get("phone") or "").strip()[:60],
                  location=(data.get("location") or "").strip()[:160], service=(data.get("service") or "").strip()[:200],
                  details=(data.get("details") or "").strip()[:5000], lang=(data.get("lang") or "en")[:4],
                  page=(request.headers.get("Referer") or "")[:255], ip=ip[:64])
    db.session.add(inq)
    db.session.commit()
    inq.emailed = send_inquiry_email(inq)
    db.session.commit()
    return jsonify(success=True)
