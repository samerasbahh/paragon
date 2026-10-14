#!/usr/bin/env python3
"""Generates the Paragon website in English (root) and Arabic (ar/).

    python3 build.py

Edit text here; project facts live in data/projects.py, photo lists in data/photos.json.
Every visible string is written as t("English", "العربية").
"""
import os, sys, json, html
from urllib.parse import quote
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from icons import ICON, WA_SVG
from data.projects import SECTORS, CONTRACTS, MONTHS_EN, MONTHS_AR, P, FEATURED, CLIENTS
from data.content import FOUNDED, ABOUT, STAGES, VISION, SERVICES

ROOT = HERE
SITE = "https://www.paragoncmc.com/"          # live address, used for Google (canonical links, sitemap)
LANG = 'en'                                   # set per build pass
CUR = 'index.html'                            # current page, relative to the language root
ABS = False                                   # 404 page: use root-absolute links (it can be shown at any address)

def t(en, ar): return ar if LANG == 'ar' else en
def ltr(s): return f'<span dir="ltr">{s}</span>'
def esc(s): return html.escape(s, quote=True)
def _depth(): return CUR.count('/')
def U(path):                                  # link to another page in the same language
    if ABS: return '/' + ('ar/' if LANG == 'ar' else '') + path
    return '../' * _depth() + path
def A(path):                                  # link to a shared asset
    if ABS: return '/' + path
    return '../' * (_depth() + (1 if LANG == 'ar' else 0)) + path
def abs_url(path, lang=None):
    lang = lang or LANG
    path = '' if path == 'index.html' else path
    return SITE + ('ar/' if lang == 'ar' else '') + path

# ---------------------------------------------------------------- company facts
PHONE = "+972 59 452 2209"; PHONE_TEL = "tel:+972594522209"
PHONE_OFF = "+970 2 295 4967"; PHONE_OFF_TEL = "tel:+97022954967"
EMAIL = "info@paragoncmc.com"
WA_NUMBER = "972594522209"
IG = "https://www.instagram.com/paragon_cmc/"
IG_WORKSHOPS = "https://www.instagram.com/paragonworkshops/"
FB = "https://www.facebook.com/paragoncmc"

def wa():
    msg = t("Hello Paragon, I'd like to ask about a project.", "مرحباً باراجون، أود الاستفسار عن مشروع.")
    return f"https://wa.me/{WA_NUMBER}?text={quote(msg)}"

def address():
    return t("P.O. Box 53, Office 402, Sunrise Building, Al-Irsal Street, Ramallah, Palestine",
             "ص.ب 53، مكتب 402، عمارة صن رايز، شارع الإرسال، رام الله، فلسطين")

def nav():
    return [("index.html", t("Home", "الرئيسية")), ("about.html", t("About", "من نحن")), ("services.html", t("Services", "الخدمات")),
            ("projects.html", t("Projects", "المشاريع")), ("clients.html", t("Clients", "عملاؤنا")),
            ("workshops.html", t("Workshops", "الورش")),
            ("contact.html", t("Contact", "اتصل بنا"))]

# ---------------------------------------------------------------- photos & projects
PHOTOS = json.load(open(os.path.join(ROOT, 'data', 'photos.json')))
def ph(slug, f, thumb=False): return A(f"assets/projects/{slug}/{f}{'-t' if thumb else ''}.webp")
def ph_abs(slug, f): return f"{SITE}assets/projects/{slug}/{f}.webp"
def ph_dims(slug, f, thumb=False):
    for it in PHOTOS[slug]:
        if it['f'] == f: return (it['tw'], it['th']) if thumb else (it['w'], it['h'])
    return (1600, 1200)

HERO = {'home': ('hyundai-mopar-visitor-center', '01'), 'about': ('sk-rooftop', '05'), 'services': ('asharq-news-ramallah', '04'),
        'projects': ('french-german-cultural-center', '03'), 'workshops': ('_workshops', '07'),
        'contact': ('la-vanda-bridal-store', '01'), 'banner': ('locanda-farah-boutique-hotel', '03')}
def hero_bg(key): s, f = HERO[key]; return ph(s, f)
def og(name): return f"{SITE}assets/og/{name}.jpg"     # 1200x630 JPEG share images

SECTOR = {k: (en, ar) for k, en, ar in SECTORS}
def sector_name(k): en, ar = SECTOR[k]; return t(en, ar)

class Project:
    def __init__(self, row):
        (self.slug, self.sector, self.en, self.ar, self.loc_en, self.loc_ar, self.contract, self.date,
         self.status, self.cover, self.x_en, self.x_ar) = row
        self.photos = PHOTOS.get(self.slug, [])
    @property
    def name(self): return t(self.en, self.ar)
    @property
    def loc(self): return t(self.loc_en, self.loc_ar)
    @property
    def contract_name(self): return t(*CONTRACTS[self.contract])
    @property
    def url(self): return f"projects/{self.slug}.html"
    def date_text(self):
        y, m = self.date
        if self.slug == 'palestine-cinema-days-festival':
            return t('October 2021 & October 2022', 'تشرين الأول 2021 وتشرين الأول 2022')
        d = (t(MONTHS_EN[m - 1], MONTHS_AR[m - 1]) + ' ' if m else '') + str(y)
        return t(f'Expected {d}', f'متوقّع {d}') if self.status == 'ongoing' else d
    def short_meta(self):
        bits = [x for x in (self.loc, str(self.date[0])) if x]
        return ' · '.join(bits)
    def description(self):
        sec_en, sec_ar = SECTOR[self.sector]; con_en, con_ar = CONTRACTS[self.contract]
        loc_en = f' in {self.loc_en}' if self.loc_en else ''; loc_ar = f' في {self.loc_ar}' if self.loc_ar else ''
        if self.status == 'ongoing':
            base = t(f'A {sec_en.lower()} project{loc_en} under a {con_en.lower()} contract, listed as ongoing in our 2024 portfolio with completion {self.date_text().lower()}.',
                     f'مشروع ضمن قطاع {sec_ar}{loc_ar} بعقد {con_ar}، كان قيد التنفيذ في ملف أعمالنا لعام 2024 مع إنجاز {self.date_text()}.')
        else:
            base = t(f'A {sec_en.lower()} project{loc_en}, delivered by Paragon under a {con_en.lower()} contract and completed {self.date_text()}.',
                     f'مشروع ضمن قطاع {sec_ar}{loc_ar}، نفّذته باراجون بعقد {con_ar} وتم إنجازه في {self.date_text()}.')
        extra = t(self.x_en, self.x_ar)
        return (base + ' ' + extra) if extra else base
    def search_text(self):
        y, m = self.date
        parts = [self.en, self.ar, *SECTOR[self.sector], *CONTRACTS[self.contract], self.loc_en, self.loc_ar, str(y),
                 MONTHS_EN[m - 1] if m else '', MONTHS_AR[m - 1] if m else '', self.x_en, self.x_ar,
                 'ongoing قيد التنفيذ' if self.status == 'ongoing' else 'completed منجز', self.slug.replace('-', ' ')]
        return ' '.join(p for p in parts if p)

PROJECTS = [Project(r) for r in P]
BY_SLUG = {p.slug: p for p in PROJECTS}

# ---------------------------------------------------------------- page chrome
def jsonld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'

def org_ld():
    return {
        "@context": "https://schema.org", "@type": "GeneralContractor", "@id": SITE + "#org",
        "name": "Paragon Engineering Company", "alternateName": ["Paragon", "باراجون للهندسة", "شركة باراجون للهندسة"],
        "url": SITE, "logo": SITE + "assets/logo/paragon-logo.png", "image": SITE + "assets/projects/hyundai-mopar-visitor-center/01.webp",
        "description": "Multidisciplinary contracting company in Ramallah, Palestine, specializing in interior fit-out, turnkey solutions, and landscape design and execution.",
        "telephone": "+972594522209", "email": EMAIL, "foundingDate": str(FOUNDED),
        "address": {"@type": "PostalAddress", "streetAddress": "Office 402, Sunrise Building, Al-Irsal Street", "postOfficeBoxNumber": "53",
                    "addressLocality": "Ramallah", "addressCountry": "PS"},
        "areaServed": [{"@type": "Place", "name": "Ramallah"}, {"@type": "Place", "name": "Jerusalem"}, {"@type": "Country", "name": "Palestine"}],
        "numberOfEmployees": {"@type": "QuantitativeValue", "minValue": 60},
        "knowsAbout": ["Interior fit-out", "Turnkey projects", "Design and build", "Landscape design", "Landscape construction", "Swimming pools", "Bespoke joinery", "Renovation",
                       "Project management", "Facilities management", "Value engineering", "Property renovation"],
        "sameAs": [FB, IG, IG_WORKSHOPS],
        "contactPoint": {"@type": "ContactPoint", "telephone": "+972594522209", "contactType": "customer service", "availableLanguage": ["English", "Arabic"]},
    }

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(u)} for i, (n, u) in enumerate(items)]}

