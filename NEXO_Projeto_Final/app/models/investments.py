from dataclasses import dataclass

from ..db import DatabaseConnection


@dataclass
class Investment:
    id: int
    name: str
    category: str
    amount: float

    @staticmethod
    def ensure_schema(db_path=None):
        with DatabaseConnection(db_path) as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS investments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

    @classmethod
    def create_investment(cls, user_id, name, category, amount, db_path=None):
        with DatabaseConnection(db_path) as db:
            db.cursor.execute(
                "INSERT INTO investments (user_id, name, category, amount) VALUES (?, ?, ?, ?)",
                (user_id, name, category, amount),
            )
            return cls(db.cursor.lastrowid, name, category, amount)

    @classmethod
    def find_by_user_id(cls, user_id, db_path=None):
        with DatabaseConnection(db_path) as db:
            rows = db.cursor.execute(
                "SELECT id, name, category, amount FROM investments WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
            return [cls(**row) for row in rows]

    @staticmethod
    def update(investment_id, user_id, name, category, amount, db_path=None):
        with DatabaseConnection(db_path) as db:
            db.cursor.execute(
                "UPDATE investments SET name = ?, category = ?, amount = ? WHERE id = ? AND user_id = ?",
                (name, category, amount, investment_id, user_id),
            )
            return db.cursor.rowcount > 0

    @staticmethod
    def delete(investment_id, user_id, db_path=None):
        with DatabaseConnection(db_path) as db:
            db.cursor.execute(
                "DELETE FROM investments WHERE id = ? AND user_id = ?",
                (investment_id, user_id),
            )
            return db.cursor.rowcount > 0
