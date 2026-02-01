import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-rundaword-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rundaword.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ==================== MODELS ====================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    packages = db.relationship('VocabPackage', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class VocabPackage(db.Model):
    __tablename__ = 'vocab_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    package_name = db.Column(db.String(100), nullable=False)
    package_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    vocabularies = db.relationship('Vocabulary', backref='package', lazy=True, cascade='all, delete-orphan')


class Vocabulary(db.Model):
    __tablename__ = 'vocabularies'
    
    id = db.Column(db.Integer, primary_key=True)
    word_en = db.Column(db.String(150), nullable=False)
    word_vi = db.Column(db.String(255), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('vocab_packages.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== ROUTES ====================

# Home
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# Auth Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email hoặc mật khẩu không đúng!', 'danger')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng!', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username đã được sử dụng!', 'danger')
            return render_template('register.html')
        
        user = User(username=username, email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất!', 'info')
    return redirect(url_for('login'))


# Main Routes
@app.route('/dashboard')
@login_required
def dashboard():
    recent_packages = VocabPackage.query.filter_by(user_id=current_user.id)\
        .order_by(VocabPackage.created_at.desc()).limit(4).all()
    return render_template('index.html', packages=recent_packages)


@app.route('/profile')
@login_required
def profile():
    package_count = VocabPackage.query.filter_by(user_id=current_user.id).count()
    return render_template('profile.html', package_count=package_count)


# Vocab Routes
@app.route('/packages')
@login_required
def packages():
    user_packages = VocabPackage.query.filter_by(user_id=current_user.id)\
        .order_by(VocabPackage.created_at.desc()).all()
    return render_template('packages.html', packages=user_packages)


@app.route('/package/<int:package_id>')
@login_required
def package_detail(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    
    if package.user_id != current_user.id:
        flash('Bạn không có quyền truy cập gói từ này!', 'danger')
        return redirect(url_for('packages'))
    
    return render_template('package_detail.html', package=package)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_package():
    if request.method == 'POST':
        package_name = request.form.get('package_name')
        description = request.form.get('description')
        
        new_package = VocabPackage(
            package_name=package_name,
            package_description=description,
            user_id=current_user.id
        )
        db.session.add(new_package)
        db.session.commit()
        
        flash('Tạo gói từ thành công!', 'success')
        return redirect(url_for('package_detail', package_id=new_package.id))
    
    return render_template('create_package.html')


@app.route('/edit/<int:package_id>', methods=['GET', 'POST'])
@login_required
def edit_package(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    
    if package.user_id != current_user.id:
        flash('Bạn không có quyền chỉnh sửa gói từ này!', 'danger')
        return redirect(url_for('packages'))
    
    if request.method == 'POST':
        package.package_name = request.form.get('package_name')
        package.package_description = request.form.get('description')
        db.session.commit()
        
        flash('Cập nhật gói từ thành công!', 'success')
        return redirect(url_for('package_detail', package_id=package.id))
    
    return render_template('edit_package.html', package=package)


# ==================== MAIN ====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✓ Database initialized!")
    
    print("✓ Starting Flask server...")
    print("✓ Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