def head(title, desc, image_abs, ld=()):
    other_lang = 'ar' if LANG == 'en' else 'en'
    return f'''<!doctype html>
<html lang="{LANG}" dir="{'rtl' if LANG == 'ar' else 'ltr'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{abs_url(CUR)}">
<link rel="alternate" hreflang="en" href="{abs_url(CUR, 'en')}">
<link rel="alternate" hreflang="ar" href="{abs_url(CUR, 'ar')}">
<link rel="alternate" hreflang="x-default" href="{abs_url(CUR, 'en')}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{t('Paragon Engineering', 'باراجون للهندسة')}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{abs_url(CUR)}">
<meta property="og:image" content="{image_abs}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{'ar_PS' if LANG == 'ar' else 'en_US'}">
<meta property="og:locale:alternate" content="{'en_US' if LANG == 'ar' else 'ar_PS'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0F2034">
<link rel="icon" type="image/png" sizes="512x512" href="{A('assets/logo/paragon-icon.png')}">
<link rel="icon" type="image/png" sizes="32x32" href="{A('assets/logo/favicon-32.png')}">
<link rel="apple-touch-icon" href="{A('assets/logo/apple-touch-icon.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{A('assets/style.css')}">
{"".join(jsonld(x) for x in ld)}
</head>
<body>
<a class="skip" href="#main">{t('Skip to content', 'انتقل إلى المحتوى')}</a>
'''

def header(active):
    other = ('../' * _depth()) + ('ar/' + CUR if LANG == 'en' else '../' + CUR)
    if ABS: other = '/ar/' if LANG == 'en' else '/'
    other_label = t('العربية', 'English'); other_lang = t('ar', 'en')
    links = "".join(f'<li><a href="{U(h)}"{" class=\"active\" aria-current=\"page\"" if h == active else ""}>{x}</a></li>' for h, x in nav())
    mlinks = "".join(f'<a href="{U(h)}">{x}</a>' for h, x in nav())
    return f'''<header class="site-header">
  <div class="container nav">
    <a class="brand" href="{U('index.html')}" aria-label="{t('Paragon Engineering — home', 'باراجون للهندسة — الرئيسية')}"><img src="{A('assets/logo/paragon-logo.png')}" alt="Paragon — A Model of Excellence" width="218" height="50"></a>
    <nav aria-label="{t('Main', 'القائمة الرئيسية')}"><ul class="nav-links">{links}</ul></nav>
    <div class="nav-cta">
      <a class="lang-switch" href="{other}" hreflang="{other_lang}" lang="{other_lang}">{ICON['globe']}<span>{other_label}</span></a>
      <a class="btn btn-primary btn-sm" href="{U('contact.html')}#inquiry"><span class="btn-icon">{ICON['calendar']}</span>{t('Schedule Appointment', 'احجز موعداً')}</a>
      <button class="menu-toggle" aria-label="{t('Open menu', 'فتح القائمة')}" aria-expanded="false">{ICON['menu']}</button>
    </div>
  </div>
  <div class="mobile-menu">{mlinks}<a href="{other}" lang="{other_lang}" class="m-lang">{ICON['globe']}{other_label}</a><a class="btn btn-primary" href="{U('contact.html')}#inquiry">{t('Schedule Appointment', 'احجز موعداً')}</a></div>
</header>
<main id="main">
'''

def footer():
    return f'''</main>
<footer class="site-footer">
  <div class="container foot-grid">
    <div>
      <a class="foot-logo" href="{U('index.html')}"><img src="{A('assets/logo/paragon-logo-light.png')}" alt="Paragon — A Model of Excellence" width="279" height="64" loading="lazy"></a>
      <p class="foot-about">{t(f'Multidisciplinary contracting company: interior fit-out, turnkey solutions and landscape design &amp; execution. Established {FOUNDED} in Ramallah, Palestine.',
                              f'شركة مقاولات متعددة التخصصات: تجهيزات داخلية وحلول تسليم مفتاح وتصميم وتنفيذ اللاندسكيب. تأسست عام {FOUNDED} في رام الله، فلسطين.')}</p>
      <div class="socials">
        <a href="{IG}" target="_blank" rel="noopener" aria-label="Instagram">{ICON['instagram']}</a>
        <a href="{FB}" target="_blank" rel="noopener" aria-label="Facebook">{ICON['facebook']}</a>
        <a href="{wa()}" target="_blank" rel="noopener" aria-label="WhatsApp">{WA_SVG}</a>
      </div>
    </div>
    <div>
      <h2 class="foot-h">{t('Quick links', 'روابط سريعة')}</h2>
      <ul>{"".join(f'<li><a href="{U(h)}">{x}</a></li>' for h, x in nav())}</ul>
    </div>
    <div>
      <h2 class="foot-h">{t('Sectors', 'القطاعات')}</h2>
      <ul>{"".join(f'<li><a href="{U("projects.html")}?sector={k}">{t(en, ar)}</a></li>' for k, en, ar in SECTORS)}</ul>
    </div>
    <div>
      <h2 class="foot-h">{t('Contact', 'تواصل معنا')}</h2>
      <ul>
        <li>{address()}</li>
        <li><a href="{PHONE_TEL}">{ltr(PHONE)}</a></li>
        <li><a href="mailto:{EMAIL}">{ltr(EMAIL)}</a></li>
        <li>{t('Registration no.', 'رقم التسجيل')} {ltr('562583153')}</li>
      </ul>
    </div>
  </div>
  <div class="foot-bottom container">© <span id="year">2026</span> {t('Paragon Engineering Company. All rights reserved.', 'شركة باراجون للهندسة. جميع الحقوق محفوظة.')}</div>
</footer>
<a class="wa-float" href="{wa()}" target="_blank" rel="noopener" aria-label="{t('Chat on WhatsApp', 'تواصل عبر واتساب')}">{WA_SVG}</a>
<script src="{A('assets/main.js')}" defer></script>
</body>
</html>
'''

# ---------------------------------------------------------------- shared blocks
def section_head(eyebrow, title, text=None, h='h2'):
    p = f'<p>{text}</p>' if text else ''
    return f'<div class="section-head reveal"><span class="eyebrow">{eyebrow}</span><{h}>{title}</{h}>{p}</div>'

def page_hero(bg, crumbs, eyebrow, title, text):
    cr = " / ".join([f'<a href="{U(u)}">{n}</a>' for n, u in crumbs[:-1]] + [f'<span aria-current="page">{crumbs[-1][0]}</span>'])
    return f'''<section class="page-hero" style="background-image:url('{bg}')">
  <div class="container">
    <nav class="crumbs reveal" aria-label="{t('Breadcrumb', 'مسار التنقل')}">{cr}</nav>
    <span class="eyebrow reveal">{eyebrow}</span>
    <h1 class="reveal d1">{title}</h1>
    <p class="reveal d2">{text}</p>
  </div>
</section>
'''

def cta_band(title, text):
    return f'''<section class="cta-band">
  <div class="container cta-inner reveal">
    <div>
      <span class="eyebrow">{t('Start smart', 'ابدأ بذكاء')}</span>
      <h2>{title}</h2>
      <p>{text}</p>
      <div class="badge-line"><span class="dot"></span>{t('Free, no-obligation estimate', 'تقدير مجاني ودون أي التزام')}</div>
    </div>
    <div class="cta-actions">
      <a class="btn btn-primary" href="{U('contact.html')}#inquiry">{ICON['calendar']}{t('Schedule Appointment', 'احجز موعداً')}</a>
      <a class="btn btn-outline-light" href="{wa()}" target="_blank" rel="noopener">{WA_SVG}{t('WhatsApp', 'واتساب')}</a>
    </div>
  </div>
</section>
'''

def value_card(icon, title, items, d=0):
    li = "".join(f"<li>{ICON['check']}{x}</li>" for x in items)
    return f'<div class="value reveal{" d%d" % d if d else ""}"><h3><span class="ico">{ICON[icon]}</span>{title}</h3><ul>{li}</ul></div>'

def services():
    out = []
    for s in SERVICES:
        out.append(dict(id=s['id'], img=s['img'], icon=s['icon'], title=esc(t(*s['title'])), short=t(*s['short']), text=t(*s['text']),
                        feats=[esc(t(*f)) for f in s['feats']]))
    return out

def svc_rows():
    out = []
    for i, s in enumerate(services()):
        feats = "".join(f"<li>{ICON['check-circle']}{f}</li>" for f in s['feats'])
        links = f'<a class="link-arrow" href="{U("contact.html")}#inquiry">{t("Request this service", "اطلب هذه الخدمة")} {ICON["arrow"]}</a>'
        if s['id'] == 'joinery':
            links += f'<a class="link-arrow" href="{U("workshops.html")}">{t("Visit our workshops", "تعرّف على ورشنا")} {ICON["arrow"]}</a>'
        slug, f = s['img']; w, h = ph_dims(slug, f, True)
        out.append(f'''<article class="svc" id="{s['id']}">
  <div class="svc-media reveal"><img src="{ph(slug, f, True)}" srcset="{ph(slug, f, True)} 640w, {ph(slug, f)} 1600w" sizes="(max-width:900px) 100vw, 600px" alt="{s['title']}" width="{w}" height="{h}" loading="lazy"></div>
  <div class="svc-body reveal d1">
    <span class="tag">{i + 1:02d}</span>
    <h2 class="svc-h">{s['title']}</h2>
    <p>{s['text']}</p>
    <ul class="feat">{feats}</ul>
    <div class="svc-links">{links}</div>
  </div>
</article>''')
    return '<div class="svc-list">' + "\n".join(out) + '</div>'

