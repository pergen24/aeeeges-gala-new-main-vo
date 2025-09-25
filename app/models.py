from datetime import datetime
from . import db
#from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import generate_password_hash, check_password_hash

class TicketPurchase(db.Model):
    __tablename__ = 'ticket_purchases'
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.String(50), nullable=False)   # e.g., VIP, GENERAL
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  # pending, uploaded, approved
    receipt_filename1 = db.Column(db.String(255))  # path to uploaded receipt
    receipt_filename2 = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ticket_type": self.ticket_type,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "phone": self.phone,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "receipt_filename1": self.receipt_filename1,
            "receipt_filename2": self.receipt_filename2
        }


# --------------------------
# Tabla de administradores
# --------------------------
class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)  # 512 para scrypt u otros hashes largos

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)






#class Admin(db.Model):
#    __tablename__ = 'admins'
#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(50), unique=True, nullable=False)
#    password_hash = db.Column(db.String(512), nullable=False)

#    def set_password(self, password):
#        self.password_hash = generate_password_hash(password)

#    def check_password(self, password):
#        return check_password_hash(self.password_hash, password)
