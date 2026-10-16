"""Database models for the Paragon CMS."""
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def now():
    return datetime.now(timezone.utc)


class Bilingual:
    """Mixin: pick the English or Arabic column for the current language."""

    def tr(self, field, lang):
        ar = getattr(self, f"{field}_ar", None)
        en = getattr(self, f"{field}_en", None)
        return (ar or en or "") if lang == "ar" else (en or ar or "")


# --------------------------------------------------------------------------- users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False, default="")
    password_hash = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    last_login = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.active


# --------------------------------------------------------------------------- site content
class Setting(db.Model):
    """Key/value site settings (contact details, social links, hero images ...)."""
    key = db.Column(db.String(64), primary_key=True)
    en = db.Column(db.Text, default="")
    ar = db.Column(db.Text, default="")


class Block(db.Model):
    """An editable piece of page text. Defaults are registered from the templates."""
    key = db.Column(db.String(120), primary_key=True)
    page = db.Column(db.String(40), index=True, nullable=False, default="general")
    en = db.Column(db.Text, default="")
    ar = db.Column(db.Text, default="")
    default_en = db.Column(db.Text, default="")
    default_ar = db.Column(db.Text, default="")
    position = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime(timezone=True), default=now, onupdate=now)


class Item(db.Model, Bilingual):
    """Small repeatable list items: delivery stages, values, hero chips, ticker words ..."""
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(40), index=True, nullable=False)
    icon = db.Column(db.String(40), default="")
    title_en = db.Column(db.Text, default="")
    title_ar = db.Column(db.Text, default="")
    text_en = db.Column(db.Text, default="")
    text_ar = db.Column(db.Text, default="")
    link = db.Column(db.String(255), default="")
    position = db.Column(db.Integer, default=0)


class Stat(db.Model, Bilingual):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False, default=0)
    suffix = db.Column(db.String(8), default="")
    label_en = db.Column(db.String(160), default="")
    label_ar = db.Column(db.String(160), default="")
    position = db.Column(db.Integer, default=0)


class Photo(db.Model, Bilingual):
    """An image stored as <path>.webp (large) and <path>-t.webp (thumbnail) under static/."""
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255), nullable=False)          # e.g. projects/sk-rooftop/01
    gallery = db.Column(db.String(40), index=True, default="project")  # project | workshops | library
    project_id = db.Column(db.Integer, db.ForeignKey("project.id", ondelete="CASCADE"), index=True)
    w = db.Column(db.Integer, default=1600)
    h = db.Column(db.Integer, default=1200)
    tw = db.Column(db.Integer, default=640)
    th = db.Column(db.Integer, default=480)
    alt_en = db.Column(db.String(255), default="")
    alt_ar = db.Column(db.String(255), default="")
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=now)


class Sector(db.Model, Bilingual):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(40), unique=True, nullable=False)
    name_en = db.Column(db.String(120), default="")
    name_ar = db.Column(db.String(120), default="")
    cover_id = db.Column(db.Integer, db.ForeignKey("photo.id", ondelete="SET NULL"))
    cover = db.relationship("Photo", foreign_keys=[cover_id])
    position = db.Column(db.Integer, default=0)


class ContractType(db.Model, Bilingual):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(40), unique=True, nullable=False)
    name_en = db.Column(db.String(120), default="")
    name_ar = db.Column(db.String(120), default="")
    position = db.Column(db.Integer, default=0)


project_clients = db.Table(
    "project_clients",
    db.Column("project_id", db.Integer, db.ForeignKey("project.id", ondelete="CASCADE"), primary_key=True),
    db.Column("client_id", db.Integer, db.ForeignKey("client.id", ondelete="CASCADE"), primary_key=True),
)


class Project(db.Model, Bilingual):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name_en = db.Column(db.String(200), default="")
    name_ar = db.Column(db.String(200), default="")
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.id"))
    sector = db.relationship("Sector")
    contract_id = db.Column(db.Integer, db.ForeignKey("contract_type.id"))
    contract = db.relationship("ContractType")
    location_en = db.Column(db.String(120), default="")
    location_ar = db.Column(db.String(120), default="")
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    status = db.Column(db.String(12), default="done")       # done | ongoing
    date_text_en = db.Column(db.String(120), default="")   # optional override, e.g. "October 2021 & October 2022"
    date_text_ar = db.Column(db.String(120), default="")
    auto_intro = db.Column(db.Boolean, default=True)        # prepend the generated one-line summary
    description_en = db.Column(db.Text, default="")
    description_ar = db.Column(db.Text, default="")
    seo_title_en = db.Column(db.String(200), default="")
    seo_title_ar = db.Column(db.String(200), default="")
    seo_desc_en = db.Column(db.String(320), default="")
    seo_desc_ar = db.Column(db.String(320), default="")
    cover_id = db.Column(db.Integer, db.ForeignKey("photo.id", ondelete="SET NULL", use_alter=True))
    cover = db.relationship("Photo", foreign_keys=[cover_id], post_update=True)
    photos = db.relationship("Photo", foreign_keys=[Photo.project_id], order_by="Photo.position",
                             cascade="all, delete-orphan", backref="project")
    clients = db.relationship("Client", secondary=project_clients, back_populates="projects", order_by="Client.position")
    featured = db.Column(db.Boolean, default=False)
    featured_position = db.Column(db.Integer, default=0)
    published = db.Column(db.Boolean, default=True)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=now)
    updated_at = db.Column(db.DateTime(timezone=True), default=now, onupdate=now)

    @property
    def cover_photo(self):
        return self.cover or (self.photos[0] if self.photos else None)


class Client(db.Model, Bilingual):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    name_en = db.Column(db.String(160), default="")
    name_ar = db.Column(db.String(160), default="")
    logo_path = db.Column(db.String(255), default="")      # relative to static/, with extension
    projects = db.relationship("Project", secondary=project_clients, back_populates="clients", order_by="Project.position")
    published = db.Column(db.Boolean, default=True)
    position = db.Column(db.Integer, default=0)


class Service(db.Model, Bilingual):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    icon = db.Column(db.String(40), default="pen")
    title_en = db.Column(db.String(200), default="")
    title_ar = db.Column(db.String(200), default="")
    short_en = db.Column(db.Text, default="")
    short_ar = db.Column(db.Text, default="")
    text_en = db.Column(db.Text, default="")
    text_ar = db.Column(db.Text, default="")
    features_en = db.Column(db.Text, default="")    # one per line
    features_ar = db.Column(db.Text, default="")
    photo_id = db.Column(db.Integer, db.ForeignKey("photo.id", ondelete="SET NULL"))
    photo = db.relationship("Photo")
    extra_link_url = db.Column(db.String(255), default="")
    extra_link_en = db.Column(db.String(120), default="")
    extra_link_ar = db.Column(db.String(120), default="")
    published = db.Column(db.Boolean, default=True)
    position = db.Column(db.Integer, default=0)

    def features(self, lang):
        raw = self.tr("features", lang)
        return [x.strip() for x in raw.splitlines() if x.strip()]


class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(60))
    location = db.Column(db.String(160))
    service = db.Column(db.String(200))
    details = db.Column(db.Text)
    lang = db.Column(db.String(4))
    page = db.Column(db.String(255))
    ip = db.Column(db.String(64))
    is_read = db.Column(db.Boolean, default=False, index=True)
    emailed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, index=True)
