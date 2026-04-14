from __future__ import annotations

from datetime import datetime

from flask import Blueprint, render_template

from app.models import Match, TeamSetting


public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    settings = TeamSetting.query.first()
    next_matches = Match.query.filter(Match.starts_at >= datetime.utcnow()).order_by(Match.starts_at.asc()).limit(4).all()
    return render_template("public/home.html", settings=settings, next_matches=next_matches)

