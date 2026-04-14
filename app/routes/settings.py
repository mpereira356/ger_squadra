from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from app.decorators import roles_required
from app.extensions import db
from app.forms import TeamSettingsForm, UserForm
from app.models import LoginAttempt, TeamSetting, User
from app.services.audit import log_action
from app.services.backup import create_backup
from app.utils import save_upload


settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/", methods=["GET", "POST"])
@roles_required("admin", "manager")
def index():
    settings = TeamSetting.query.first()
    form = TeamSettingsForm(obj=settings)
    if form.validate_on_submit():
        logo_path = save_upload(form.logo.data, "logos")
        form.populate_obj(settings)
        if logo_path:
            settings.logo_path = logo_path
        log_action("update", "settings", settings.id, "Configuracoes do time atualizadas")
        db.session.commit()
        flash("Configurações salvas.", "success")
        return redirect(url_for("settings.index"))

    user_form = UserForm()
    users = User.query.order_by(User.name.asc()).all()
    login_attempts = LoginAttempt.query.order_by(LoginAttempt.created_at.desc()).limit(20).all()
    backups = sorted(Path(current_app.config["BACKUP_FOLDER"]).glob("*.sqlite3"), reverse=True)
    return render_template("settings/index.html", form=form, user_form=user_form, users=users, login_attempts=login_attempts, backups=backups)


@settings_bp.route("/usuarios", methods=["POST"])
@roles_required("admin")
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data.lower().strip(), role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        log_action("create", "user", None, user.email)
        db.session.commit()
        flash("Usuário criado.", "success")
    else:
        flash("Verifique os dados do usuário.", "danger")
    return redirect(url_for("settings.index"))


@settings_bp.route("/backup", methods=["POST"])
@roles_required("admin")
def backup():
    backup_file = create_backup()
    log_action("backup", "database", backup_file.name, "Backup manual")
    db.session.commit()
    flash("Backup criado com sucesso.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/backup/<path:filename>")
@roles_required("admin")
def download_backup(filename: str):
    path = Path(current_app.config["BACKUP_FOLDER"]) / filename
    return send_file(path, as_attachment=True)
