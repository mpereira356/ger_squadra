from __future__ import annotations

from collections import defaultdict
from datetime import date
from io import BytesIO

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import extract, func

from app.models import Expense, Payment, Player


def dashboard_totals(year: int | None = None):
    payments_query = Payment.query
    expenses_query = Expense.query
    if year:
        payments_query = payments_query.filter(Payment.reference_year == year)
        expenses_query = expenses_query.filter(extract("year", Expense.expense_date) == year)

    received = float(
        payments_query.with_entities(func.coalesce(func.sum(Payment.amount_paid), 0)).scalar() or 0
    )
    expenses = float(
        expenses_query.with_entities(func.coalesce(func.sum(Expense.amount), 0)).scalar() or 0
    )
    late_count = payments_query.filter(Payment.status.in_(["pendente", "atrasado", "parcial"])).count()
    players = Player.query.filter_by(status="ativo").count()
    return {"received": received, "expenses": expenses, "balance": received - expenses, "late_count": late_count, "players": players}


def monthly_chart_data(year: int):
    revenues = defaultdict(float)
    expenses = defaultdict(float)

    for row in Payment.query.filter_by(reference_year=year).all():
        revenues[row.reference_month] += float(row.amount_paid or 0)
    for row in Expense.query.filter(extract("year", Expense.expense_date) == year).all():
        expenses[row.expense_date.month] += float(row.amount or 0)

    labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    return {
        "labels": labels,
        "revenues": [revenues[m] for m in range(1, 13)],
        "expenses": [expenses[m] for m in range(1, 13)],
        "balances": [revenues[m] - expenses[m] for m in range(1, 13)],
    }


def export_payments_excel(payments):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Financeiro"
    sheet.append(["Jogador", "Referencia", "Vencimento", "Status", "Forma", "Valor devido", "Valor pago"])
    for payment in payments:
        sheet.append(
            [
                payment.player.name,
                f"{payment.reference_month:02d}/{payment.reference_year}",
                payment.due_date.strftime("%d/%m/%Y"),
                payment.status,
                payment.payment_method,
                float(payment.amount_due or 0),
                float(payment.amount_paid or 0),
            ]
        )
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


def export_summary_pdf(title: str, lines: list[str]):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 60
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, title)
    y -= 30
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Gerado em {date.today().strftime('%d/%m/%Y')}")
    y -= 30
    for line in lines:
        pdf.drawString(50, y, line[:100])
        y -= 18
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 11)
    pdf.save()
    buffer.seek(0)
    return buffer

