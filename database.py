import sqlite3
import click
from flask import g, current_app


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row 
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        db.execute("PRAGMA foreign_keys = ON")

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                failed_attempts INTEGER DEFAULT 0,
                locked_until    DATETIME DEFAULT NULL
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_entries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                site_name   TEXT    NOT NULL,
                site_url    TEXT,
                username    TEXT    NOT NULL,
                enc_password BLOB   NOT NULL,   -- AES-256-GCM ciphertext
                iv          BLOB    NOT NULL,   -- 12-byte nonce
                tag         BLOB    NOT NULL,   -- 16-byte auth tag
                notes       TEXT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        db.commit()
        db.close()

    app.teardown_appcontext(close_db)
