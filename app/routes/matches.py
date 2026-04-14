from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.forms import MatchForm
from app.models import Attendance, Match, Player
from app.services.audit import log_action


matches_bp = Blueprint("matches", __name__)


@matches_bp.route("/")
@login_required
def index():
    matches = Match.query.order_by(Match.starts_at.desc()).all()
    players = Player.query.filter_by(status="ativo").order_by(Player.name.asc()).all()
    return render_template("matches/index.html", matches=matches, players=players)


@matches_bp.route("/nova", methods=["GET", "POST"])
@login_required
def create():
    form = MatchForm()
    if form.validate_on_submit():
        match = Match(
            title=form.title.data,
            opponent=form.opponent.data,
            location=form.location.data,
            starts_at=form.starts_at.data,
            confirmation_deadline=form.confirmation_deadline.data,
            game_fee=form.game_fee.data or 0,
            notes=form.notes.data,
        )
        db.session.add(match)
        db.session.flush()
        log_action("create", "match", match.id, match.title)
        db.session.commit()
        flash("Partida cadastrada.", "success")
        return redirect(url_for("matches.index"))
    return render_template("matches/form.html", form=form, title="Nova partida")


@matches_bp.route("/<int:match_id>")
@login_required
def detail(match_id: int):
    match = Match.query.get_or_404(match_id)
    players = Player.query.filter_by(status="ativo").order_by(Player.name.asc()).all()
    attendance_map = {item.player_id: item for item in match.attendances}
    return render_template("matches/detail.html", match=match, players=players, attendance_map=attendance_map)


@matches_bp.route("/<int:match_id>/presenca", methods=["POST"])
@login_required
def save_attendance(match_id: int):
    match = Match.query.get_or_404(match_id)
    for player in Player.query.filter_by(status="ativo").all():
        status = request.form.get(f"player_{player.id}")
        if not status:
            continue
        attendance = Attendance.query.filter_by(match_id=match.id, player_id=player.id).first()
        if not attendance:
            attendance = Attendance(match_id=match.id, player_id=player.id)
            db.session.add(attendance)
        attendance.status = status
        attendance.guest_fee = match.game_fee if player.player_type == "avulso" else 0
    log_action("attendance", "match", match.id, "Lista de presenca atualizada")
    db.session.commit()
    flash("Presença atualizada.", "success")
    return redirect(url_for("matches.detail", match_id=match.id))

