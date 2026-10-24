#!/usr/bin/env python3
"""Local development entry: python run.py"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

from app import create_app, db

app = create_app(os.environ.get("FLASK_ENV", "development"))


def _register_cli():
    from app.services.seed import run_seed

    @app.cli.command("seed")
    def seed_command():
        run_seed()

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        run_seed()
        print("Database initialized.")


try:
    if getattr(app, "cli", None) is not None:
        _register_cli()
except Exception:
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
