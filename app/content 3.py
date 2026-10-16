"""Helpers shared by the public site and the admin: language, editable text blocks,
settings, image URLs/processing and project formatting."""
import html
import io
import os
import re
import uuid
from datetime import datetime
from urllib.parse import quote

from flask import current_app, g, request
from markupsafe import Markup, escape
from PIL import Image, ImageOps

from .extensions import db
from .icons import ICON, WA_SVG
from .models import Block, Client, Photo, Project, Setting

MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MONTHS_AR = ['كانون الثاني', 'شباط', 'آذار', 'نيسان', 'أيار', 'حزيران', 'تموز', 'آب', 'أيلول', 'تشرين الأول', 'تشرين الثاني', 'كانون الأول']

ICON_NAMES = sorted(k for k in ICON if k not in ('menu', 'x', 'left', 'right'))

# Settings shown in the admin (key, label, bilingual?, help)
SETTINGS_SCHEMA = [
    ("Company", [
        ("company_name", "Company name", True, ""),
        ("founded", "Year established", False, "Used wherever {founded} appears in page texts."),
        ("registration_no", "Registration number", False, ""),
        ("address", "Office address", True, ""),
        ("map_query", "Google Maps search for the map", False, "e.g. Sunrise Building, Al-Irsal Street, Ramallah"),
    ]),
    ("Contact", [
        ("phone", "Phone (as displayed)", False, "e.g. +972 59 452 2209"),
        ("whatsapp", "WhatsApp number (digits only, with country code)", False, "e.g. 972594522209"),
        ("whatsapp_message", "WhatsApp greeting message", True, "Pre-typed when visitors open a chat."),
        ("email", "Public email", False, ""),
        ("notify_email", "Send contact-form inquiries to", False, "Requires the MAIL_* server settings. Leave empty to only keep them in the admin."),
    ]),
    ("Social", [
        ("instagram", "Instagram URL", False, ""),
        ("instagram_workshops", "Workshops Instagram URL", False, ""),
        ("facebook", "Facebook URL", False, ""),
    ]),
    ("Search engines", [
        ("google_verification", "Google Search Console verification code", False, "The content=\"...\" value of the meta tag Google gives you."),
        ("org_description", "Company description for Google", False, "Shown to search engines in structured data."),
    ]),
]

HERO_SLOTS = [  # setting key, label
    ("hero_home", "Home page header"), ("hero_about", "About page header"), ("hero_services", "Services page header"),
    ("hero_projects", "Projects page header"), ("hero_clients", "Clients page header"), ("hero_workshops", "Workshops page header"),
    ("hero_contact", "Contact page header"), ("banner_workshops", "Home page workshops banner"), ("about_photo", "About page photo"),
    ("hero_404", "Not-found page header"),
]


# --------------------------------------------------------------------------- language
def lang():
    return getattr(g, "lang", "en")


def t(en, ar):
    return ar if lang() == "ar" else en


# --------------------------------------------------------------------------- settings
def settings():
    if not hasattr(g, "_settings"):
        g._settings = {s.key: s for s in Setting.query.all()}
    return g._settings


def s(key, default=""):
    """Setting in the current language (falls back to English)."""
    row = settings().get(key)
    if not row:
        return default
    return (row.ar or row.en or default) if lang() == "ar" else (row.en or default)


def s_raw(key, default=""):
    row = settings().get(key)
    return (row.en if row and row.en else default)


def set_setting(key, en="", ar=""):
    row = db.session.get(Setting, key) or Setting(key=key)
    row.en, row.ar = en, ar
    db.session.add(row)
    if hasattr(g, "_settings"):
        g._settings[key] = row


# --------------------------------------------------------------------------- editable text blocks
def _blocks():
    if not hasattr(g, "_blocks"):
        g._blocks = {b.key: b for b in Block.query.all()}
    return g._blocks


def counts():
    if not hasattr(g, "_counts"):
        g._counts = {
            "projects": Project.query.filter_by(published=True).count(),
            "clients": Client.query.filter_by(published=True).count(),
        }
    return g._counts


def fill_tokens(text):
    if not text or "{" not in text:
        return text
    c = counts()
    tokens = {"{founded}": s_raw("founded", ""), "{projects}": str(c["projects"]), "{clients}": str(c["clients"]),
              "{email}": s_raw("email", ""), "{phone}": s_raw("phone", "")}
    for k, v in tokens.items():
        text = text.replace(k, v)
    return text


