# models/models.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# db sẽ được import khi cần
db = None

def init_db(database):
    """Khởi tạo db reference"""
    global db
    db = database

class User(UserMixin):
    """User model base class"""
    
    def set_password(self, password):
        """Hash mật khẩu trước khi lưu"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Kiểm tra mật khẩu khi login"""
        return check_password_hash(self.password_hash, password)
