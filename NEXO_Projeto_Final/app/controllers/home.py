from math import isfinite

from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, url_for

from ..models.categories import Category
from ..models.investments import Investment
from .auth import check_csrf, csrf_token

home_bp = Blueprint("home", __name__)


@home_bp.get("/")
def index():
    return redirect(url_for("home.welcome"))


@home_bp.route("/bem-vindo", methods=["GET", "POST"])
def welcome():
    db_path = current_app.config["SQLITE_DB"]
    if request.method == "POST":
        check_csrf()
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        amount = request.form.get("amount", type=float)
        edit_id = request.form.get("edit_id", type=int)
        if not 1 <= len(name) <= 80 or not 1 <= len(category) <= 60 or amount is None or not isfinite(amount) or amount < 0.01:
            flash("Informe um nome de até 80 caracteres, uma categoria de até 60 e um valor a partir de 0,01.", "error")
            return redirect(url_for("home.welcome", editar=edit_id))

        if edit_id is None:
            Investment.create_investment(g.usuario.id, name, category, amount, db_path)
            flash("Investimento cadastrado.", "success")
            current_app.logger.info("Investimento cadastrado pela conta %s.", g.usuario.id)
        elif not Investment.update(edit_id, g.usuario.id, name, category, amount, db_path):
            abort(404)
        else:
            flash("Investimento atualizado.", "success")
        return redirect(url_for("home.welcome"))

    investments = Investment.find_by_user_id(g.usuario.id, db_path)
    edit_id = request.args.get("editar", type=int)
    editing = next((item for item in investments if item.id == edit_id), None)
    if edit_id is not None and editing is None:
        abort(404)
    return render_template(
        "welcome.html",
        name=g.usuario.name,
        investments=investments,
        total_amount=sum(item.amount for item in investments),
        editing=editing,
        categories=Category.list_for_user(g.usuario.id, db_path),
        csrf_token=csrf_token(),
    )


@home_bp.post("/investimentos/<int:investment_id>/excluir")
def delete_investment(investment_id):
    check_csrf()
    if not Investment.delete(investment_id, g.usuario.id, current_app.config["SQLITE_DB"]):
        abort(404)
    flash("Investimento excluído.", "success")
    current_app.logger.info("Investimento %s excluído pela conta %s.", investment_id, g.usuario.id)
    return redirect(url_for("home.welcome"))
