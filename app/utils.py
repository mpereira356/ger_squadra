from __future__ import annotations

import calendar
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    last_day = calendar.monthrange(year, month)[1]
    return datetime(year, month, 1), datetime(year, month, last_day, 23, 59, 59)


def currency(value: float | int | None) -> str:
    value = float(value or 0)
    text = f"{value:,.2f}"
    return f"R$ {text}".replace(",", "X").replace(".", ",").replace("X", ".")


def save_upload(file: FileStorage | None, folder: str) -> str | None:
    if not file or not file.filename:
        return None
    filename = secure_filename(file.filename)
    suffix = Path(filename).suffix
    generated = f"{uuid4().hex}{suffix}"
    target_dir = Path(current_app.config["UPLOAD_FOLDER"]) / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    file.save(target_dir / generated)
    return f"uploads/{folder}/{generated}"

