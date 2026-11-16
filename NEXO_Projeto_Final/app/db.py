"""Conexão local com SQLite usando apenas a biblioteca nativa sqlite3."""

from pathlib import Path
import sqlite3


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "nexo.sqlite3"


class DatabaseConnection:
    """Context manager usado pelos modelos para abrir e fechar o SQLite."""

    def __init__(self, db_path=None):
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.connection = None

    def __enter__(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
        finally:
            self.connection.close()
