from app import create_app
from iniciar_bd import iniciar_bd


if __name__ == "__main__":
    app = create_app()
    iniciar_bd(app.config["SQLITE_DB"])
    app.run(host="127.0.0.1", port=5055)
