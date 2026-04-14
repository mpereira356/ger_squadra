from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models import MonthlyClosure


def get_or_create_closure(year: int, month: int) -> MonthlyClosure:
    closure = MonthlyClosure.query.filter_by(reference_year=year, reference_month=month).first()
    if not closure:
        closure = MonthlyClosure(reference_year=year, reference_month=month)
        db.session.add(closure)
    return closure


def is_month_closed(year: int, month: int) -> bool:
    closure = MonthlyClosure.query.filter_by(reference_year=year, reference_month=month).first()
    return bool(closure and closure.is_closed)


def close_month(closure: MonthlyClosure, summary: str, user_id: int) -> MonthlyClosure:
    closure.is_closed = True
    closure.closed_at = datetime.utcnow()
    closure.summary = summary
    closure.closed_by_id = user_id
    return closure


def reopen_month(closure: MonthlyClosure) -> MonthlyClosure:
    closure.is_closed = False
    closure.closed_at = None
    closure.summary = None
    closure.closed_by_id = None
    return closure

