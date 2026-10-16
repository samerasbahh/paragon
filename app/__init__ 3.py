"""Paragon Engineering website + CMS (Flask)."""
import os

from flask import Flask, g, render_template, request

from .config import BASE_DIR, Config
from .extensions import csrf, db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="static", static_url_path="/assets",
                instance_path=os.path.join(BASE_DIR, "instance"))
    app.config.from_object(config_class)
    os.makedirs(app.instance_path, exist_ok=True)

    if not app.config.get("SECRET_KEY"):
        # Development fallback: a random key stored in instance/ (set SECRET_KEY in production).
        key_file = os.path.join(app.instance_path, "secret_key")
        if not os.path.exists(key_file):
            with open(key_file, "w") as fh:
                fh.write(os.urandom(32).hex())
        with open(key_file) as fh:
            app.config["SECRET_KEY"] = fh.read().strip()

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message = "Please sign in to continue."

    from . import models  # noqa: F401  (register models)
    from .content import commit_new_blocks, template_globals
    from .public import public, site
    from .admin import admin

    app.register_blueprint(site)
    app.register_blueprint(public, name="public_en")
    app.register_blueprint(public, name="public_ar", url_prefix="/ar")
    app.register_blueprint(admin, url_prefix="/admin")

    from .seo import seo_globals
    app.jinja_env.globals.update(template_globals())
    app.jinja_env.globals.update(seo_globals())
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.after_request(commit_new_blocks)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if request.path.startswith("/admin"):
            resp.headers.setdefault("X-Frame-Options", "DENY")
            resp.headers.setdefault("Cache-Control", "no-store")
        return resp

    @app.errorhandler(404)
    def not_found(e):
        g.lang = "ar" if request.path.startswith("/ar/") or request.path == "/ar" else "en"
        if request.path.startswith("/admin") or request.path.startswith("/assets"):
            return "Not found", 404
        return render_template("public/404.html", page_key="404", cur=""), 404

    from .cli import register_cli
    register_cli(app)
    return app
