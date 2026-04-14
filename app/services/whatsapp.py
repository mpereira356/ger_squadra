from __future__ import annotations

from urllib.parse import quote

from app.models import ChargeHistory, Payment, Player, TeamSetting


def _settings() -> TeamSetting | None:
    return TeamSetting.query.first()


def billing_message(player: Player, payment: Payment) -> str:
    settings = _settings()
    template = (
        settings.billing_message_template
        if settings and settings.billing_message_template
        else "Ola {nome}, sua mensalidade de {mes}/{ano} esta pendente. Valor: R$ {valor}. PIX: {pix}"
    )
    return template.format(
        nome=player.nickname or player.name,
        mes=f"{payment.reference_month:02d}",
        ano=payment.reference_year,
        valor=f"{float(payment.amount_due or 0):.2f}",
        pix=settings.pix_key if settings else "",
        nomeTime=settings.team_name if settings else "Time",
        vencimento=payment.due_date.strftime("%d/%m/%Y"),
    )


def whatsapp_url(phone: str, message: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if digits and not digits.startswith("55"):
        digits = f"55{digits}"
    return f"https://wa.me/{digits}?text={quote(message)}"


def create_charge_history(player_id: int, payment_id: int | None, message: str, sent_by_id: int) -> ChargeHistory:
    return ChargeHistory(
        player_id=player_id,
        payment_id=payment_id,
        message=message,
        sent_by_id=sent_by_id,
        status="gerado",
    )

