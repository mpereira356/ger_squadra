from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="manager")
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self) -> bool:
        return self.is_active_user


class LoginAttempt(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.String(255))
    success = db.Column(db.Boolean, default=False, nullable=False)


class Player(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    nickname = db.Column(db.String(80))
    phone = db.Column(db.String(30))
    position = db.Column(db.String(50))
    player_type = db.Column(db.String(20), nullable=False, default="mensalista")
    status = db.Column(db.String(20), nullable=False, default="ativo")
    notes = db.Column(db.Text)
    photo_path = db.Column(db.String(255))
    monthly_fee = db.Column(db.Numeric(10, 2), default=0)
    per_game_fee = db.Column(db.Numeric(10, 2), default=0)
    due_day = db.Column(db.Integer, default=5)

    payments = db.relationship("Payment", backref="player", lazy=True, cascade="all, delete-orphan")
    attendances = db.relationship("Attendance", backref="player", lazy=True, cascade="all, delete-orphan")


class Payment(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    reference_year = db.Column(db.Integer, nullable=False, index=True)
    reference_month = db.Column(db.Integer, nullable=False, index=True)
    due_date = db.Column(db.Date, nullable=False)
    paid_at = db.Column(db.DateTime)
    amount_due = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    discount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    fine = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    interest = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    payment_method = db.Column(db.String(30), default="pix")
    status = db.Column(db.String(20), nullable=False, default="pendente", index=True)
    receipt_path = db.Column(db.String(255))
    notes = db.Column(db.Text)


class ExpenseCategory(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))


class Expense(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("expense_category.id"), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    supplier = db.Column(db.String(120))
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    expense_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pendente")
    recurring = db.Column(db.Boolean, default=False, nullable=False)
    receipt_path = db.Column(db.String(255))
    notes = db.Column(db.Text)

    category = db.relationship("ExpenseCategory")


class MonthlyClosure(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference_year = db.Column(db.Integer, nullable=False, index=True)
    reference_month = db.Column(db.Integer, nullable=False, index=True)
    is_closed = db.Column(db.Boolean, default=False, nullable=False)
    closed_at = db.Column(db.DateTime)
    closed_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    summary = db.Column(db.Text)

    closed_by = db.relationship("User")
    __table_args__ = (db.UniqueConstraint("reference_year", "reference_month", name="uq_month_closure"),)


class ChargeHistory(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey("payment.id"))
    channel = db.Column(db.String(20), default="whatsapp", nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    status = db.Column(db.String(20), default="gerado", nullable=False)

    sender = db.relationship("User")
    payment = db.relationship("Payment")


class Match(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    opponent = db.Column(db.String(120))
    location = db.Column(db.String(120))
    starts_at = db.Column(db.DateTime, nullable=False)
    confirmation_deadline = db.Column(db.DateTime)
    game_fee = db.Column(db.Numeric(10, 2), default=0)
    notes = db.Column(db.Text)

    attendances = db.relationship("Attendance", backref="match", lazy=True, cascade="all, delete-orphan")


class Attendance(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pendente")
    is_guest = db.Column(db.Boolean, default=False, nullable=False)
    guest_fee = db.Column(db.Numeric(10, 2), default=0)
    notes = db.Column(db.Text)


class TeamSetting(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(120), nullable=False, default="Amigos da Squadra")
    logo_path = db.Column(db.String(255))
    primary_color = db.Column(db.String(20), default="#0f766e")
    secondary_color = db.Column(db.String(20), default="#f59e0b")
    monthly_fee_default = db.Column(db.Numeric(10, 2), default=65)
    single_match_fee_default = db.Column(db.Numeric(10, 2), default=30)
    pix_key = db.Column(db.String(120))
    admin_phone = db.Column(db.String(30))
    billing_message_template = db.Column(db.Text)
    match_message_template = db.Column(db.Text)
    public_home_text = db.Column(db.Text)


class AuditLog(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    action = db.Column(db.String(120), nullable=False)
    entity = db.Column(db.String(80), nullable=False)
    entity_id = db.Column(db.String(40))
    details = db.Column(db.Text)

    user = db.relationship("User")

