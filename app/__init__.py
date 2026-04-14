from __future__ import annotations

from datetime import datetime
from pathlib import Path

from flask import Flask

from config import Config
from app.extensions import csrf, db, login_manager, migrate
from app.models import ExpenseCategory, Player, TeamSetting, User
from app.utils import currency


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["REPORTS_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["BACKUP_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para continuar."

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.finance import finance_bp
    from app.routes.matches import matches_bp
    from app.routes.players import players_bp
    from app.routes.public import public_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/app")
    app.register_blueprint(players_bp, url_prefix="/app/jogadores")
    app.register_blueprint(finance_bp, url_prefix="/app/financeiro")
    app.register_blueprint(matches_bp, url_prefix="/app/partidas")
    app.register_blueprint(reports_bp, url_prefix="/app/relatorios")
    app.register_blueprint(settings_bp, url_prefix="/app/configuracoes")

    @app.context_processor
    def inject_globals():
        return {
            "now": datetime.utcnow(),
            "team_settings": TeamSetting.query.first(),
            "currency": currency,
        }

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        seed_defaults()
        print("Banco inicializado com sucesso.")

    @app.cli.command("seed")
    def seed_command():
        seed_defaults()
        print("Dados iniciais carregados.")

    with app.app_context():
        db.create_all()
        seed_defaults()

    return app


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


def seed_defaults() -> None:
    from flask import current_app

    if not TeamSetting.query.first():
        db.session.add(
            TeamSetting(
                team_name=current_app.config["DEFAULT_TEAM_NAME"],
                pix_key="time@pix.com",
                admin_phone="5511999999999",
                billing_message_template=(
                    "Olá {nome}, sua cobrança de {nomeTime} venceu em {vencimento}. "
                    "Valor: R$ {valor}. PIX: {pix}"
                ),
                match_message_template="Olá {nome}, obrigado pela presença. Valor avulso: R$ {valor}. PIX: {pix}",
                public_home_text="Gestão moderna para finanças, jogos e presença do time.",
            )
        )

    if not ExpenseCategory.query.count():
        db.session.add_all(
            [
                ExpenseCategory(name="Quadra", description="Locação da quadra"),
                ExpenseCategory(name="Uniforme", description="Camisas e materiais"),
                ExpenseCategory(name="Arbitragem", description="Árbitro e apoio"),
                ExpenseCategory(name="Resenha", description="Confraternização"),
            ]
        )

    if not Player.query.count():
        seed_players = [
            ("Andrey", "11999990001", "mensalista"),
            ("Bruno Lima", "11999990002", "mensalista"),
            ("Cicero", "11999990003", "mensalista"),
            ("Cleiber", "11999990004", "mensalista"),
            ("Eliseu", "11999990005", "mensalista"),
            ("Fabricio Hugo Souza", "11999990006", "mensalista"),
            ("Felipe", "11999990007", "mensalista"),
            ("Fernando", "11999990008", "mensalista"),
            ("Giba", "11999990009", "mensalista"),
            ("Gustavo Sorte", "11999990010", "mensalista"),
            ("Gustavo Hofmann", "11999990011", "mensalista"),
            ("Junior", "11999990012", "mensalista"),
            ("Maceio", "11999990013", "mensalista"),
            ("Marcao", "11999990014", "mensalista"),
            ("Paulinho", "11999990015", "mensalista"),
            ("Renan", "11999990016", "mensalista"),
            ("Rick Goulard", "11999990017", "mensalista"),
            ("Tito", "11999990018", "mensalista"),
            ("Vilson", "11999990019", "mensalista"),
            ("Carlos Alberto", "11988880001", "avulso"),
            ("Marcelo Silva", "11988880002", "avulso"),
            ("Rafael Souza", "11988880003", "avulso"),
            ("Thiago Santos", "11988880004", "avulso"),
            ("Rodrigo Lima", "11988880005", "avulso"),
            ("Andre Costa", "11988880006", "avulso"),
            ("Luiz Fernando", "11988880007", "avulso"),
            ("Paulo Henrique", "11988880008", "avulso"),
            ("Diego Alves", "11988880009", "avulso"),
            ("Bruno Henrique", "11988880010", "avulso"),
        ]
        for name, phone, player_type in seed_players:
            db.session.add(
                Player(
                    name=name,
                    phone=phone,
                    player_type=player_type,
                    status="ativo",
                    monthly_fee=65 if player_type == "mensalista" else 0,
                    per_game_fee=30,
                    due_day=5,
                )
            )

    admin_email = current_app.config["DEFAULT_ADMIN_EMAIL"]
    admin_password = current_app.config["DEFAULT_ADMIN_PASSWORD"]
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            name="Administrador",
            email=admin_email,
            role="admin",
        )
        admin.set_password(admin_password)
        db.session.add(admin)
    else:
        admin.role = "admin"
        admin.set_password(admin_password)

    db.session.commit()
