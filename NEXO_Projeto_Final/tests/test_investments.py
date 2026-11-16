from app.models.investments import Investment

from app.models.users import User
from iniciar_bd import iniciar_bd


def test_investment_persists_and_lists_from_sqlite(tmp_path):
    db_path = tmp_path / "atividade.sqlite3"
    iniciar_bd(db_path)
    user_id = User.find_by_username("demo", db_path).id

    created = Investment.create_investment(
        user_id=user_id,
        name="Tesouro Selic",
        category="Renda Fixa",
        amount=1500.50,
        db_path=db_path,
    )

    assert created.id is not None
    items = Investment.find_by_user_id(user_id, db_path=db_path)
    assert [(item.name, item.category, item.amount) for item in items] == [
        ("Tesouro Selic", "Renda Fixa", 1500.50)
    ]
    assert db_path.exists()
