from dataclasses import dataclass

from ..db import DatabaseConnection


@dataclass
class Category:
    id: int
    name: str

    @staticmethod
    def ensure_schema(db_path):
        with DatabaseConnection(db_path) as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
                    name TEXT NOT NULL COLLATE NOCASE,
                    UNIQUE (user_id, name)
                )
            """)

    @staticmethod
    def create(user_id, name, db_path):
        with DatabaseConnection(db_path) as db:
            db.cursor.execute(
                "INSERT INTO categories (user_id, name) VALUES (?, ?)", (user_id, name)
            )

    @classmethod
    def list_for_user(cls, user_id, db_path):
        with DatabaseConnection(db_path) as db:
            rows = db.cursor.execute(
                "SELECT id, name FROM categories WHERE user_id = ? ORDER BY name", (user_id,)
            ).fetchall()
            return [cls(**row) for row in rows]

    @staticmethod
    def delete(category_id, user_id, db_path):
        with DatabaseConnection(db_path) as db:
            db.cursor.execute(
                "DELETE FROM categories WHERE id = ? AND user_id = ?", (category_id, user_id)
            )
            return db.cursor.rowcount > 0
