from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

# Extensiones
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # Configuración
    from .config import Config
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from .cli import register_commands
    register_commands(app)

    # Registrar Blueprints
    from .routes import bp
    app.register_blueprint(bp)

    return app
