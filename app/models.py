from app import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    provincia = db.Column(db.String(50), nullable=False)
    cedula = db.Column(db.String(20))
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(128), nullable=False)