from functools import wraps
from flask import request, Response
from .models import Admin
from . import db

# Decorador para proteger rutas de admin usando la tabla Admin
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return Response(
                "Acceso denegado", 401,
                {"WWW-Authenticate": 'Basic realm="Login Required"'}
            )

        # Buscar usuario en la base de datos
        admin = Admin.query.filter_by(username=auth.username).first()
        if not admin or not admin.check_password(auth.password):
            return Response(
                "Acceso denegado", 401,
                {"WWW-Authenticate": 'Basic realm="Login Required"'}
            )

        # Usuario autenticado correctamente
        return f(*args, **kwargs)

    return decorated
