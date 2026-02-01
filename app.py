# app.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config

# Khởi tạo extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load config từ class tương ứng
    app.config.from_object(config[config_name])

    # Tạo thư mục upload nếu chưa có
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Khởi tạo các extension
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import models và routes trong app context
    with app.app_context():
        from models import models
        
        @login_manager.user_loader
        def load_user(user_id):
            return models.User.query.get(int(user_id))

        # Register blueprints
        from routes import main_bp, auth_bp, vocab_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(vocab_bp, url_prefix='/vocab')

    return app


# Để chạy nhanh trong development
if __name__ == '__main__':
    app = create_app('development')
    
    # Tạo database nếu chưa có
    with app.app_context():
        db.create_all()
        print("✓ Database initialized!")
    
    print("✓ Starting Flask server...")
    print("✓ Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
