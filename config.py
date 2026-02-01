# config.py
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Cấu hình cơ bản chung cho tất cả các môi trường"""

    # Tên ứng dụng
    APP_NAME = "RundaWord"

    # Secret key để bảo mật session, csrf, jwt, v.v. → NÊN ĐẶT GIÁ TRỊ MẠNH, KHÔNG COMMIT LÊN GIT
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-rundaword-2025-change-me-please'

    # Database (SQLite mặc định cho dev, dễ chuyển sang PostgreSQL/MySQL sau)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'rundaword.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Thời gian session tồn tại (ví dụ: 7 ngày)
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Folder upload file Excel (gói từ vựng)
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Giới hạn upload 16MB

    # Ngôn ngữ mặc định
    BABEL_DEFAULT_LOCALE = 'vi'

    # Các thiết lập bảo mật khác (tùy chọn bật khi production)
    SESSION_COOKIE_SECURE = False  # Đổi thành True khi dùng HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Email server (nếu sau này cần gửi mail xác thực, reset password)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('RundaWord', os.environ.get('MAIL_USERNAME'))

    #cơ sở dữ liệu
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'rundaword.db')


class DevelopmentConfig(Config):
    """Cấu hình cho môi trường phát triển (localhost)"""
    DEBUG = True
    ENV = 'development'

    # Database dev dùng SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'rundaword_dev.db')

    # Tắt bảo mật cookie để dễ debug
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Cấu hình cho unit test"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False  # Tắt CSRF khi test form (tùy trường hợp)

    # Database test dùng SQLite in-memory hoặc file riêng
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # hoặc 'sqlite:///test.db'

    # Folder upload tạm cho test
    UPLOAD_FOLDER = os.path.join(basedir, 'test_uploads')


class ProductionConfig(Config):
    """Cấu hình cho production (deploy lên server thật)"""
    DEBUG = False
    ENV = 'production'

    # Bật các thiết lập bảo mật
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)

    # Nên dùng PostgreSQL hoặc MySQL trên production
    # Ví dụ: postgresql://user:pass@host:5432/dbname
    # Hoặc dùng biến môi trường DATABASE_URL từ hosting (Render, Railway, Heroku, v.v.)

    # Buộc dùng HTTPS (nếu server có proxy như nginx)
    PREFERRED_URL_SCHEME = 'https'


# Mapping để dễ chọn config
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    # Mặc định là development nếu không chỉ định
    'default': DevelopmentConfig
}