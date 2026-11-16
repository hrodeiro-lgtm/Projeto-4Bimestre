import logging
import os
from secrets import token_hex

from flask import Flask, render_template

from .controllers.auth import auth_bp
from .controllers.categories import categories_bp
from .controllers.home import home_bp
from .db import DEFAULT_DB_PATH
from .utils.auth_middleware import load_user


def create_app(test_config=None):
    app = Flask(__name__, template_folder="views")
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY") or token_hex(32),
        SQLITE_DB=DEFAULT_DB_PATH,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)

    app.logger.setLevel(logging.INFO)
    app.before_request(load_user)
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(categories_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    return app
