# app/models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)  # Tên hiển thị (Hà Anh Nguyễn, v.v.)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: một User có nhiều VocabPackage
    packages = db.relationship('VocabPackage', back_populates='user', cascade="all, delete-orphan")

    def __init__(self, username, email, password, name=None):
        self.username = username
        self.email = email
        self.name = name
        self.set_password(password)

    def set_password(self, password):
        """Hash mật khẩu trước khi lưu"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Kiểm tra mật khẩu khi login"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"


class VocabPackage(db.Model):
    __tablename__ = 'vocab_packages'

    id = db.Column(db.Integer, primary_key=True)
    package_name = db.Column(db.String(100), nullable=False)
    package_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key liên kết với User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship: một Package thuộc về một User
    user = db.relationship('User', back_populates='packages')

    # Relationship: một Package có nhiều Vocabulary
    vocabularies = db.relationship('Vocabulary', back_populates='package', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<VocabPackage '{self.package_name}' (User: {self.user.username})>"


class Vocabulary(db.Model):
    __tablename__ = 'vocabularies'

    id = db.Column(db.Integer, primary_key=True)
    word_en = db.Column(db.String(150), nullable=False, index=True)
    word_vi = db.Column(db.String(255), nullable=False)

    # Foreign key liên kết với VocabPackage
    package_id = db.Column(db.Integer, db.ForeignKey('vocab_packages.id'), nullable=False)

    # Relationship: một từ thuộc về một Package
    package = db.relationship('VocabPackage', back_populates='vocabularies')

    def __repr__(self):
        return f"<Vocabulary '{self.word_en}' → '{self.word_vi}'>"