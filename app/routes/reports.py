from __future__ import annotations

from datetime import date

from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from sqlalchemy import extract

from app.models import Expense, Payment, Player
from app.services.reports import export_summary_pdf


reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/")
@login_required
def index():
    year = request.args.get("ano", type=int) or date.today().year
    player_id = request.args.get("jogador", type=int)
    payments_query = Payment.query.filter(Payment.reference_year == year)
    if player_id:
        payments_query = payments_query.filter(Payment.player_id == player_id)
    payments = payments_query.order_by(Payment.reference_month.asc()).all()
    expenses = Expense.query.filter(extract("year", Expense.expense_date) == year).all()
    late_payments = [item for item in payments if item.status in {"pendente", "atrasado", "parcial"}]
    summary = {
        "received": sum(float(item.amount_paid or 0) for item in payments),
        "due": sum(float(item.amount_due or 0) for item in payments),
        "expenses": sum(float(item.amount or 0) for item in expenses),
        "late": len(late_payments),
    }
    summary["balance"] = summary["received"] - summary["expenses"]
    players = Player.query.order_by(Player.name.asc()).all()
    return render_template("reports/index.html", payments=payments, expenses=expenses, summary=summary, players=players, year=year, player_id=player_id)


@reports_bp.route("/pdf")
@login_required
def export_pdf():
    year = request.args.get("ano", type=int) or date.today().year
    payments = Payment.query.filter(Payment.reference_year == year).all()
    lines = [
        f"Receitas recebidas: R$ {sum(float(item.amount_paid or 0) for item in payments):.2f}",
        f"Pagamentos pendentes: {sum(1 for item in payments if item.status != 'pago')}",
        f"Total de jogadores com cobranca: {len({item.player_id for item in payments})}",
    ]
    output = export_summary_pdf(f"Relatorio financeiro {year}", lines)
    return send_file(output, as_attachment=True, download_name=f"relatorio_{year}.pdf", mimetype="application/pdf")

