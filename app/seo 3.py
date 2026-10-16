"""Structured data (JSON-LD) for search engines."""
from flask import current_app

from .content import abs_url, img_abs, lang, og_url as _og_url, project_description, project_url, s, s_raw


def site_url():
    return current_app.config["SITE_URL"]


def org_ld():
    sa = [u for u in (s_raw("facebook"), s_raw("instagram"), s_raw("instagram_workshops")) if u]
    phone = "".join(ch for ch in s_raw("phone") if ch.isdigit() or ch == "+")
    data = {
        "@context": "https://schema.org", "@type": "GeneralContractor", "@id": site_url() + "#org",
        "name": s_raw("company_name", "Paragon Engineering Company"),
        "url": site_url(), "logo": site_url() + "assets/logo/paragon-logo.png",
        "image": site_url() + "assets/og/home.jpg",
        "description": s_raw("org_description"),
        "telephone": phone, "email": s_raw("email"), "foundingDate": s_raw("founded"),
        "address": {"@type": "PostalAddress", "streetAddress": s_raw("address"), "addressLocality": "Ramallah", "addressCountry": "PS"},
        "areaServed": [{"@type": "Place", "name": "Ramallah"}, {"@type": "Place", "name": "Jerusalem"}, {"@type": "Country", "name": "Palestine"}],
        "sameAs": sa,
        "contactPoint": {"@type": "ContactPoint", "telephone": phone, "contactType": "customer service", "availableLanguage": ["English", "Arabic"]},
    }
    ar_name = (s("company_name") if lang() == "ar" else "")
    if ar_name:
        data["alternateName"] = ar_name
    return data


def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": str(n), "item": abs_url(u)} for i, (n, u) in enumerate(items)]}


def services_ld(services):
    L = lang()
    return {"@context": "https://schema.org", "@type": "ItemList", "name": "Services",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {
                "@type": "Service", "name": sv.tr("title", L), "description": sv.tr("text", L),
                "provider": {"@id": site_url() + "#org"}, "areaServed": "Palestine",
                "url": abs_url("services.html") + "#" + sv.slug}} for i, sv in enumerate(services)]}


def projects_ld(projects):
    L = lang()
    return {"@context": "https://schema.org", "@type": "ItemList", "name": "Projects",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": abs_url(project_url(p)), "name": p.tr("name", L)}
                                for i, p in enumerate(projects)]}


def clients_ld(clients):
    L = lang()
    return {"@context": "https://schema.org", "@type": "ItemList", "name": "Clients",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {"@type": "Organization", "name": c.tr("name", L)}}
                                for i, c in enumerate(clients)]}


def project_ld(p):
    L = lang()
    data = {"@context": "https://schema.org", "@type": "CreativeWork", "name": p.tr("name", L),
            "about": p.sector.name_en if p.sector else "", "description": project_description(p),
            "creator": {"@id": site_url() + "#org"}, "dateCreated": str(p.year or ""),
            "image": [img_abs(ph) for ph in p.photos[:10]], "url": abs_url(project_url(p)), "inLanguage": L}
    if p.location_en:
        data["locationCreated"] = {"@type": "Place", "name": p.location_en + ", Palestine"}
    return data


def og_url(p):
    return _og_url(p.slug, p.cover_photo)


def seo_globals():
    return dict(org_ld=org_ld, crumbs_ld=crumbs_ld, services_ld=services_ld, projects_ld=projects_ld,
                clients_ld=clients_ld, project_ld=project_ld, og_url=og_url)
