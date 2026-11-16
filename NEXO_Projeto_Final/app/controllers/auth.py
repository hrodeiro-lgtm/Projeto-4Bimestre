import secrets
from sqlite3 import IntegrityError

from flask import Blueprint, abort, current_app, flash, g, make_response, redirect
from flask import render_template, request, session, url_for

from ..models.users import User

auth_bp = Blueprint("auth", __name__)


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def check_csrf():
    submitted = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not expected or not secrets.compare_digest(submitted, expected):
        abort(400)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario is not None:
        return redirect(url_for("home.welcome"))

    if request.method == "GET":
        return render_template(
            "login.html", csrf_token=csrf_token(),
            remembered_username=request.cookies.get("remembered_username", ""),
        )

    check_csrf()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = User.find_by_username(username, current_app.config["SQLITE_DB"])
    if user is None or len(password) > 128 or not user.verify_password(password):
        current_app.logger.warning("Falha na autenticação.")
        flash("Usuário ou senha inválidos.", "error")
        return render_template("login.html", csrf_token=csrf_token(), remembered_username=username), 401

    session.clear()
    session["user_id"] = user.id
    session["username"] = user.username
    flash("Login realizado.", "success")
    current_app.logger.info("Login realizado para a conta %s.", user.id)
    response = make_response(redirect(url_for("home.welcome")))
    if request.form.get("remember"):
        response.set_cookie("remembered_username", user.username, max_age=30*24*60*60,
                            httponly=True, samesite="Lax")
    else:
        response.delete_cookie("remembered_username")
    return response


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def register():
    if g.usuario is not None:
        return redirect(url_for("home.welcome"))
    if request.method == "POST":
        check_csrf()
        username = request.form.get("username", "").strip()
        name = request.form.get("display_name", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirm_password", "")
        if not 1 <= len(username) <= 40 or not 1 <= len(name) <= 80:
            flash("Informe um usuário de até 40 caracteres e um nome de até 80.", "error")
        elif not 12 <= len(password) <= 128:
            flash("A senha deve ter entre 12 e 128 caracteres.", "error")
        elif password != confirmation:
            flash("As senhas não coincidem.", "error")
        else:
            try:
                User.create_user(username, name, password, current_app.config["SQLITE_DB"])
            except IntegrityError:
                flash("Esse nome de usuário já está em uso.", "error")
            else:
                current_app.logger.info("Nova conta cadastrada.")
                flash("Conta criada. Entre com seu usuário e sua senha.", "success")
                return redirect(url_for("auth.login"))
    return render_template("register.html", csrf_token=csrf_token())


@auth_bp.post("/logout")
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("auth.login"))