def svc_grid():
    out = []
    for i, s in enumerate(services()):
        slug, f = s['img']
        out.append(f'''<a class="svc-card reveal d{i % 4 + 1}" href="{U("services.html")}#{s['id']}">
  <span class="sc-media"><img src="{ph(slug, f, True)}" alt="" loading="lazy"><span class="sc-n">{i + 1:02d}</span></span>
  <span class="sc-body"><span class="sc-ico">{ICON[s['icon']]}</span><b>{s['title']}</b><small>{s['short']}</small><span class="sc-more">{t('Learn more', 'اعرف المزيد')} {ICON['arrow']}</span></span>
</a>''')
    return '<div class="svc-grid">' + "".join(out) + '</div>'

def stages_html():
    return '<div class="steps">' + "".join(
        f'<div class="step reveal d{i % 5 + 1}"><span class="n">0{i + 1}</span><div class="ico">{ICON[ic]}</div><h3>{t(en, ar)}</h3></div>'
        for i, (ic, en, ar) in enumerate(STAGES)) + '</div>'

def stats():
    items = [(FOUNDED, '', t('Established', 'سنة التأسيس')), (20, '+', t('Years of construction experience', 'سنة خبرة في البناء')),
             (60, '+', t('Team members', 'عضواً في الفريق')), (50, '+', t('Project handovers', 'مشروعاً تم تسليمه'))]
    return '<section class="stats" aria-label="' + t('Paragon in numbers', 'باراجون في أرقام') + '"><div class="container stats-grid">' + "".join(
        f'<div class="stat reveal d{i}"><div class="num" data-count="{n}" data-suffix="{s}"{" data-plain" if n > 1000 else ""}>{n}{s}</div><div class="label">{l}</div></div>' for i, (n, s, l) in enumerate(items)) + '</div></section>'

def project_card(p, d=0, heading='h3'):
    w, h = ph_dims(p.slug, p.cover, True)
    badge = f'<span class="p-status">{t("Ongoing", "قيد التنفيذ")}</span>' if p.status == 'ongoing' else ''
    return f'''<article class="p-card reveal{' d%d' % d if d else ''}" data-sector="{p.sector}" data-contract="{p.contract}" data-search="{esc(p.search_text())}">
  <a href="{U(p.url)}" class="p-link">
    <div class="p-media"><img src="{ph(p.slug, p.cover, True)}" alt="{esc(p.name)}" width="{w}" height="{h}" loading="lazy">{badge}<span class="p-count">{ICON['grid']}{len(p.photos)}</span></div>
    <div class="p-body">
      <span class="p-sector">{sector_name(p.sector)}</span>
      <{heading} class="p-name">{p.name}</{heading}>
      <div class="p-meta"><span>{p.short_meta()}</span><span class="pill">{p.contract_name}</span></div>
    </div>
  </a>
</article>'''

def sector_cards():
    out = []
    covers = {'hospitality': ('lemon-restaurant', '03'), 'commercial': ('la-vanda-bridal-store', '01'), 'healthcare': ('dr-adel-asfour-clinic', '05'),
              'workspace': ('qcom-ramallah', '06'), 'broadcasting': ('asharq-news-ramallah', '04'), 'residential': ('sk-rooftop', '04')}
    for i, (k, en, ar) in enumerate(SECTORS):
        n = sum(1 for p in PROJECTS if p.sector == k); s, f = covers[k]
        out.append(f'<a class="sector reveal d{i % 3 + 1}" href="{U("projects.html")}?sector={k}"><img src="{ph(s, f, True)}" alt="" loading="lazy"><span class="s-body"><span class="s-name">{t(en, ar)}</span><span class="s-count">{n} {t("projects", "مشاريع")} {ICON["arrow"]}</span></span></a>')
    return '<div class="sectors">' + "".join(out) + '</div>'

def client_name(c): return t(c[1], c[2])
def client_logo(c, cls='logo-card', link=True):
    key, en, ar, slugs = c
    n = len(slugs)
    if n == 1: href = U(BY_SLUG[slugs[0]].url)
    elif n > 1: href = U('clients.html') + '#' + key
    else: href = None
    sub = (t(f'{n} project' + ('s' if n > 1 else ''), f'{n} ' + ('مشروع' if n == 1 else 'مشاريع'))) if n else t('Client', 'عميل')
    inner = f'<span class="lg"><img src="{A("assets/clients/" + key + ".webp")}" alt="{esc(en)}" loading="lazy"></span><span class="lc-name">{client_name(c)}</span><span class="lc-sub">{sub}</span>'
    if link and href: return f'<a class="{cls}" id="c-{key}" href="{href}">{inner}</a>'
    return f'<div class="{cls}" id="c-{key}">{inner}</div>'

def clients_block():
    logos = "".join(client_logo(c, 'logo-card mini') for c in CLIENTS)
    return f'''<section class="section clients" aria-labelledby="clients-h">
  <div class="container">
    {section_head(t('Clients', 'عملاؤنا'), t('Trusted by leading brands &amp; institutions', 'موضع ثقة علامات تجارية ومؤسسات رائدة'))}
    <div class="logo-grid reveal">{logos}</div>
    <div class="center mt-40"><a class="btn btn-outline" href="{U('clients.html')}">{t('View all clients', 'عرض جميع العملاء')} {ICON['arrow']}</a></div>
  </div>
</section>'''.replace('<h2>', '<h2 id="clients-h">', 1)

def service_options():
    return [esc(t(*s['title'])) for s in SERVICES] + [t("Other", "أخرى")]

def contact_section(heading, eyebrow):
    opts = "".join(f"<option>{o}</option>" for o in service_options())
    return f'''<section class="section contact" id="inquiry">
  <div class="container contact-grid">
    <div class="reveal">
      <span class="eyebrow">{eyebrow}</span>
      <h2>{heading}</h2>
      <p class="intro">{t('Tell us about your space. Paragon takes it from concept design to turnkey handover with <b>punctuality</b>, <b>integrity</b> and <b>excellence</b>. One team, one accountable partner.',
                          'أخبرنا عن مساحتك. تتولى باراجون مشروعك من التصميم المبدئي حتى التسليم الكامل بـ<b>دقة في المواعيد</b> و<b>نزاهة</b> و<b>تميّز</b>. فريق واحد وشريك واحد مسؤول.')}</p>
      <ul class="checks">
        <li>{ICON['check-circle']}<span>{t('<b>Free estimates</b>, flexible according to materials and scheduling.', '<b>تقديرات تكلفة مجانية</b> ومرنة حسب المواد والجدول الزمني.')}</span></li>
        <li>{ICON['shield']}<span>{t('All works guaranteed and warrantied.', 'جميع الأعمال مضمونة وبكفالة.')}</span></li>
        <li>{ICON['hardhat']}<span>{t('A 60+ strong team with in-house wood and metal workshops.', 'فريق يضم أكثر من 60 عضواً مع ورش خشب ومعادن خاصة بنا.')}</span></li>
      </ul>
      <div class="contact-pills">
        <a href="{wa()}" target="_blank" rel="noopener">{WA_SVG}{t('WhatsApp us', 'راسلنا عبر واتساب')}</a>
        <a href="{PHONE_TEL}">{ICON['phone']}{ltr(PHONE)}</a>
        <a href="mailto:{EMAIL}">{ICON['mail']}{ltr(EMAIL)}</a>
      </div>
    </div>
    <form class="form-card inquiry reveal d2" novalidate>
      <div class="field">{ICON['user']}<input name="name" aria-label="{t('Full name', 'الاسم الكامل')}" placeholder="{t('Full name', 'الاسم الكامل')}" required autocomplete="name"></div>
      <div class="field">{ICON['mail']}<input type="email" name="email" aria-label="{t('Email address', 'البريد الإلكتروني')}" placeholder="{t('Email address', 'البريد الإلكتروني')}" required autocomplete="email" dir="auto"></div>
      <div class="field">{ICON['phone']}<input type="tel" name="phone" aria-label="{t('Phone number', 'رقم الهاتف')}" placeholder="{t('Phone number', 'رقم الهاتف')}" autocomplete="tel" dir="auto"></div>
      <div class="field">{ICON['pin']}<input name="location" aria-label="{t('Project location', 'موقع المشروع')}" placeholder="{t('Project location (e.g. Ramallah, Al-Tireh)', 'موقع المشروع (مثال: رام الله، الطيرة)')}"></div>
      <div class="field">{ICON['grid']}<select name="service" required aria-label="{t('Service', 'الخدمة')}"><option value="" disabled selected>{t('Select a service', 'اختر الخدمة')}</option>{opts}</select></div>
      <div class="field">{ICON['msg']}<textarea name="details" aria-label="{t('Project details', 'تفاصيل المشروع')}" placeholder="{t('Tell us about your project: scope, size, timeline', 'أخبرنا عن مشروعك: النطاق والمساحة والجدول الزمني')}"></textarea></div>
      <input type="text" name="_honey" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
      <div class="form-actions">
        <button class="btn btn-primary" type="submit">{ICON['send']}{t('Send inquiry', 'إرسال الطلب')}</button>
        <button class="btn btn-wa wa-send" type="button">{WA_SVG}{t('Send on WhatsApp', 'إرسال عبر واتساب')}</button>
      </div>
      <small class="form-note">{t(f'Your inquiry goes straight to our team at {EMAIL}. Prefer chatting? Send the same details on WhatsApp.', f'يصل طلبك مباشرةً إلى فريقنا على {ltr(EMAIL)}. تفضّل المحادثة؟ أرسل التفاصيل نفسها عبر واتساب.')}</small>
      <div class="form-ok" role="status">{ICON['check-circle']}<span>{t("Thank you! Your inquiry has been sent. Our team will get back to you soon.", 'شكراً لك! تم إرسال طلبك بنجاح، وسيتواصل معك فريقنا قريباً.')}</span></div>
      <div class="form-err" role="alert">{t('Sorry, the message could not be sent right now. Please <a href="#" class="wa-fallback">send it on WhatsApp</a>, <a href="#" class="mail-fallback">email us</a>, or call', 'عذراً، تعذّر إرسال الرسالة حالياً. يرجى <a href="#" class="wa-fallback">إرسالها عبر واتساب</a> أو <a href="#" class="mail-fallback">مراسلتنا بالبريد</a> أو الاتصال على')} <a href="{PHONE_TEL}">{ltr(PHONE)}</a>.</div>
    </form>
  </div>
</section>
'''

