# app.py
from flask import Flask
from config import config


def create_app(config_name='default'):
    app = Flask(__name__)

    # Load config từ class tương ứng
    app.config.from_object(config[config_name])

    # Tạo thư mục upload nếu chưa có
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Khởi tạo các extension (sẽ thêm sau)
    # db = SQLAlchemy(app)
    # migrate = Migrate(app, db)
    # login_manager = LoginManager(app)
    # login_manager.login_view = 'auth.login'

    # Register blueprints
    # from .main import main as main_blueprint
    # app.register_blueprint(main_blueprint)
    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint, url_prefix='/auth')
    # ...

    return app


# Để chạy nhanh trong development
if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)