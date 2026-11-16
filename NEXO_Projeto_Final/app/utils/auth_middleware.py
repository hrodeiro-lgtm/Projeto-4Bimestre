from flask import current_app, g, redirect, request, session, url_for

from ..models.users import User


def load_user():
    user_id = session.get("user_id")
    g.usuario = None
    if user_id is not None:
        g.usuario = User.find_by_id(user_id, current_app.config["SQLITE_DB"])
        if g.usuario is None:
            session.clear()

    public = {"auth.login", "auth.register", "static"}
    if request.endpoint and request.endpoint not in public and g.usuario is None:
        return redirect(url_for("auth.login"))