def lightbox():
    return f'''<div class="lightbox" role="dialog" aria-modal="true" aria-label="{t('Photo viewer', 'عارض الصور')}">
  <button class="lb-btn lb-close" aria-label="{t('Close', 'إغلاق')}">{ICON['x']}</button>
  <button class="lb-btn lb-prev" aria-label="{t('Previous', 'السابق')}">{ICON['left']}</button>
  <img alt="">
  <button class="lb-btn lb-next" aria-label="{t('Next', 'التالي')}">{ICON['right']}</button>
  <div class="lb-cap"></div>
</div>'''

def gallery(slug, alt_base, start=0):
    items = []
    for i, it in enumerate(PHOTOS[slug], 1):
        f = it['f']; alt = f"{alt_base} — {t('photo', 'صورة')} {i}"
        items.append(f'<figure class="g-item reveal" data-full="{ph(slug, f)}"><img src="{ph(slug, f, True)}" alt="{esc(alt)}" width="{it["tw"]}" height="{it["th"]}" loading="{"eager" if i <= 3 else "lazy"}"><figcaption>{esc(alt_base)}</figcaption></figure>')
    return '<div class="masonry">' + "".join(items) + '</div>'

# ---------------------------------------------------------------- pages
def page_home():
    s, f = HERO['home']
    ticker = [t("Interior fit-out", "تجهيزات داخلية"), t("Turnkey solutions", "حلول تسليم المفتاح"), t("Landscape &amp; pools", "لاندسكيب وبرك سباحة"),
              t("Bespoke joinery", "نجارة حسب الطلب"), t("Renovation", "تجديد"), t("Project management", "إدارة مشاريع"),
              t("Facilities management", "إدارة المرافق"), t("Value engineering", "هندسة القيمة")]
    tk = "".join(f"<span>{x}</span>" for x in ticker * 4)
    featured = "".join(project_card(BY_SLUG[sl], i % 3 + 1) for i, sl in enumerate(FEATURED))
    ws = PHOTOS['_workshops']
    return head(t("Paragon Engineering | Fit-out, Turnkey & Landscape Contractor in Ramallah, Palestine", "باراجون للهندسة | مقاولات تجهيزات داخلية وتسليم مفتاح ولاندسكيب في رام الله، فلسطين"),
                t(f"Paragon Engineering, established {FOUNDED} in Ramallah, Palestine: interior fit-out, turnkey solutions, landscape design & construction, bespoke joinery, project and facilities management. 50+ projects handed over.",
                  f"باراجون للهندسة، تأسست عام {FOUNDED} في رام الله، فلسطين: تجهيزات داخلية، حلول تسليم مفتاح، تصميم وتنفيذ اللاندسكيب، نجارة حسب الطلب، إدارة المشاريع والمرافق. أكثر من 50 مشروعاً تم تسليمه."),
                og('home'),
                [org_ld(), {"@context": "https://schema.org", "@type": "WebSite", "name": "Paragon Engineering", "url": SITE, "inLanguage": ["en", "ar"]}]) + header("index.html") + f'''
<section class="hero" style="background-image:url('{hero_bg('home')}')">
  <div class="container">
    <div class="hero-inner">
      <span class="eyebrow reveal">{t(f'Ramallah • Since {FOUNDED} • Multidisciplinary contracting', f'رام الله • منذ {FOUNDED} • مقاولات متعددة التخصصات')}</span>
      <h1 class="reveal d1">{t('Interior fit-out, turnkey &amp; landscape, <em>from concept</em> to keys-in-hand.', 'تجهيزات داخلية وتسليم مفتاح ولاندسكيب، <em>من الفكرة</em> حتى تسليم المفتاح.')}</h1>
      <p class="lead reveal d2">{t('A multidisciplinary contracting company bringing together technical expertise, skilled craftsmanship and a commitment to quality, across residential, commercial, hospitality, healthcare, workplace and food &amp; beverage projects.',
                                  'شركة مقاولات متعددة التخصصات تجمع بين الخبرة الفنية والحرفية الماهرة والالتزام بالجودة، في المشاريع السكنية والتجارية والضيافة والرعاية الصحية ومساحات العمل والمطاعم والمقاهي.')}</p>
      <div class="hero-actions reveal d3">
        <a class="btn btn-outline-light" href="{U('projects.html')}">{t('Explore Projects', 'استعرض مشاريعنا')}</a>
        <a class="btn btn-primary" href="{U('contact.html')}#inquiry"><span class="btn-icon">{ICON['calendar']}</span>{t('Schedule Appointment', 'احجز موعداً')}</a>
      </div>
      <div class="chips reveal d4">
        <span class="chip">{ICON['check-circle']}{t('Free, flexible estimates', 'تقديرات تكلفة مجانية ومرنة')}</span>
        <span class="chip">{ICON['hammer']}{t('Bespoke joinery workshops', 'ورش نجارة حسب الطلب')}</span>
        <span class="chip">{ICON['shield']}{t('Guaranteed &amp; warrantied works', 'أعمال مضمونة وبكفالة')}</span>
      </div>
    </div>
  </div>
  <div class="hero-ticker" aria-hidden="true"><div class="track">{tk}</div></div>
</section>

{stats()}

<section class="section" id="services">
  <div class="container">
    {section_head(t('What we do', 'ماذا نقدّم'), t('Eight services, one accountable team', 'ثماني خدمات وفريق واحد مسؤول'),
                  t('From design and technical consultancy to landscape, joinery, project delivery and long-term facilities management.', 'من التصميم والاستشارات الفنية إلى اللاندسكيب والنجارة وتنفيذ المشاريع وإدارة المرافق على المدى الطويل.'))}
    {svc_grid()}
    <div class="center mt-40"><a class="btn btn-outline" href="{U('services.html')}">{t('All services in detail', 'تفاصيل جميع الخدمات')} {ICON['arrow']}</a></div>
  </div>
</section>

{cta_band(t('Schedule your appointment today', 'احجز موعدك اليوم'),
          t('All estimates are free and flexible according to materials and scheduling. Tell us what you have in mind and we will come back with options.',
            'جميع تقديرات التكلفة مجانية ومرنة حسب المواد والجدول الزمني. أخبرنا بما تفكر به وسنعود إليك بالخيارات المناسبة.'))}

<section class="section gray" id="projects">
  <div class="container">
    {section_head(t('Signature projects', 'مشاريع مميزة'), t('Spaces we have delivered', 'مساحات نفّذناها'),
                  t(f'A selection from {len(PROJECTS)} projects across hospitality, commercial, healthcare, workspace, broadcasting and residential sectors.',
                    f'مختارات من {len(PROJECTS)} مشروعاً في قطاعات الضيافة والتجارة والرعاية الصحية ومساحات العمل والبث والسكن.'))}
    <div class="p-grid">{featured}</div>
    <div class="center mt-40"><a class="btn btn-primary" href="{U('projects.html')}">{t(f'Browse all {len(PROJECTS)} projects', f'تصفّح جميع المشاريع ({len(PROJECTS)})')} {ICON['arrow']}</a></div>
  </div>
</section>

<section class="section" id="sectors">
  <div class="container">
    {section_head(t('Sectors', 'القطاعات'), t('Experience across every kind of space', 'خبرة في كل أنواع المساحات'))}
    {sector_cards()}
  </div>
</section>

<section class="section process" id="about">
  <div class="container">
    {section_head(t('About Paragon', 'عن باراجون'), t('Engineering foundation, crafted execution', 'أساس هندسي وتنفيذ متقن'),
                  t(f'Established in {FOUNDED}. Driven by professionalism, accountability and long-term client relationships.', f'تأسست عام {FOUNDED}، وتنطلق من المهنية والمسؤولية والعلاقات طويلة الأمد مع العملاء.'))}
    <div class="about-split">
      <div class="glass reveal"><h3><span class="ico">{ICON['target']}</span>{t('Who we are', 'من نحن')}</h3><p>{t(*ABOUT[0])}</p><p>{t(*ABOUT[1])}</p></div>
      <div class="glass reveal d1"><h3><span class="ico">{ICON['eye']}</span>{t('Our vision', 'رؤيتنا')}</h3><p>{t(*VISION[0])}</p></div>
    </div>
    <p class="stages-intro reveal">{t('Our integrated approach covers every stage of delivery:', 'يغطي نهجنا المتكامل كل مراحل التنفيذ:')}</p>
    {stages_html()}
    <div class="center mt-40"><a class="btn btn-primary" href="{U('about.html')}">{t('More about Paragon', 'المزيد عن باراجون')} {ICON['arrow']}</a></div>
  </div>
</section>

{clients_block()}

<section class="mission" style="background-image:url('{ph('_workshops', ws[6]['f'] if len(ws) > 6 else '01')}')">
  <div class="container reveal">
    <span class="eyebrow">{t('Wood &amp; metal workshops', 'ورش الخشب والمعادن')}</span>
    <h2>{t('Crafted with passion, built to last.', 'صُنعت بشغف لتدوم.')}</h2>
    <p>{t('Bespoke furniture, joinery and metalwork made in-house, from shop drawings to final finish, with full quality control.', 'أثاث حسب الطلب وأعمال نجارة ومعادن تُصنع في ورشنا، من المخططات التنفيذية حتى اللمسة الأخيرة، مع رقابة كاملة على الجودة.')}</p>
    <div style="margin-top:28px"><a class="btn btn-outline-light" href="{U('workshops.html')}">{t('Visit the workshops', 'تعرّف على الورش')} {ICON['arrow']}</a></div>
  </div>
</section>

{contact_section(t('Ready to build something <br>exceptional?', 'جاهز لبناء<br>شيء استثنائي؟'), t('Start a project', 'ابدأ مشروعك'))}
''' + footer()

