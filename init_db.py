from app import create_app, db
from app.models import Admin

app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    print("Tablas creadas correctamente")

    # Crear admin por defecto si no existe
    if not Admin.query.filter_by(username="visionalfa").first():
        admin = Admin(username="visionalfa")
        admin.set_password("098765")
        db.session.add(admin)
        db.session.commit()
        print("Admin 'visionalfa' creado correctamente.")
    else:
        print("El admin 'visionalfa' ya existe.")
