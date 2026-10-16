"""Optional email notification for new contact-form inquiries (configure MAIL_* env vars)."""
import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app

from .extensions import db
from .models import Setting


def send_inquiry_email(inq):
    cfg = current_app.config
    row = db.session.get(Setting, "notify_email")
    to = (row.en if row else "") or ""
    if not (cfg.get("MAIL_SERVER") and to):
        return False
    msg = EmailMessage()
    msg["Subject"] = f"New website inquiry — {inq.service or 'General'} — {inq.name}"
    msg["From"] = cfg.get("MAIL_FROM") or cfg.get("MAIL_USERNAME") or to
    msg["To"] = to
    msg["Reply-To"] = inq.email
    msg.set_content(
        f"Name: {inq.name}\nEmail: {inq.email}\nPhone: {inq.phone or '-'}\nLocation: {inq.location or '-'}\n"
        f"Service: {inq.service or '-'}\nSite language: {inq.lang}\n\nProject details:\n{inq.details or '-'}\n\n"
        f"Sent from: {inq.page or '-'}\nAll inquiries: {cfg['SITE_URL']}admin/inquiries\n")
    try:
        if cfg.get("MAIL_USE_SSL"):
            server = smtplib.SMTP_SSL(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=10, context=ssl.create_default_context())
        else:
            server = smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=10)
            if cfg.get("MAIL_USE_TLS"):
                server.starttls(context=ssl.create_default_context())
        if cfg.get("MAIL_USERNAME"):
            server.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as exc:  # never break the form because email failed
        current_app.logger.warning("Inquiry email failed: %s", exc)
        return False