def page_services():
    s, f = HERO['services']
    crumbs = [(t('Home', 'الرئيسية'), 'index.html'), (t('Services', 'الخدمات'), 'services.html')]
    svc_ld = {"@context": "https://schema.org", "@type": "ItemList", "name": t("Paragon services", "خدمات باراجون"),
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {"@type": "Service", "name": t(*x['title']), "description": t(*x['text']),
                                   "provider": {"@id": SITE + "#org"}, "areaServed": "Palestine", "url": abs_url('services.html') + '#' + x['id']}} for i, x in enumerate(SERVICES)]}
    toc = "".join(f'<a href="#{x["id"]}"><span>{i + 1:02d}</span>{esc(t(*x["title"]))}</a>' for i, x in enumerate(SERVICES))
    return head(t("Services | Fit-out, Turnkey, Landscape, Joinery & Project Management | Paragon Engineering", "الخدمات | تجهيزات داخلية، تسليم مفتاح، لاندسكيب، نجارة وإدارة مشاريع | باراجون للهندسة"),
                t("Design & technical consultancy, general contracting & fit-out, bespoke joinery, landscape design & construction, project management, facilities management, value engineering and property renovation in Palestine.",
                  "التصميم والاستشارات الفنية، المقاولات العامة والتجهيزات الداخلية، النجارة حسب الطلب، تصميم وتنفيذ اللاندسكيب، إدارة المشاريع والمرافق، هندسة القيمة وتجديد العقارات في فلسطين."),
                og('services'), [crumbs_ld(crumbs), svc_ld]) + header("services.html") + \
      page_hero(hero_bg('services'), crumbs, t('Services', 'الخدمات'),
                t('Everything your project needs, under one roof.', 'كل ما يحتاجه مشروعك تحت سقف واحد.'),
                t('Eight integrated services, from design and technical development to construction, landscape, handover and long-term care.',
                  'ثماني خدمات متكاملة، من التصميم والتطوير الفني إلى التنفيذ واللاندسكيب والتسليم والعناية طويلة الأمد.')) + f'''
<section class="section">
  <div class="container">
    <nav class="svc-toc reveal" aria-label="{t('Services', 'الخدمات')}">{toc}</nav>
    {svc_rows()}
  </div>
</section>

{stats()}

<section class="section">
  <div class="container">
    {section_head(t('Sectors', 'القطاعات'), t('Where we work', 'أين نعمل'))}
    {sector_cards()}
  </div>
</section>

{cta_band(t('Not sure which service you need?', 'لست متأكداً من الخدمة التي تحتاجها؟'),
          t("Book a free appointment. We'll visit, listen, and recommend the right scope, with an estimate that's flexible according to materials and scheduling.",
            'احجز موعداً مجانياً. سنزورك ونستمع إليك ونقترح النطاق المناسب، مع تقدير تكلفة مرن حسب المواد والجدول الزمني.'))}

{contact_section(t("Let's talk about <br>your project.", 'لنتحدث عن<br>مشروعك.'), t('Start a project', 'ابدأ مشروعك'))}
''' + footer()

def page_about():
    s, f = HERO['about']
    crumbs = [(t('Home', 'الرئيسية'), 'index.html'), (t('About', 'من نحن'), 'about.html')]
    about_ld = {"@context": "https://schema.org", "@type": "AboutPage", "name": t("About Paragon Engineering", "عن باراجون للهندسة"), "url": abs_url('about.html'),
                "mainEntity": {"@id": SITE + "#org"}, "inLanguage": LANG}
    secs = [('residential', t('Residential', 'سكني')), ('commercial', t('Commercial', 'تجاري')), ('hospitality', t('Hospitality', 'الضيافة')),
            ('healthcare', t('Healthcare', 'الرعاية الصحية')), ('workspace', t('Workplace', 'مساحات العمل')), ('hospitality', t('Food &amp; beverage', 'المطاعم والمقاهي'))]
    sec_html = "".join(f'<a class="chip-f" href="{U("projects.html")}?sector={k}">{n}</a>' for k, n in secs)
    vals = [('award', t('Professionalism', 'المهنية'), t('Technical expertise and skilled craftsmanship, applied with discipline on every site.', 'خبرة فنية وحرفية ماهرة تُطبَّق بانضباط في كل موقع.')),
            ('shield', t('Accountability', 'المسؤولية'), t('Meticulous planning, effective coordination and rigorous quality control.', 'تخطيط دقيق وتنسيق فعّال ورقابة صارمة على الجودة.')),
            ('user', t('Long-term relationships', 'علاقات طويلة الأمد'), t('Enduring value through reliable execution and consistently high-quality results.', 'قيمة مستدامة من خلال تنفيذ موثوق ونتائج عالية الجودة باستمرار.'))]
    vals_html = "".join(f'<div class="value reveal d{i}"><h3><span class="ico">{ICON[ic]}</span>{a}</h3><p class="v-text">{d}</p></div>' for i, (ic, a, d) in enumerate(vals))
    return head(t(f"About Us | Multidisciplinary Contracting Company Since {FOUNDED} | Paragon Engineering", f"من نحن | شركة مقاولات متعددة التخصصات منذ {FOUNDED} | باراجون للهندسة"),
                t(ABOUT[0][0], ABOUT[0][1]), og('home'), [crumbs_ld(crumbs), about_ld, org_ld()]) + header("about.html") + \
      page_hero(hero_bg('about'), crumbs, t('About us', 'من نحن'),
                t('Engineering foundation. Crafted execution.', 'أساس هندسي. تنفيذ متقن.'),
                t(f'A multidisciplinary contracting company, established in {FOUNDED}.', f'شركة مقاولات متعددة التخصصات، تأسست عام {FOUNDED}.')) + f'''
<section class="section">
  <div class="container about-intro">
    <div class="reveal">
      <span class="eyebrow">{t('Who we are', 'من نحن')}</span>
      <h2>{t('Spaces that meet the highest standards of function, aesthetics and execution.', 'مساحات تستوفي أعلى معايير الوظيفة والجمال وجودة التنفيذ.')}</h2>
      <p class="lead-p">{t(*ABOUT[0])}</p>
      <p>{t(*ABOUT[1])}</p>
      <div class="about-sectors">{sec_html}</div>
    </div>
    <div class="about-photo reveal d1"><img src="{ph('sd-villa', '04', True)}" srcset="{ph('sd-villa', '04', True)} 640w, {ph('sd-villa', '04')} 1600w" sizes="(max-width:900px) 100vw, 520px" alt="{t('S.D. Villa interior by Paragon', 'تصميم داخلي لفيلا S.D. من تنفيذ باراجون')}" loading="lazy"></div>
  </div>
</section>

{stats()}

<section class="section gray">
  <div class="container">
    {section_head(t('Our approach', 'نهجنا'), t('An integrated approach to every stage', 'نهج متكامل في كل مرحلة'), t(*ABOUT[2]))}
    <div class="stages-light">{stages_html()}</div>
    <div class="about-split light mt-40">
      <div class="value reveal"><h3><span class="ico">{ICON['compass']}</span>{t('Every project is different', 'لكل مشروع خصوصيته')}</h3><p class="v-text">{t(*ABOUT[3])}</p></div>
      <div class="value reveal d1"><h3><span class="ico">{ICON['shield']}</span>{t('Built on trust', 'قائمون على الثقة')}</h3><p class="v-text">{t(*ABOUT[4])}</p></div>
    </div>
  </div>
</section>

<section class="section process">
  <div class="container">
    {section_head(t('Our vision', 'رؤيتنا'), t('A leading design-build partner across the MENA region', 'شريك رائد في التصميم والتنفيذ في منطقة الشرق الأوسط وشمال أفريقيا'))}
    <blockquote class="vision-quote reveal">{t(*VISION[0])}</blockquote>
    <div class="about-split">
      <div class="glass reveal"><h3><span class="ico">{ICON['target']}</span>{t('Exceeding expectations', 'تجاوز التوقعات')}</h3><p>{t(*VISION[1])}</p></div>
      <div class="glass reveal d1"><h3><span class="ico">{ICON['user']}</span>{t('People, sustainability &amp; community', 'الإنسان والاستدامة والمجتمع')}</h3><p>{t(*VISION[2])}</p></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {section_head(t('What drives us', 'ما يحرّكنا'), t('Professionalism • Accountability • Relationships', 'المهنية • المسؤولية • العلاقات'))}
    <div class="values">{vals_html}</div>
    <div class="center mt-40"><a class="btn btn-outline" href="{U('services.html')}">{t('Explore our services', 'استكشف خدماتنا')} {ICON['arrow']}</a> <a class="btn btn-primary" href="{U('projects.html')}">{t('See our projects', 'شاهد مشاريعنا')} {ICON['arrow']}</a></div>
  </div>
</section>

{clients_block()}

{cta_band(t('Let’s build something lasting', 'لنبنِ معاً ما يدوم'), t('Tell us about your space and we will come back with ideas, a timeline and a free estimate.', 'أخبرنا عن مساحتك وسنعود إليك بأفكار وجدول زمني وتقدير تكلفة مجاني.'))}
''' + footer()

