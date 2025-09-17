from app import app, db


def initialize_database() -> None:
    """Create all tables defined in SQLAlchemy models."""
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado: verdetch.db")


if __name__ == "__main__":
    initialize_database()


