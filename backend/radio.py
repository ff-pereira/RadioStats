from api import create_app

app = create_app()


@app.cli.group()
def db():
    """Database commands."""
    pass


@db.command()
def upgrade():
    """Create or upgrade the database."""
    from alembic.config import main
    main(argv=['upgrade', 'head'])


if __name__ == "__main__":
    app.run()