def page_projects():
    s, f = HERO['projects']
    chips = [('all', t('All', 'الكل'), len(PROJECTS))] + [(k, t(en, ar), sum(1 for p in PROJECTS if p.sector == k)) for k, en, ar in SECTORS]
    chips_html = "".join(f'<button type="button" class="chip-f{" active" if k == "all" else ""}" data-sector="{k}" aria-pressed="{"true" if k == "all" else "false"}">{n} <span>{c}</span></button>' for k, n, c in chips)
    copts = "".join(f'<option value="{k}">{t(*v)}</option>' for k, v in CONTRACTS.items())
    cards = "".join(project_card(p, heading='h2') for p in PROJECTS)
    items_ld = {"@context": "https://schema.org", "@type": "ItemList", "name": t("Paragon projects", "مشاريع باراجون"),
                "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": abs_url(p.url), "name": p.name} for i, p in enumerate(PROJECTS)]}
    return head(t(f"Projects Portfolio | {len(PROJECTS)} Fit-out & Design-Build Projects | Paragon Engineering", f"معرض المشاريع | {len(PROJECTS)} مشروع تجهيز وتصميم وتنفيذ | باراجون للهندسة"),
                t("Search Paragon's portfolio: restaurants, hotels, offices, clinics, studios, villas and apartments in Ramallah, Jerusalem and across Palestine, each with a full photo gallery.",
                  "ابحث في معرض أعمال باراجون: مطاعم وفنادق ومكاتب وعيادات واستوديوهات وفلل وشقق في رام الله والقدس وأنحاء فلسطين، مع معرض صور كامل لكل مشروع."),
                og('projects'), [crumbs_ld([(t('Home', 'الرئيسية'), 'index.html'), (t('Projects', 'المشاريع'), 'projects.html')]), items_ld]) + header("projects.html") + \
      page_hero(hero_bg('projects'), [(t('Home', 'الرئيسية'), 'index.html'), (t('Projects', 'المشاريع'), 'projects.html')], t('Project portfolio', 'معرض المشاريع'),
                t('Find a project.', 'ابحث عن مشروع.'),
                t(f'Search {len(PROJECTS)} projects by name, client, sector, city or year, then open any project to see its full photo gallery.',
                  f'ابحث في {len(PROJECTS)} مشروعاً بالاسم أو العميل أو القطاع أو المدينة أو السنة، ثم افتح أي مشروع لمشاهدة معرض صوره الكامل.')) + f'''
<section class="section finder-sec">
  <div class="container">
    <div class="finder" role="search">
      <div class="search-box">
        {ICON['search']}
        <input id="project-search" type="search" autocomplete="off" spellcheck="false"
               placeholder="{t('Search projects, clients, sectors, cities…', 'ابحث عن مشروع أو عميل أو قطاع أو مدينة…')}"
               aria-label="{t('Search projects', 'البحث في المشاريع')}">
        <kbd aria-hidden="true">/</kbd>
      </div>
      <div class="filters">
        <div class="chips-f" role="group" aria-label="{t('Filter by sector', 'التصفية حسب القطاع')}">{chips_html}</div>
        <select id="contract-filter" aria-label="{t('Form of contract', 'نوع العقد')}"><option value="all">{t('All contract types', 'كل أنواع العقود')}</option>{copts}</select>
      </div>
      <p class="result-count" aria-live="polite" data-tpl-en="Showing {{n}} of {{t}} projects" data-tpl-ar="عرض {{n}} من {{t}} مشروعاً"></p>
    </div>
    <div class="p-grid" id="project-grid">{cards}</div>
    <div class="empty" hidden>
      <p>{t('No projects match your search.', 'لا توجد مشاريع تطابق بحثك.')}</p>
      <button type="button" class="btn btn-outline reset-search">{t('Clear search', 'مسح البحث')}</button>
    </div>
  </div>
</section>

{clients_block()}

{cta_band(t('Your project could be next', 'مشروعك قد يكون التالي'), t('All estimates are free and flexible according to materials and scheduling.', 'جميع تقديرات التكلفة مجانية ومرنة حسب المواد والجدول الزمني.'))}
''' + footer()

def client_strip(p):
    cs = [c for c in CLIENTS if p.slug in c[3]]
    if not cs: return ''
    items = "".join(f'<a class="client-chip" href="{U("clients.html")}#c-{c[0]}"><img src="{A("assets/clients/" + c[0] + ".webp")}" alt="" loading="lazy">{client_name(c)}</a>' for c in cs)
    return f'<div class="client-strip reveal"><span>{t("Client", "العميل")}</span>{items}</div>'

def page_project(p):
    idx = PROJECTS.index(p); prev_p = PROJECTS[idx - 1]; next_p = PROJECTS[(idx + 1) % len(PROJECTS)]
    related = [q for q in PROJECTS if q.sector == p.sector and q is not p][:3]
    if len(related) < 3: related += [q for q in PROJECTS if q not in related and q is not p][:3 - len(related)]
    title_loc = f" {t('—', '—')} {p.loc}" if p.loc else ''
    d = p.description(); meta_desc = (f"{p.name}: {d[0].lower() + d[1:]}" if LANG == 'en' else f"{p.name}: {d}")[:300]
    crumbs = [(t('Home', 'الرئيسية'), 'index.html'), (t('Projects', 'المشاريع'), 'projects.html'), (p.name, p.url)]
    work_ld = {"@context": "https://schema.org", "@type": "CreativeWork", "name": p.name, "about": t(*SECTOR[p.sector]) if False else SECTOR[p.sector][0],
               "description": p.description(), "creator": {"@id": SITE + "#org"}, "dateCreated": str(p.date[0]),
               "image": [ph_abs(p.slug, it['f']) for it in p.photos[:10]], "url": abs_url(p.url), "inLanguage": LANG}
    if p.loc_en: work_ld["locationCreated"] = {"@type": "Place", "name": p.loc_en + ", Palestine"}
    facts = [(t('Sector', 'القطاع'), f'<a href="{U("projects.html")}?sector={p.sector}">{sector_name(p.sector)}</a>'),
             (t('Form of contract', 'نوع العقد'), p.contract_name),
             (t('Completion', 'الإنجاز') if p.status == 'done' else t('Status', 'الحالة'), p.date_text() if p.status == 'done' else t(f'Ongoing · {p.date_text()}', f'قيد التنفيذ · {p.date_text()}')),
             (t('Location', 'الموقع'), p.loc or t('Palestine', 'فلسطين')),
             (t('Photos', 'الصور'), str(len(p.photos)))]
    facts_html = "".join(f'<div><span>{k}</span><b>{v}</b></div>' for k, v in facts)
    rel_html = "".join(project_card(q, i + 1) for i, q in enumerate(related))
    return head(t(f"{p.en}{(' ' + p.loc_en) if p.loc_en else ''} | {SECTOR[p.sector][0]} Fit-out Project | Paragon Engineering",
                  f"{p.ar}{(' ' + p.loc_ar) if p.loc_ar else ''} | مشروع {SECTOR[p.sector][1]} | باراجون للهندسة"),
                meta_desc, og(p.slug), [crumbs_ld(crumbs), work_ld]) + header("projects.html") + \
      page_hero(ph(p.slug, p.cover), crumbs, sector_name(p.sector), p.name, (p.contract_name + ' · ' + p.date_text()) + (f' · {p.loc}' if p.loc else '')) + f'''
<section class="section project-detail">
  <div class="container">
    <div class="facts reveal">{facts_html}</div>
    <p class="p-desc reveal">{p.description()}</p>
    {client_strip(p)}
    <h2 class="gal-h reveal">{t('Project gallery', 'معرض صور المشروع')} <span>{len(p.photos)} {t('photos', 'صور')}</span></h2>
    {gallery(p.slug, p.name)}
    <nav class="p-nav" aria-label="{t('More projects', 'مشاريع أخرى')}">
      <a href="{U(prev_p.url)}" class="prev"><span>{ICON['left']}{t('Previous project', 'المشروع السابق')}</span><b>{prev_p.name}</b></a>
      <a href="{U('projects.html')}" class="all">{ICON['grid']}<span>{t('All projects', 'كل المشاريع')}</span></a>
      <a href="{U(next_p.url)}" class="next"><span>{t('Next project', 'المشروع التالي')}{ICON['right']}</span><b>{next_p.name}</b></a>
    </nav>
  </div>
</section>

<section class="section gray">
  <div class="container">
    {section_head(t('More projects', 'مشاريع أخرى'), t(f'More in {SECTOR[p.sector][0]}', f'المزيد في قطاع {SECTOR[p.sector][1]}'))}
    <div class="p-grid">{rel_html}</div>
  </div>
</section>

{cta_band(t('Planning something similar?', 'تخطط لمشروع مشابه؟'), t('Tell us about your space and we will come back with ideas, a timeline and a free estimate.', 'أخبرنا عن مساحتك وسنعود إليك بأفكار وجدول زمني وتقدير تكلفة مجاني.'))}
{lightbox()}
''' + footer()

