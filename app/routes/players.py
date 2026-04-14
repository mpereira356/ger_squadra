from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.forms import PlayerForm
from app.models import Player
from app.services.audit import log_action
from app.utils import save_upload


players_bp = Blueprint("players", __name__)


@players_bp.route("/")
@login_required
def index():
    search = request.args.get("busca", "").strip()
    query = Player.query.order_by(Player.name.asc())
    if search:
        query = query.filter(Player.name.ilike(f"%{search}%"))
    players = query.all()
    return render_template("players/index.html", players=players, search=search)


@players_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create():
    form = PlayerForm()
    if form.validate_on_submit():
        photo_path = save_upload(form.photo.data, "players")
        player = Player(
            name=form.name.data,
            nickname=form.nickname.data,
            phone=form.phone.data,
            position=form.position.data,
            player_type=form.player_type.data,
            status=form.status.data,
            notes=form.notes.data,
            photo_path=photo_path,
            monthly_fee=form.monthly_fee.data or 0,
            per_game_fee=form.per_game_fee.data or 0,
            due_day=form.due_day.data or 5,
        )
        db.session.add(player)
        db.session.flush()
        log_action("create", "player", player.id, f"Jogador {player.name} cadastrado")
        db.session.commit()
        flash("Jogador cadastrado.", "success")
        return redirect(url_for("players.index"))
    return render_template("players/form.html", form=form, title="Novo jogador")


@players_bp.route("/<int:player_id>")
@login_required
def detail(player_id: int):
    player = Player.query.get_or_404(player_id)
    return render_template("players/detail.html", player=player)


@players_bp.route("/<int:player_id>/editar", methods=["GET", "POST"])
@login_required
def edit(player_id: int):
    player = Player.query.get_or_404(player_id)
    form = PlayerForm(obj=player)
    if form.validate_on_submit():
        photo_path = save_upload(form.photo.data, "players")
        form.populate_obj(player)
        if photo_path:
            player.photo_path = photo_path
        log_action("update", "player", player.id, f"Jogador {player.name} atualizado")
        db.session.commit()
        flash("Jogador atualizado.", "success")
        return redirect(url_for("players.detail", player_id=player.id))
    return render_template("players/form.html", form=form, title=f"Editar {player.name}")
