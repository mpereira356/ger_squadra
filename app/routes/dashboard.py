from __future__ import annotations

from datetime import date

from flask import Blueprint, render_template, request
from flask_login import login_required

from app.models import Expense, Payment
from app.services.reports import dashboard_totals, monthly_chart_data


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    selected_year = request.args.get("ano", type=int) or date.today().year
    totals = dashboard_totals(selected_year)
    latest_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()
    latest_expenses = Expense.query.order_by(Expense.created_at.desc()).limit(5).all()
    chart_data = monthly_chart_data(selected_year)
    return render_template(
        "dashboard/index.html",
        totals=totals,
        latest_payments=latest_payments,
        latest_expenses=latest_expenses,
        chart_data=chart_data,
        selected_year=selected_year,
    )