def page_clients():
    crumbs = [(t('Home', 'الرئيسية'), 'index.html'), (t('Clients', 'عملاؤنا'), 'clients.html')]
    with_projects = [c for c in CLIENTS if c[3]]
    cards = "".join(client_logo(c) for c in CLIENTS)
    groups = []
    for i, c in enumerate(with_projects):
        rows = "".join(f'<a class="cg-proj" href="{U(BY_SLUG[s].url)}"><img src="{ph(s, BY_SLUG[s].cover, True)}" alt="" loading="lazy"><span><b>{BY_SLUG[s].name}</b><small>{sector_name(BY_SLUG[s].sector)} · {BY_SLUG[s].short_meta()}</small></span>{ICON["arrow"]}</a>' for s in c[3])
        groups.append(f'''<div class="client-group reveal d{i % 3 + 1}" id="{c[0]}">
      <div class="cg-head"><span class="lg sm"><img src="{A('assets/clients/' + c[0] + '.webp')}" alt="{esc(c[1])}" loading="lazy"></span><h3>{client_name(c)}</h3></div>
      {rows}
    </div>''')
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": t("Paragon clients", "عملاء باراجون"),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {"@type": "Organization", "name": c[1]}} for i, c in enumerate(CLIENTS)]}
    return head(t("Clients | Brands & Institutions We Have Built For | Paragon Engineering", "عملاؤنا | علامات تجارية ومؤسسات نفّذنا لها | باراجون للهندسة"),
                t(f"Paragon Engineering has delivered fit-out and design-build projects for {len(CLIENTS)} clients including Bloomberg, Asharq News, Oxfam, Userpilot, Hyundai, Institut Français and Lemon.",
                  f"نفّذت باراجون للهندسة مشاريع تجهيز وتصميم وتنفيذ لـ{len(CLIENTS)} عميلاً، منهم بلومبرغ والشرق للأخبار وأوكسفام وUserpilot وهيونداي والمعهد الفرنسي وليمون."),
                og('projects'), [crumbs_ld(crumbs), ld]) + header("clients.html") + \
      page_hero(hero_bg('projects'), crumbs, t('Clients', 'عملاؤنا'),
                t('Trusted by leading brands &amp; institutions.', 'موضع ثقة علامات تجارية ومؤسسات رائدة.'),
                t(f'{len(CLIENTS)} clients across hospitality, retail, media, NGOs, healthcare and technology. Tap a logo to see the work we did for them.',
                  f'{len(CLIENTS)} عميلاً في قطاعات الضيافة والتجزئة والإعلام والمنظمات والرعاية الصحية والتكنولوجيا. اضغط على أي شعار لمشاهدة الأعمال التي نفّذناها له.')) + f'''
<section class="section">
  <div class="container">
    {section_head(t('Our clients', 'عملاؤنا'), t(f'{len(CLIENTS)} brands &amp; institutions', f'{len(CLIENTS)} علامة تجارية ومؤسسة'))}
    <div class="logo-grid big">{cards}</div>
  </div>
</section>

<section class="section gray">
  <div class="container">
    {section_head(t('Client projects', 'مشاريع العملاء'), t('Work by client', 'أعمالنا حسب العميل'), t('Projects from our portfolio, grouped by the client they were built for.', 'مشاريع من ملف أعمالنا مصنّفة حسب العميل الذي نُفّذت له.'))}
    <div class="cg-grid">{"".join(groups)}</div>
  </div>
</section>

{cta_band(t('Join our clients', 'انضم إلى عملائنا'), t('Tell us about your space and we will come back with ideas, a timeline and a free estimate.', 'أخبرنا عن مساحتك وسنعود إليك بأفكار وجدول زمني وتقدير تكلفة مجاني.'))}
''' + footer()

def page_workshops():
    s, f = HERO['workshops']
    why = [('ruler', t('Expert engineers &amp; in-house operations', 'مهندسون خبراء وعمليات داخلية'), t('Our engineers translate your vision into detailed shop drawings. Everything from joinery to painting and metalwork is done in-house, for complete quality control.', 'يحوّل مهندسونا رؤيتك إلى مخططات تنفيذية مفصّلة. وتتم جميع العمليات، من النجارة إلى الدهان وأعمال المعادن، داخل ورشنا لضمان رقابة كاملة على الجودة.')),
           ('award', t('Unwavering commitment to quality', 'التزام ثابت بالجودة'), t('Precision and attention to detail come first. Rigorous product control and stage inspections guarantee quality from raw material to final finish.', 'الدقة والاهتمام بالتفاصيل أولاً. رقابة صارمة على المنتج وفحوصات في كل مرحلة تضمن الجودة من المادة الخام حتى اللمسة الأخيرة.')),
           ('clock', t('Time management', 'إدارة الوقت'), t('We understand deadlines. Our time control keeps every piece within the agreed timeframe.', 'ندرك أهمية المواعيد. التزامنا بإدارة الوقت يضمن تسليم كل قطعة ضمن الإطار الزمني المتفق عليه.')),
           ('pen', t('Bespoke &amp; customised creations', 'تصاميم حسب الطلب'), t("No one-size-fits-all: we specialise in furniture tailored to your needs and preferences.", 'لا نؤمن بالحلول الجاهزة: نتخصص في صناعة أثاث مصمّم خصيصاً لاحتياجاتك وذوقك.')),
           ('shield', t('Safety first', 'السلامة أولاً'), t('Your safety and our team’s come first. We follow strict safety standards throughout production.', 'سلامتك وسلامة فريقنا أولوية. نلتزم بأشد معايير السلامة طوال عملية الإنتاج.'))]
    why_html = "".join(f'<div class="value reveal d{i % 3}"><h3><span class="ico">{ICON[ic]}</span>{a}</h3><p class="v-text">{b}</p></div>' for i, (ic, a, b) in enumerate(why))
    wm = [p for p in PROJECTS if p.contract == 'wm']
    crumbs = [(t('Home', 'الرئيسية'), 'index.html'), (t('Workshops', 'الورش'), 'workshops.html')]
    return head(t("Wood & Metal Workshops | Bespoke Furniture & Joinery in Ramallah | Paragon", "ورش الخشب والمعادن | أثاث ونجارة حسب الطلب في رام الله | باراجون"),
                t("Paragon's in-house wood and metal workshops make bespoke furniture, joinery and metalwork in Ramallah, from shop drawings to final finish.",
                  "تصنع ورش الخشب والمعادن في باراجون أثاثاً ونجارة وأعمال معادن حسب الطلب في رام الله، من المخططات التنفيذية حتى اللمسة الأخيرة."),
                og('workshops'), [crumbs_ld(crumbs)]) + header("workshops.html") + \
      page_hero(hero_bg('workshops'), crumbs, t('Wood &amp; metal workshops', 'ورش الخشب والمعادن'),
                t('Crafted with passion, built to last.', 'صُنعت بشغف لتدوم.'),
                t('A dedicated wood and metal workshop crafting bespoke furniture pieces that exceed expectations.', 'ورشة خشب ومعادن متخصصة تصنع قطع أثاث حسب الطلب تفوق التوقعات.')) + f'''
<section class="section">
  <div class="container">
    <div class="about-split light">
      <div class="value reveal"><h3><span class="ico">{ICON['hammer']}</span>{t('What', 'ماذا نصنع')}</h3><p class="v-text">{t('We are a dedicated wood and metal workshop committed to crafting exceptional bespoke furniture pieces that exceed your expectations.', 'نحن ورشة خشب ومعادن متخصصة، ملتزمة بصناعة قطع أثاث استثنائية حسب الطلب تفوق توقعاتك.')}</p></div>
      <div class="value reveal d1"><h3><span class="ico">{ICON['compass']}</span>{t('How', 'كيف نعمل')}</h3><p class="v-text">{t('We believe in the power of meticulous craftsmanship and prioritise precision, quality control and client satisfaction at every step of the process.', 'نؤمن بقوة الحرفية الدقيقة، ونضع الدقة ورقابة الجودة ورضا العميل في مقدمة كل خطوة من خطوات العمل.')}</p></div>
    </div>
    {section_head(t('Why us', 'لماذا نحن'), t('Five reasons clients choose our workshops', 'خمسة أسباب تجعل عملاءنا يختارون ورشنا'))}
    <div class="values five">{why_html}</div>
  </div>
</section>

<section class="section gray">
  <div class="container">
    {section_head(t('Workshop gallery', 'معرض الورش'), t('Pieces from our workshops', 'قطع من ورشنا'), t('Click any photo to view it full screen.', 'انقر على أي صورة لعرضها بملء الشاشة.'))}
    {gallery('_workshops', t('Paragon wood &amp; metal workshops', 'ورش باراجون للخشب والمعادن').replace('&amp;', '&'))}
    <div class="center mt-40"><a class="btn btn-outline" href="{IG_WORKSHOPS}" target="_blank" rel="noopener">{ICON['instagram']}{t('Follow @paragonworkshops', 'تابع @paragonworkshops')}</a></div>
  </div>
</section>

<section class="section">
  <div class="container">
    {section_head(t('Wood &amp; metal works projects', 'مشاريع أعمال الخشب والمعادن'), t('Made in our workshops', 'صُنعت في ورشنا'))}
    <div class="p-grid">{"".join(project_card(p, i % 3 + 1) for i, p in enumerate(wm))}</div>
  </div>
</section>

{contact_section(t('Have a piece <br>in mind?', 'لديك قطعة<br>في بالك؟'), t('Bespoke furniture', 'أثاث حسب الطلب'))}
{lightbox()}
''' + footer()

