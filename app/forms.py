from __future__ import annotations

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    DateField,
    DateTimeLocalField,
    DecimalField,
    EmailField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional


class LoginForm(FlaskForm):
    email = StringField("Login", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=1)])
    submit = SubmitField("Entrar")


class UserForm(FlaskForm):
    name = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    email = EmailField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[Optional(), Length(min=6)])
    role = SelectField("Perfil", choices=[("admin", "Administrador"), ("manager", "Gestor")])
    submit = SubmitField("Salvar")


class PlayerForm(FlaskForm):
    name = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    nickname = StringField("Apelido", validators=[Optional(), Length(max=80)])
    phone = StringField("Telefone", validators=[Optional(), Length(max=30)])
    position = StringField("Posicao", validators=[Optional(), Length(max=50)])
    player_type = SelectField("Tipo", choices=[("mensalista", "Mensalista"), ("avulso", "Avulso")])
    status = SelectField("Status", choices=[("ativo", "Ativo"), ("inativo", "Inativo"), ("lesionado", "Lesionado")])
    notes = TextAreaField("Observacoes", validators=[Optional(), Length(max=2000)])
    monthly_fee = DecimalField("Mensalidade", places=2, validators=[Optional()])
    per_game_fee = DecimalField("Taxa por jogo", places=2, validators=[Optional()])
    due_day = IntegerField("Dia de vencimento", validators=[Optional(), NumberRange(min=1, max=28)])
    photo = FileField("Foto", validators=[FileAllowed(["jpg", "jpeg", "png", "webp"])])
    submit = SubmitField("Salvar")


class PaymentForm(FlaskForm):
    player_id = SelectField("Jogador", coerce=int, validators=[DataRequired()])
    reference_year = IntegerField("Ano", validators=[DataRequired()])
    reference_month = IntegerField("Mes", validators=[DataRequired(), NumberRange(min=1, max=12)])
    due_date = DateField("Vencimento", validators=[DataRequired()])
    amount_due = DecimalField("Valor devido", places=2, validators=[DataRequired()])
    amount_paid = DecimalField("Valor pago", places=2, validators=[Optional()])
    discount = DecimalField("Desconto", places=2, validators=[Optional()])
    fine = DecimalField("Multa", places=2, validators=[Optional()])
    interest = DecimalField("Juros", places=2, validators=[Optional()])
    payment_method = SelectField("Forma", choices=[("pix", "PIX"), ("dinheiro", "Dinheiro"), ("cartao", "Cartao"), ("transferencia", "Transferencia")])
    status = SelectField("Status", choices=[("pendente", "Pendente"), ("parcial", "Parcial"), ("pago", "Pago"), ("atrasado", "Atrasado")])
    paid_at = DateTimeLocalField("Pago em", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    notes = TextAreaField("Observacoes", validators=[Optional(), Length(max=2000)])
    receipt = FileField("Comprovante", validators=[FileAllowed(["jpg", "jpeg", "png", "pdf", "webp"])])
    submit = SubmitField("Salvar")


class ExpenseCategoryForm(FlaskForm):
    name = StringField("Categoria", validators=[DataRequired(), Length(max=80)])
    description = StringField("Descricao", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Salvar")


class ExpenseForm(FlaskForm):
    category_id = SelectField("Categoria", coerce=int, validators=[DataRequired()])
    description = StringField("Descricao", validators=[DataRequired(), Length(max=255)])
    supplier = StringField("Fornecedor", validators=[Optional(), Length(max=120)])
    amount = DecimalField("Valor", places=2, validators=[DataRequired()])
    expense_date = DateField("Data", validators=[DataRequired()])
    status = SelectField("Status", choices=[("pendente", "Pendente"), ("pago", "Pago")])
    recurring = BooleanField("Recorrente")
    notes = TextAreaField("Observacoes", validators=[Optional(), Length(max=2000)])
    receipt = FileField("Comprovante", validators=[FileAllowed(["jpg", "jpeg", "png", "pdf", "webp"])])
    submit = SubmitField("Salvar")


class MatchForm(FlaskForm):
    title = StringField("Titulo", validators=[DataRequired(), Length(max=120)])
    opponent = StringField("Adversario", validators=[Optional(), Length(max=120)])
    location = StringField("Local", validators=[Optional(), Length(max=120)])
    starts_at = DateTimeLocalField("Data e hora", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    confirmation_deadline = DateTimeLocalField("Confirmar ate", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    game_fee = DecimalField("Taxa", places=2, validators=[Optional()])
    notes = TextAreaField("Observacoes", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Salvar")


class TeamSettingsForm(FlaskForm):
    team_name = StringField("Nome do time", validators=[DataRequired(), Length(max=120)])
    logo = FileField("Logo", validators=[FileAllowed(["jpg", "jpeg", "png", "webp"])])
    primary_color = StringField("Cor primaria", validators=[DataRequired(), Length(max=20)])
    secondary_color = StringField("Cor secundaria", validators=[DataRequired(), Length(max=20)])
    monthly_fee_default = DecimalField("Mensalidade padrao", places=2, validators=[DataRequired()])
    single_match_fee_default = DecimalField("Valor avulso", places=2, validators=[DataRequired()])
    pix_key = StringField("Chave PIX", validators=[Optional(), Length(max=120)])
    admin_phone = StringField("Telefone admin", validators=[Optional(), Length(max=30)])
    billing_message_template = TextAreaField("Mensagem de cobranca", validators=[Optional(), Length(max=3000)])
    match_message_template = TextAreaField("Mensagem pos-jogo", validators=[Optional(), Length(max=3000)])
    public_home_text = TextAreaField("Texto da home publica", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("Salvar")