def block_text(key, en, ar):
    blocks = _blocks()
    row = blocks.get(key)
    if row is None:
        # First time this text is shown: register it so it appears in the admin.
        page = key.split(".", 1)[0]
        en, ar = (en or "").replace("&amp;", "&"), (ar or "").replace("&amp;", "&")
        row = Block(key=key, page=page, en=en, ar=ar, default_en=en, default_ar=ar, position=len(blocks))
        db.session.add(row)
        blocks[key] = row
        g._blocks_dirty = True
    value = (row.ar or row.en) if lang() == "ar" else (row.en or row.ar)
    return fill_tokens(value or "")


def b(key, en, ar=""):
    """Editable rich text (may contain simple HTML such as <em>, <b>, <br>)."""
    return Markup(block_text(key, en, ar or en))


_TAG = re.compile(r"<[^>]+>")


def plain(value):
    return html.unescape(_TAG.sub("", str(value or ""))).strip()


def bt(key, en, ar=""):
    """Editable plain text, for attributes and page titles."""
    return plain(block_text(key, en, ar or en))


def commit_new_blocks(response):
    if getattr(g, "_blocks_dirty", False):
        try:
            db.session.commit()
        except Exception:  # another request registered the same key first
            db.session.rollback()
    return response


# --------------------------------------------------------------------------- URLs
def U(path=""):
    """Public URL of a page in the current language."""
    path = "" if path in ("", "index.html") else path
    return "/" + ("ar/" if lang() == "ar" else "") + path


def A(path):
    """URL of a static asset (paths are relative to app/static)."""
    path = path[len("assets/"):] if path.startswith("assets/") else path
    return "/assets/" + path


def abs_url(path="", lng=None):
    lng = lng or lang()
    path = "" if path in ("", "index.html") else path
    return current_app.config["SITE_URL"] + ("ar/" if lng == "ar" else "") + path


def img(photo, thumb=False):
    if photo is None:
        return ""
    return A(f"{photo.path}{'-t' if thumb else ''}.webp")


def img_abs(photo):
    return current_app.config["SITE_URL"] + "assets/" + photo.path + ".webp" if photo else ""


def photo_by_path(path):
    return Photo.query.filter_by(path=path).first() if path else None


def slot_photo(key):
    return photo_by_path(s_raw(key))


def icon(name):
    return Markup(ICON.get(name, ICON["check"]))


def wa_link(message=None):
    number = re.sub(r"\D", "", s_raw("whatsapp", ""))
    msg = message if message is not None else s("whatsapp_message", "")
    return f"https://wa.me/{number}" + (f"?text={quote(msg)}" if msg else "")


def tel_link(display):
    digits = re.sub(r"[^\d+]", "", display or "")
    return "tel:" + digits


def ltr(value):
    return Markup('<span dir="ltr">') + escape(value) + Markup("</span>")


# --------------------------------------------------------------------------- projects
def project_url(p):
    return f"projects/{p.slug}.html"


def project_date_text(p, lng=None):
    lng = lng or lang()
    override = p.date_text_ar if lng == "ar" else p.date_text_en
    if override:
        return override
    if not p.year:
        return ""
    months = MONTHS_AR if lng == "ar" else MONTHS_EN
    d = (months[p.month - 1] + " " if p.month else "") + str(p.year)
    if p.status == "ongoing":
        return f"متوقّع {d}" if lng == "ar" else f"Expected {d}"
    return d


def project_short_meta(p):
    loc = p.tr("location", lang())
    return " · ".join(x for x in (loc, str(p.year or "")) if x)


def project_intro(p, lng=None):
    lng = lng or lang()
    sec = p.sector.tr("name", lng) if p.sector else ""
    con = p.contract.tr("name", lng) if p.contract else ""
    loc = p.tr("location", lng)
    date = project_date_text(p, lng)
    if lng == "ar":
        loc_t = f" في {loc}" if loc else ""
        if p.status == "ongoing":
            return f"مشروع ضمن قطاع {sec}{loc_t} بعقد {con}، كان قيد التنفيذ في ملف أعمالنا لعام 2024 مع إنجاز {date}."
        return f"مشروع ضمن قطاع {sec}{loc_t}، نفّذته باراجون بعقد {con} وتم إنجازه في {date}."
    loc_t = f" in {loc}" if loc else ""
    if p.status == "ongoing":
        return f"A {sec.lower()} project{loc_t} under a {con.lower()} contract, listed as ongoing in our 2024 portfolio with completion {date.lower()}."
    return f"A {sec.lower()} project{loc_t}, delivered by Paragon under a {con.lower()} contract and completed {date}."


