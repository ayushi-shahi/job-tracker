import bcrypt
from app.extensions import db
from app.models.user import User


def register_user(email: str, password: str) -> User:
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already registered")

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(email: str, password: str) -> User:
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("Invalid email or password")
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        raise ValueError("Invalid email or password")
    return user