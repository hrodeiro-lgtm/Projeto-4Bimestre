from app.db import DEFAULT_DB_PATH
from app.models.categories import Category
from app.models.investments import Investment
from app.models.users import User


def iniciar_bd(db_path=DEFAULT_DB_PATH):
    User.ensure_schema(db_path)
    Investment.ensure_schema(db_path)
    Category.ensure_schema(db_path)
    if User.find_by_username("demo", db_path) is None:
        usuario = User(username="demo", name="Usuário Demo", db_path=db_path)
        usuario.set_password("NexoDemo2026!")
        usuario.save()


if __name__ == "__main__":
    iniciar_bd()
    print("Banco pronto. Usuário de demonstração: demo")
