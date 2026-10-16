"""Command-line tools:  flask --app wsgi <command>

  init-db        create the database tables
  seed           import the current website content (projects, photos, clients, services, texts ...)
  create-admin   add an admin user (prompts for the password)
  prime-texts    render every page once so all editable texts appear in the admin
"""
import importlib.util
import json
import os

import click

from .config import BASE_DIR
from .extensions import db
from .models import (Block, Client, ContractType, Item, Photo, Project, Sector, Service, Setting, Stat, User)

LEGACY = os.path.join(BASE_DIR, "legacy")


def _load(name):
    spec = importlib.util.spec_from_file_location(f"legacy_{name}", os.path.join(LEGACY, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Create database tables."""
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--name", prompt=True, default="")
    @click.password_option()
    def create_admin(email, name, password):
        """Create an admin user."""
        if len(password) < 10:
            raise click.ClickException("Use a password of at least 10 characters.")
        db.create_all()
        if User.query.filter(db.func.lower(User.email) == email.lower()).first():
            raise click.ClickException("That email already has an account.")
        u = User(email=email.lower().strip(), name=name.strip())
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        click.echo(f"Admin {u.email} created.")

    @app.cli.command("seed")
    @click.option("--force", is_flag=True, help="Delete existing content first.")
    def seed(force):
        """Import the current website content into the database."""
        db.create_all()
        if Project.query.count() and not force:
            raise click.ClickException("The database already has content. Use --force to replace it.")
        if force:
            for model in (Block, Item, Stat, Service, Client, Project, Photo, Sector, ContractType, Setting):
                if model is Project:
                    for p in Project.query.all():
                        p.cover_id = None
                    db.session.flush()
                model.query.delete()
            db.session.execute(db.text("DELETE FROM project_clients"))
            db.session.commit()
        seed_content()
        click.echo("Content imported.")
        prime(app)
        click.echo(f"{Block.query.count()} editable texts registered.")

    @app.cli.command("prime-texts")
    def prime_texts():
        """Render every page so all texts are listed in the admin."""
        prime(app)
        click.echo(f"{Block.query.count()} editable texts registered.")


def prime(app):
    from .content import project_url
    client = app.test_client()
    pages = ["", "about.html", "services.html", "projects.html", "clients.html", "workshops.html", "contact.html", "no-such-page.html"]
    first = Project.query.filter_by(published=True).order_by(Project.position).first()
    if first:
        pages.append(project_url(first))
    for prefix in ("/", "/ar/"):
        for pg in pages:
            client.get(prefix + pg)


def seed_content():
    pr = _load("projects")
    ct = _load("content")
    photos = json.load(open(os.path.join(LEGACY, "photos.json")))

    # ---- settings
    settings = {
        "company_name": ("Paragon Engineering Company", "شركة باراجون للهندسة"),
        "founded": (str(ct.FOUNDED), ""),
        "registration_no": ("562583153", ""),
        "address": ("P.O. Box 53, Office 402, Sunrise Building, Al-Irsal Street, Ramallah, Palestine",
                    "ص.ب 53، مكتب 402، عمارة صن رايز، شارع الإرسال، رام الله، فلسطين"),
        "map_query": ("Sunrise Building, Al-Irsal Street, Ramallah", ""),
        "phone": ("+972 59 452 2209", ""),
        "whatsapp": ("972594522209", ""),
        "whatsapp_message": ("Hello Paragon, I'd like to ask about a project.", "مرحباً باراجون، أود الاستفسار عن مشروع."),
        "email": ("info@paragoncmc.com", ""),
        "notify_email": ("info@paragoncmc.com", ""),
        "instagram": ("https://www.instagram.com/paragon_cmc/", ""),
        "instagram_workshops": ("https://www.instagram.com/paragonworkshops/", ""),
        "facebook": ("https://www.facebook.com/paragoncmc", ""),
        "org_description": ("Multidisciplinary contracting company in Ramallah, Palestine, specializing in interior fit-out, turnkey solutions, and landscape design and execution.", ""),
        "google_verification": ("", ""),
        "hero_home": ("projects/hyundai-mopar-visitor-center/01", ""),
        "hero_about": ("projects/sk-rooftop/05", ""),
        "hero_services": ("projects/asharq-news-ramallah/04", ""),
        "hero_projects": ("projects/french-german-cultural-center/03", ""),
        "hero_clients": ("projects/french-german-cultural-center/03", ""),
        "hero_workshops": ("projects/_workshops/07", ""),
        "hero_contact": ("projects/la-vanda-bridal-store/01", ""),
        "banner_workshops": ("projects/_workshops/07", ""),
        "about_photo": ("projects/sd-villa/04", ""),
        "hero_404": ("projects/locanda-farah-boutique-hotel/03", ""),
    }
    for k, (en, ar) in settings.items():
        db.session.add(Setting(key=k, en=en, ar=ar))

    # ---- photos
    by_path = {}
    for slug, rows in photos.items():
        for i, it in enumerate(rows):
            ph = Photo(path=f"projects/{slug}/{it['f']}", gallery="workshops" if slug == "_workshops" else "project",
                       w=it["w"], h=it["h"], tw=it["tw"], th=it["th"], position=i + 1)
            db.session.add(ph)
            by_path[ph.path] = ph
    db.session.flush()

    # ---- sectors & contract types
    covers = {'hospitality': 'lemon-restaurant/03', 'commercial': 'la-vanda-bridal-store/01', 'healthcare': 'dr-adel-asfour-clinic/05',
              'workspace': 'qcom-ramallah/06', 'broadcasting': 'asharq-news-ramallah/04', 'residential': 'sk-rooftop/04'}
    sectors = {}
    for i, (k, en, ar) in enumerate(pr.SECTORS):
        cov = by_path.get("projects/" + covers.get(k, ""))
        sectors[k] = Sector(key=k, name_en=en, name_ar=ar, position=i + 1, cover_id=cov.id if cov else None)
        db.session.add(sectors[k])
    contracts = {}
    for i, (k, (en, ar)) in enumerate(pr.CONTRACTS.items()):
        contracts[k] = ContractType(key=k, name_en=en, name_ar=ar, position=i + 1)
        db.session.add(contracts[k])
    db.session.flush()

    # ---- projects
    projects = {}
    for i, row in enumerate(pr.P):
        slug, sector, en, ar, loc_en, loc_ar, contract, (year, month), status, cover, x_en, x_ar = row
        p = Project(slug=slug, name_en=en, name_ar=ar, sector_id=sectors[sector].id, contract_id=contracts[contract].id,
                    location_en=loc_en, location_ar=loc_ar, year=year, month=month, status=status,
                    description_en=x_en, description_ar=x_ar, auto_intro=True, position=i + 1, published=True)
        if slug == "palestine-cinema-days-festival":
            p.date_text_en, p.date_text_ar = "October 2021 & October 2022", "تشرين الأول 2021 وتشرين الأول 2022"
        if slug in pr.FEATURED:
            p.featured, p.featured_position = True, pr.FEATURED.index(slug) + 1
        db.session.add(p)
        db.session.flush()
        for ph in Photo.query.filter(Photo.path.like(f"projects/{slug}/%")).all():
            ph.project_id = p.id
        cov = by_path.get(f"projects/{slug}/{cover}")
        p.cover_id = cov.id if cov else None
        projects[slug] = p

    # ---- clients
    for i, (key, en, ar, slugs) in enumerate(pr.CLIENTS):
        c = Client(key=key, name_en=en, name_ar=ar, logo_path=f"clients/{key}.webp", position=i + 1, published=True)
        c.projects = [projects[s] for s in slugs if s in projects]
        db.session.add(c)

    # ---- services
    for i, sv in enumerate(ct.SERVICES):
        slug, f = sv["img"]
        ph = by_path.get(f"projects/{slug}/{f}")
        row = Service(slug=sv["id"], icon=sv["icon"], title_en=sv["title"][0], title_ar=sv["title"][1],
                      short_en=sv["short"][0], short_ar=sv["short"][1], text_en=sv["text"][0], text_ar=sv["text"][1],
                      features_en="\n".join(x[0] for x in sv["feats"]), features_ar="\n".join(x[1] for x in sv["feats"]),
                      photo_id=ph.id if ph else None, position=i + 1, published=True)
        if sv["id"] == "joinery":
            row.extra_link_url, row.extra_link_en, row.extra_link_ar = "workshops.html", "Visit our workshops", "تعرّف على ورشنا"
        db.session.add(row)

    # ---- numbers
    for i, (n, suf, en, ar) in enumerate([(ct.FOUNDED, "", "Established", "سنة التأسيس"), (20, "+", "Years of construction experience", "سنة خبرة في البناء"),
                                          (60, "+", "Team members", "عضواً في الفريق"), (50, "+", "Project handovers", "مشروعاً تم تسليمه")]):
        db.session.add(Stat(number=n, suffix=suf, label_en=en, label_ar=ar, position=i + 1))

    # ---- small lists
    def add_items(group, rows):
        for i, r in enumerate(rows):
            icon, ten, tar = r[0], r[1], r[2]
            xen, xar = (r[3], r[4]) if len(r) > 4 else ("", "")
            link = r[5] if len(r) > 5 else ""
            db.session.add(Item(group=group, icon=icon, title_en=ten, title_ar=tar, text_en=xen, text_ar=xar, link=link, position=i + 1))

    add_items("stages", [(ic, en, ar) for ic, en, ar in ct.STAGES])
    add_items("hero_chips", [("check-circle", "Free, flexible estimates", "تقديرات تكلفة مجانية ومرنة"),
                             ("hammer", "Bespoke joinery workshops", "ورش نجارة حسب الطلب"),
                             ("shield", "Guaranteed & warrantied works", "أعمال مضمونة وبكفالة")])
    add_items("ticker", [("", "Interior fit-out", "تجهيزات داخلية"), ("", "Turnkey solutions", "حلول تسليم المفتاح"),
                         ("", "Landscape & pools", "لاندسكيب وبرك سباحة"), ("", "Bespoke joinery", "نجارة حسب الطلب"),
                         ("", "Renovation", "تجديد"), ("", "Project management", "إدارة مشاريع"),
                         ("", "Facilities management", "إدارة المرافق"), ("", "Value engineering", "هندسة القيمة")])
    add_items("about_values", [
        ("award", "Professionalism", "المهنية", "Technical expertise and skilled craftsmanship, applied with discipline on every site.", "خبرة فنية وحرفية ماهرة تُطبَّق بانضباط في كل موقع."),
        ("shield", "Accountability", "المسؤولية", "Meticulous planning, effective coordination and rigorous quality control.", "تخطيط دقيق وتنسيق فعّال ورقابة صارمة على الجودة."),
        ("user", "Long-term relationships", "علاقات طويلة الأمد", "Enduring value through reliable execution and consistently high-quality results.", "قيمة مستدامة من خلال تنفيذ موثوق ونتائج عالية الجودة باستمرار.")])
    add_items("about_sectors", [("", "Residential", "سكني", "", "", "residential"), ("", "Commercial", "تجاري", "", "", "commercial"),
                                ("", "Hospitality", "الضيافة", "", "", "hospitality"), ("", "Healthcare", "الرعاية الصحية", "", "", "healthcare"),
                                ("", "Workplace", "مساحات العمل", "", "", "workspace"), ("", "Food & beverage", "المطاعم والمقاهي", "", "", "hospitality")])
    add_items("ws_why", [
        ("ruler", "Expert engineers & in-house operations", "مهندسون خبراء وعمليات داخلية", "Our engineers translate your vision into detailed shop drawings. Everything from joinery to painting and metalwork is done in-house, for complete quality control.", "يحوّل مهندسونا رؤيتك إلى مخططات تنفيذية مفصّلة. وتتم جميع العمليات، من النجارة إلى الدهان وأعمال المعادن، داخل ورشنا لضمان رقابة كاملة على الجودة."),
        ("award", "Unwavering commitment to quality", "التزام ثابت بالجودة", "Precision and attention to detail come first. Rigorous product control and stage inspections guarantee quality from raw material to final finish.", "الدقة والاهتمام بالتفاصيل أولاً. رقابة صارمة على المنتج وفحوصات في كل مرحلة تضمن الجودة من المادة الخام حتى اللمسة الأخيرة."),
        ("clock", "Time management", "إدارة الوقت", "We understand deadlines. Our time control keeps every piece within the agreed timeframe.", "ندرك أهمية المواعيد. التزامنا بإدارة الوقت يضمن تسليم كل قطعة ضمن الإطار الزمني المتفق عليه."),
        ("pen", "Bespoke & customised creations", "تصاميم حسب الطلب", "No one-size-fits-all: we specialise in furniture tailored to your needs and preferences.", "لا نؤمن بالحلول الجاهزة: نتخصص في صناعة أثاث مصمّم خصيصاً لاحتياجاتك وذوقك."),
        ("shield", "Safety first", "السلامة أولاً", "Your safety and our team’s come first. We follow strict safety standards throughout production.", "سلامتك وسلامة فريقنا أولوية. نلتزم بأشد معايير السلامة طوال عملية الإنتاج.")])
    add_items("contact_checks", [
        ("check-circle", "<b>Free estimates</b>, flexible according to materials and scheduling.", "<b>تقديرات تكلفة مجانية</b> ومرنة حسب المواد والجدول الزمني."),
        ("shield", "All works guaranteed and warrantied.", "جميع الأعمال مضمونة وبكفالة."),
        ("hardhat", "A 60+ strong team with in-house wood and metal workshops.", "فريق يضم أكثر من 60 عضواً مع ورش خشب ومعادن خاصة بنا.")])

    # ---- long About / Vision texts (shared by the Home and About pages)
    def tok(s):
        return s.replace(str(ct.FOUNDED), "{founded}")
    for i, (en, ar) in enumerate(ct.ABOUT, 1):
        db.session.add(Block(key=f"about.p{i}", page="about", en=tok(en), ar=tok(ar), default_en=tok(en), default_ar=tok(ar), position=100 + i))
    for i, (en, ar) in enumerate(ct.VISION, 1):
        db.session.add(Block(key=f"about.vision{i}", page="about", en=en, ar=ar, default_en=en, default_ar=ar, position=110 + i))
    db.session.commit()
