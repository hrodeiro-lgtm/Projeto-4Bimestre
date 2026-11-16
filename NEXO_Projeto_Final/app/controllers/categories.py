from sqlite3 import IntegrityError

from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, url_for

from ..models.categories import Category
from .auth import check_csrf, csrf_token

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/categorias", methods=["GET", "POST"])
def index():
    db_path = current_app.config["SQLITE_DB"]
    if request.method == "POST":
        check_csrf()
        name = request.form.get("name", "").strip()
        if not 1 <= len(name) <= 60:
            flash("Informe um nome de categoria com até 60 caracteres.", "error")
        else:
            try:
                Category.create(g.usuario.id, name, db_path)
            except IntegrityError:
                flash("Já existe uma categoria com esse nome.", "error")
            else:
                flash("Categoria cadastrada.", "success")
                current_app.logger.info("Categoria cadastrada pela conta %s.", g.usuario.id)
        return redirect(url_for("categories.index"))

    return render_template(
        "categories.html", categories=Category.list_for_user(g.usuario.id, db_path),
        csrf_token=csrf_token(),
    )


@categories_bp.post("/categorias/<int:category_id>/excluir")
def delete(category_id):
    check_csrf()
    if not Category.delete(category_id, g.usuario.id, current_app.config["SQLITE_DB"]):
        abort(404)
    flash("Categoria excluída.", "success")
    current_app.logger.info("Categoria %s excluída pela conta %s.", category_id, g.usuario.id)
    return redirect(url_for("categories.index"))
