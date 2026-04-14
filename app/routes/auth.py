from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm
from app.models import LoginAttempt, User
from app.services.audit import log_action


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        success = bool(user and user.check_password(form.password.data))
        attempt = LoginAttempt(
            email=form.email.data.lower().strip(),
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
            user_agent=(request.user_agent.string or "")[:255],
            success=success,
        )
        db.session.add(attempt)

        if success:
            login_user(user)
            user.last_login_at = datetime.utcnow()
            log_action("login", "user", user.id, "Login realizado com sucesso")
            db.session.commit()
            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("dashboard.index"))

        db.session.commit()
        flash("Credenciais inválidas.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    log_action("logout", "user", current_user.id, "Logout realizado")
    db.session.commit()
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("auth.login"))

