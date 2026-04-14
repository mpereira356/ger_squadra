from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-this-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'team_manager.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True
    WTF_CSRF_TIME_LIMIT = None
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    UPLOAD_FOLDER = str(BASE_DIR / "app" / "static" / "uploads")
    REPORTS_FOLDER = str(BASE_DIR / "instance" / "reports")
    BACKUP_FOLDER = str(BASE_DIR / "app" / "static" / "uploads" / "backups")
    DEFAULT_TIMEZONE = os.environ.get("APP_TIMEZONE", "America/Sao_Paulo")
    DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin")
    DEFAULT_TEAM_NAME = "Amigos da Squadra"