def page_contact():
    s, f = HERO['contact']
    q = "Sunrise+Building,+Al-Irsal+Street,+Ramallah"
    crumbs = [(t('Home', 'الرئيسية'), 'index.html'), (t('Contact', 'اتصل بنا'), 'contact.html')]
    return head(t("Contact Paragon Engineering | Contractor in Ramallah, Palestine", "اتصل بباراجون للهندسة | مقاولات في رام الله، فلسطين"),
                t("Contact Paragon Engineering in Ramallah: call or WhatsApp +972 59 452 2209 or email info@paragoncmc.com. Free, flexible estimates for design-build and fit-out projects.",
                  "تواصل مع باراجون للهندسة في رام الله: اتصل أو راسلنا عبر واتساب على ‎+972 59 452 2209 أو عبر البريد info@paragoncmc.com. تقديرات تكلفة مجانية ومرنة لمشاريع التصميم والتنفيذ والتجهيزات."),
                og('contact'), [crumbs_ld(crumbs), org_ld()]) + header("contact.html") + \
      page_hero(hero_bg('contact'), crumbs, t('Contact', 'اتصل بنا'),
                t("Let's build it right, from the first visit.", 'لنبنِ بالشكل الصحيح، من الزيارة الأولى.'),
                t('Schedule an appointment. All estimates are free and flexible according to materials and scheduling.',
                  'احجز موعداً. جميع تقديرات التكلفة مجانية ومرنة حسب المواد والجدول الزمني.')) + f'''
<section class="section gray">
  <div class="container">
    <div class="info-cards">
      <div class="info-card reveal"><span class="ico">{ICON['phone']}</span><h2 class="ic-h">{t('Call or WhatsApp', 'اتصال أو واتساب')}</h2><a href="{PHONE_TEL}">{ltr(PHONE)}</a><a href="{wa()}" target="_blank" rel="noopener">{t('Open WhatsApp chat', 'فتح محادثة واتساب')}</a></div>
      <div class="info-card reveal d1"><span class="ico">{ICON['mail']}</span><h2 class="ic-h">{t('Email', 'البريد الإلكتروني')}</h2><a href="mailto:{EMAIL}">{ltr(EMAIL)}</a></div>
      <div class="info-card reveal d2"><span class="ico">{ICON['pin']}</span><h2 class="ic-h">{t('Office', 'المكتب')}</h2><p>{address()}</p></div>
      <div class="info-card reveal d3"><span class="ico">{ICON['instagram']}</span><h2 class="ic-h">{t('Follow us', 'تابعنا')}</h2><a href="{IG}" target="_blank" rel="noopener">@paragon_cmc</a><a href="{IG_WORKSHOPS}" target="_blank" rel="noopener">@paragonworkshops</a><a href="{FB}" target="_blank" rel="noopener">facebook.com/paragoncmc</a></div>
    </div>
    <div class="map reveal"><iframe title="{t('Paragon Engineering office location', 'موقع مكتب باراجون للهندسة')}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://maps.google.com/maps?q={q}&amp;z=16&amp;hl={LANG}&amp;output=embed"></iframe></div>
  </div>
</section>

{contact_section(t('Tell us about <br>your project.', 'أخبرنا عن<br>مشروعك.'), t('Request a consultation', 'اطلب استشارة'))}
''' + footer()

def page_404():
    return head(t("Page not found | Paragon Engineering", "الصفحة غير موجودة | باراجون للهندسة"), t("This page could not be found.", "تعذّر العثور على هذه الصفحة."),
                SITE + "assets/logo/paragon-logo.png").replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">') + header("") + f'''
<section class="page-hero" style="background-image:url('{hero_bg('banner')}')"><div class="container">
  <span class="eyebrow">404</span><h1>{t('This page could not be found.', 'تعذّر العثور على هذه الصفحة.')}</h1>
  <p>{t('It may have moved. Try the projects search, or head back home.', 'ربما تم نقلها. جرّب البحث في المشاريع أو عُد إلى الصفحة الرئيسية.')}</p>
  <div class="hero-actions"><a class="btn btn-primary" href="{U('projects.html')}">{t('Search projects', 'ابحث في المشاريع')}</a><a class="btn btn-outline-light" href="{U('index.html')}">{t('Home', 'الرئيسية')}</a></div>
</div></section>
''' + footer()

# old addresses from the previous site -> new pages
REDIRECTS = {"services-nueva.html": "services.html", "project-gallery-page-nueva.html": "projects.html", "get-a-quote-nueva.html": "contact.html"}
def redirect_page(target):
    url = abs_url(target)
    return f'''<!doctype html><html lang="{LANG}"><head><meta charset="utf-8"><title>Paragon Engineering</title>
<link rel="canonical" href="{url}"><meta name="robots" content="noindex, follow"><meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("{target}" + location.search + location.hash)</script></head>
<body><a href="{target}">{t('Continue', 'متابعة')}</a></body></html>
'''

# ---------------------------------------------------------------- build
def write(rel, content):
    path = os.path.join(ROOT, ('ar/' if LANG == 'ar' else '') + rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh: fh.write(content)

def sitemap():
    pages = ["index.html", "about.html", "services.html", "projects.html", "clients.html", "workshops.html", "contact.html"] + [p.url for p in PROJECTS]
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for pg in pages:
        for lang in ('en', 'ar'):
            imgs = ''
            if pg.startswith('projects/'):
                p = BY_SLUG[pg[9:-5]]
                imgs = "".join(f'<image:image><image:loc>{ph_abs(p.slug, it["f"])}</image:loc></image:image>' for it in p.photos)
            pri = '1.0' if pg == 'index.html' else ('0.9' if pg in ('projects.html', 'services.html') else '0.7')
            out.append(f'<url><loc>{abs_url(pg, lang)}</loc><xhtml:link rel="alternate" hreflang="en" href="{abs_url(pg, "en")}"/><xhtml:link rel="alternate" hreflang="ar" href="{abs_url(pg, "ar")}"/><xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(pg, "en")}"/><priority>{pri}</priority>{imgs}</url>')
    out.append('</urlset>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write("\n".join(out))
    open(os.path.join(ROOT, 'robots.txt'), 'w').write(f"User-agent: *\nAllow: /\nDisallow: /_original-squarespace/\nDisallow: /data/\n\nSitemap: {SITE}sitemap.xml\n")

if __name__ == "__main__":
    for lang in ("en", "ar"):
        LANG = lang
        jobs = [("index.html", page_home), ("about.html", page_about), ("services.html", page_services), ("projects.html", page_projects),
                ("clients.html", page_clients), ("workshops.html", page_workshops), ("contact.html", page_contact), ("404.html", page_404)]
        for rel, fn in jobs:
            CUR = rel; ABS = (rel == '404.html'); write(rel, fn())
        ABS = False
        for p in PROJECTS:
            CUR = p.url; write(p.url, page_project(p))
        for old, new in REDIRECTS.items():
            CUR = old; write(old, redirect_page(new))
        print(lang, len(jobs) + len(PROJECTS), "pages")
    sitemap(); print("sitemap.xml, robots.txt")
