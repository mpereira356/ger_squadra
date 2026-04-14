from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from flask import current_app


def database_path() -> Path:
    uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    return Path(uri.replace("sqlite:///", ""))


def create_backup() -> Path:
    source = database_path()
    target_dir = Path(current_app.config["BACKUP_FOLDER"])
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
    shutil.copy2(source, target)
    return target


def restore_backup(source_file: Path) -> None:
    target = database_path()
    shutil.copy2(source_file, target)

