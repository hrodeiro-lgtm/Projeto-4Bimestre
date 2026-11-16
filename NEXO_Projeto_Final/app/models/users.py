"""Modelo de utilizador implementando o padrão Active Record."""

from werkzeug.security import check_password_hash, generate_password_hash

from ..db import DEFAULT_DB_PATH, DatabaseConnection


class User:
    """
    Modelo de Utilizador no padrão Active Record.
    Reúne atributos do objeto, comportamentos de instância (save, delete, verify_password)
    e métodos de classe para consultas à base de dados.
    """

    def __init__(self, id=None, username="", name="", password_hash="", db_path=None):
        self.id = id
        self.username = username
        self.name = name  # Mapeado para a coluna 'display_name' na base de dados
        self.password_hash = password_hash
        self.db_path = db_path or DEFAULT_DB_PATH

    # --- Comportamento do Objeto (Métodos de Instância) ---

    def verify_password(self, password: str) -> bool:
        """Verifica se a palavra-passe fornecida corresponde ao hash armazenado."""
        return check_password_hash(self.password_hash, password)

    def set_password(self, password: str):
        """Atualiza a palavra-passe do utilizador gerando um novo hash seguro."""
        if len(password) < 12:
            raise ValueError("A palavra-passe deve ter pelo menos 12 caracteres.")
        self.password_hash = generate_password_hash(password)

    def save(self):
        """Guarda a instância na base de dados (Insert se novo ou Update se já existir ID)."""
        with DatabaseConnection(self.db_path) as db:
            if self.id is None:
                db.cursor.execute(
                    "INSERT INTO users (username, display_name, password_hash) VALUES (?, ?, ?)",
                    (self.username, self.name, self.password_hash)
                )
                self.id = db.cursor.lastrowid
            else:
                db.cursor.execute(
                    "UPDATE users SET username = ?, display_name = ?, password_hash = ? WHERE id = ?",
                    (self.username, self.name, self.password_hash, self.id)
                )
        return self

    def delete(self):
        """Elimina a própria instância da base de dados."""
        if self.id:
            with DatabaseConnection(self.db_path) as db:
                db.cursor.execute("DELETE FROM users WHERE id = ?", (self.id,))
            self.id = None

    # --- Métodos de Classe (Buscas e Gestão da Tabela) ---

    @classmethod
    def _from_row(cls, row, db_path=None):
        """Converte um registo sqlite3.Row numa instância de User acedendo pelo nome da coluna."""
        if not row:
            return None
        return cls(
            id=row['id'],
            username=row['username'],
            name=row['display_name'],  # Acesso direto à coluna pelo nome
            password_hash=row['password_hash'],
            db_path=db_path
        )

    @classmethod
    def ensure_schema(cls, db_path=None):
        """Garante a criação da tabela de utilizadores se não existir."""
        path = db_path or DEFAULT_DB_PATH
        with DatabaseConnection(path) as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """)

    @classmethod
    def has_users(cls, db_path=None) -> bool:
        """Verifica se existe pelo menos um utilizador registado."""
        path = db_path or DEFAULT_DB_PATH
        with DatabaseConnection(path) as db:
            db.cursor.execute("SELECT 1 FROM users LIMIT 1")
            return db.cursor.fetchone() is not None

    @classmethod
    def find_by_id(cls, user_id, db_path=None):
        """Procura um utilizador pelo ID."""
        try:
            numeric_id = int(user_id)
        except (TypeError, ValueError):
            return None

        path = db_path or DEFAULT_DB_PATH
        with DatabaseConnection(path) as db:
            db.cursor.execute(
                "SELECT id, username, display_name, password_hash FROM users WHERE id = ?",
                (numeric_id,)
            )
            row = db.cursor.fetchone()
            return cls._from_row(row, db_path=path)

    @classmethod
    def find_by_username(cls, username, db_path=None):
        """Procura um utilizador pelo nome de utilizador (username)."""
        path = db_path or DEFAULT_DB_PATH
        with DatabaseConnection(path) as db:
            db.cursor.execute(
                "SELECT id, username, display_name, password_hash FROM users WHERE username = ?",
                (username,)
            )
            row = db.cursor.fetchone()
            return cls._from_row(row, db_path=path)

    @classmethod
    def all(cls, db_path=None):
        """Retorna todos os utilizadores registados na base de dados."""
        path = db_path or DEFAULT_DB_PATH
        with DatabaseConnection(path) as db:
            db.cursor.execute("SELECT id, username, display_name, password_hash FROM users")
            rows = db.cursor.fetchall()
            return [cls._from_row(row, db_path=path) for row in rows]

    @classmethod
    def create_user(cls, username, name, password, db_path=None):
        """Método de utilidade para criar e guardar um novo utilizador com validação."""
        if not username or not name or len(password) < 12:
            raise ValueError("Informe usuário, nome e uma senha com pelo menos 12 caracteres.")

        pw_hash = generate_password_hash(password)
        user = cls(username=username, name=name, password_hash=pw_hash, db_path=db_path)
        user.save()
        return user

    def __repr__(self):
        return f"<User id={self.id} username='{self.username}' name='{self.name}'>"
