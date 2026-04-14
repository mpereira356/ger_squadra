from __future__ import annotations

from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy import extract

from app.decorators import roles_required
from app.extensions import db
from app.forms import ExpenseCategoryForm, ExpenseForm, PaymentForm
from app.models import Expense, ExpenseCategory, Payment, Player
from app.services.audit import log_action
from app.services.closures import close_month, get_or_create_closure, is_month_closed, reopen_month
from app.services.reports import export_payments_excel
from app.services.whatsapp import billing_message, create_charge_history, whatsapp_url
from app.utils import currency, save_upload


finance_bp = Blueprint("finance", __name__)


@finance_bp.route("/")
@login_required
def index():
    month = request.args.get("mes", type=int) or date.today().month
    year = request.args.get("ano", type=int) or date.today().year
    payments = (
        Payment.query.filter_by(reference_month=month, reference_year=year)
        .order_by(Payment.due_date.asc())
        .all()
    )
    expenses = (
        Expense.query.filter(extract("month", Expense.expense_date) == month, extract("year", Expense.expense_date) == year)
        .order_by(Expense.expense_date.desc())
        .all()
    )
    closure = get_or_create_closure(year, month)
    db.session.commit()
    totals = {
        "received": sum(float(item.amount_paid or 0) for item in payments),
        "expected": sum(float(item.amount_due or 0) for item in payments),
        "expenses": sum(float(item.amount or 0) for item in expenses),
    }
    totals["balance"] = totals["received"] - totals["expenses"]
    return render_template("finance/index.html", payments=payments, expenses=expenses, month=month, year=year, closure=closure, totals=totals, currency=currency)


@finance_bp.route("/pagamentos/novo", methods=["GET", "POST"])
@login_required
def create_payment():
    form = PaymentForm()
    form.player_id.choices = [(p.id, p.name) for p in Player.query.order_by(Player.name.asc()).all()]
    if form.validate_on_submit():
        if is_month_closed(form.reference_year.data, form.reference_month.data):
            abort(403)
        receipt_path = save_upload(form.receipt.data, "receipts")
        payment = Payment(
            player_id=form.player_id.data,
            reference_year=form.reference_year.data,
            reference_month=form.reference_month.data,
            due_date=form.due_date.data,
            amount_due=form.amount_due.data,
            amount_paid=form.amount_paid.data or 0,
            discount=form.discount.data or 0,
            fine=form.fine.data or 0,
            interest=form.interest.data or 0,
            payment_method=form.payment_method.data,
            status=form.status.data,
            paid_at=form.paid_at.data,
            notes=form.notes.data,
            receipt_path=receipt_path,
        )
        db.session.add(payment)
        db.session.flush()
        log_action("create", "payment", payment.id, f"Pagamento para jogador {payment.player_id}")
        db.session.commit()
        flash("Pagamento registrado.", "success")
        return redirect(url_for("finance.index", mes=payment.reference_month, ano=payment.reference_year))
    form.reference_year.data = form.reference_year.data or date.today().year
    form.reference_month.data = form.reference_month.data or date.today().month
    form.due_date.data = form.due_date.data or date.today()
    return render_template("finance/payment_form.html", form=form, title="Novo pagamento")


@finance_bp.route("/despesas/categorias", methods=["GET", "POST"])
@login_required
def categories():
    form = ExpenseCategoryForm()
    if form.validate_on_submit():
        category = ExpenseCategory(name=form.name.data, description=form.description.data)
        db.session.add(category)
        log_action("create", "expense_category", None, form.name.data)
        db.session.commit()
        flash("Categoria criada.", "success")
        return redirect(url_for("finance.categories"))
    categories = ExpenseCategory.query.order_by(ExpenseCategory.name.asc()).all()
    return render_template("finance/categories.html", form=form, categories=categories)


@finance_bp.route("/despesas/nova", methods=["GET", "POST"])
@login_required
def create_expense():
    form = ExpenseForm()
    form.category_id.choices = [(c.id, c.name) for c in ExpenseCategory.query.order_by(ExpenseCategory.name.asc()).all()]
    if form.validate_on_submit():
        if is_month_closed(form.expense_date.data.year, form.expense_date.data.month):
            abort(403)
        receipt_path = save_upload(form.receipt.data, "receipts")
        expense = Expense(
            category_id=form.category_id.data,
            description=form.description.data,
            supplier=form.supplier.data,
            amount=form.amount.data,
            expense_date=form.expense_date.data,
            status=form.status.data,
            recurring=form.recurring.data,
            notes=form.notes.data,
            receipt_path=receipt_path,
        )
        db.session.add(expense)
        db.session.flush()
        log_action("create", "expense", expense.id, expense.description)
        db.session.commit()
        flash("Despesa cadastrada.", "success")
        return redirect(url_for("finance.index", mes=expense.expense_date.month, ano=expense.expense_date.year))
    form.expense_date.data = form.expense_date.data or date.today()
    return render_template("finance/expense_form.html", form=form, title="Nova despesa")


@finance_bp.route("/exportar/excel")
@login_required
def export_excel():
    month = request.args.get("mes", type=int) or date.today().month
    year = request.args.get("ano", type=int) or date.today().year
    payments = Payment.query.filter_by(reference_month=month, reference_year=year).all()
    output = export_payments_excel(payments)
    return send_file(
        output,
        as_attachment=True,
        download_name=f"financeiro_{year}_{month:02d}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@finance_bp.route("/cobranca/<int:payment_id>")
@login_required
def charge_player(payment_id: int):
    payment = Payment.query.get_or_404(payment_id)
    message = billing_message(payment.player, payment)
    history = create_charge_history(payment.player_id, payment.id, message, current_user.id)
    db.session.add(history)
    log_action("charge", "payment", payment.id, "Cobranca individual gerada")
    db.session.commit()
    return redirect(whatsapp_url(payment.player.phone or "", message))


@finance_bp.route("/fechamento/<int:year>/<int:month>", methods=["POST"])
@roles_required("admin", "manager")
def do_close(year: int, month: int):
    closure = get_or_create_closure(year, month)
    payments = Payment.query.filter_by(reference_year=year, reference_month=month).all()
    expenses = Expense.query.filter(extract("year", Expense.expense_date) == year, extract("month", Expense.expense_date) == month).all()
    summary = (
        f"Receitas: {sum(float(p.amount_paid or 0) for p in payments):.2f} | "
        f"Despesas: {sum(float(e.amount or 0) for e in expenses):.2f}"
    )
    close_month(closure, summary, current_user.id)
    log_action("close", "monthly_closure", closure.id, summary)
    db.session.commit()
    flash("Mês fechado.", "success")
    return redirect(url_for("finance.index", mes=month, ano=year))


@finance_bp.route("/reabrir/<int:year>/<int:month>", methods=["POST"])
@roles_required("admin")
def do_reopen(year: int, month: int):
    closure = get_or_create_closure(year, month)
    reopen_month(closure)
    log_action("reopen", "monthly_closure", closure.id, f"{month}/{year}")
    db.session.commit()
    flash("Mês reaberto.", "warning")
    return redirect(url_for("finance.index", mes=month, ano=year))
