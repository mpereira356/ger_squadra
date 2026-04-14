from __future__ import annotations

from flask_login import current_user

from app.extensions import db
from app.models import AuditLog


def log_action(action: str, entity: str, entity_id: str | int | None = None, details: str | None = None) -> None:
    user_id = current_user.id if getattr(current_user, "is_authenticated", False) else None
    db.session.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=str(entity_id) if entity_id is not None else None,
            details=details,
        )
    )