def project_description(p, lng=None):
    lng = lng or lang()
    extra = p.tr("description", lng)
    if p.auto_intro or not extra:
        intro = project_intro(p, lng)
        return f"{intro} {extra}".strip()
    return extra


def project_search_text(p):
    parts = [p.name_en, p.name_ar, p.location_en, p.location_ar, str(p.year or ""), p.description_en, p.description_ar,
             p.slug.replace("-", " "), "ongoing قيد التنفيذ" if p.status == "ongoing" else "completed منجز"]
    if p.sector:
        parts += [p.sector.name_en, p.sector.name_ar]
    if p.contract:
        parts += [p.contract.name_en, p.contract.name_ar]
    if p.month:
        parts += [MONTHS_EN[p.month - 1], MONTHS_AR[p.month - 1]]
    for c in p.clients:
        parts += [c.name_en, c.name_ar]
    return " ".join(x for x in parts if x)


def published_projects():
    return Project.query.filter_by(published=True).order_by(Project.position, Project.id).all()


# --------------------------------------------------------------------------- images
def static_path(*parts):
    return os.path.join(current_app.static_folder, *parts)


def process_image(file_storage, folder, max_size=1600, thumb_size=640):
    """Save an uploaded image as WebP (large + thumbnail). Returns a dict for Photo()."""
    raw = file_storage.read()
    im = Image.open(io.BytesIO(raw))
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
    sub = os.path.join(folder, datetime.now().strftime("%Y%m"))
    os.makedirs(static_path(sub), exist_ok=True)
    name = uuid.uuid4().hex[:12]
    rel = f"{sub}/{name}".replace(os.sep, "/")
    full = im.copy(); full.thumbnail((max_size, max_size), Image.LANCZOS)
    full.save(static_path(rel + ".webp"), "WEBP", quality=80, method=6)
    th = im.copy(); th.thumbnail((thumb_size, thumb_size), Image.LANCZOS)
    th.save(static_path(rel + "-t.webp"), "WEBP", quality=74, method=6)
    return dict(path=rel, w=full.width, h=full.height, tw=th.width, th=th.height)


def process_logo(file_storage, key):
    raw = file_storage.read()
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw)))
    im = im.convert("RGBA")
    im.thumbnail((480, 240), Image.LANCZOS)
    os.makedirs(static_path("uploads", "clients"), exist_ok=True)
    rel = f"uploads/clients/{key}-{uuid.uuid4().hex[:6]}.webp"
    im.save(static_path(rel), "WEBP", quality=90)
    return rel


def make_og(photo, name):
    """1200x630 JPEG used when a page is shared on WhatsApp / Facebook."""
    if not photo:
        return
    try:
        im = Image.open(static_path(photo.path + ".webp")).convert("RGB")
        os.makedirs(static_path("og"), exist_ok=True)
        ImageOps.fit(im, (1200, 630), Image.LANCZOS).save(static_path("og", f"{name}.jpg"), quality=82, optimize=True, progressive=True)
    except (FileNotFoundError, OSError):
        pass


def og_url(name, fallback_photo=None):
    if os.path.exists(static_path("og", f"{name}.jpg")):
        return current_app.config["SITE_URL"] + f"assets/og/{name}.jpg"
    return img_abs(fallback_photo) if fallback_photo else current_app.config["SITE_URL"] + "assets/og/home.jpg"


def delete_photo_files(photo):
    for suffix in (".webp", "-t.webp"):
        try:
            os.remove(static_path(photo.path + suffix))
        except OSError:
            pass


def slugify(value):
    value = re.sub(r"[^\w\s-]", "", (value or "").lower()).strip()
    value = re.sub(r"[\s_-]+", "-", value)
    value = re.sub(r"[^a-z0-9-]", "", value)
    return value.strip("-") or uuid.uuid4().hex[:8]


def template_globals():
    return dict(t=t, b=b, bt=bt, s=s, s_raw=s_raw, U=U, A=A, abs_url=abs_url, img=img, img_abs=img_abs, icon=icon,
                WA_SVG=Markup(WA_SVG), wa_link=wa_link, tel_link=tel_link, ltr=ltr, plain=plain, lang=lang,
                project_url=project_url, project_date_text=project_date_text, project_short_meta=project_short_meta,
                project_description=project_description, project_search_text=project_search_text, slot_photo=slot_photo,
                counts=counts, fill_tokens=fill_tokens, request=request)
