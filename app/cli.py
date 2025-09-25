import click
from flask import current_app
from flask.cli import with_appcontext
from . import db
from .models import Admin

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Crea las tablas y el admin por defecto."""
    db.create_all()
    click.echo("Tablas creadas correctamente.")

    # Crear admin por defecto
    if not Admin.query.filter_by(username="visionalfa").first():
        admin = Admin(username="visionalfa")
        admin.set_password("098765")
        db.session.add(admin)
        db.session.commit()
        click.echo("Admin 'visionalfa' creado correctamente.")
    else:
        click.echo("El admin 'visionalfa' ya existe.")

# Función para registrar los comandos CLI
def register_commands(app):
    app.cli.add_command(init_db_command)
