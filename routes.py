# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import db
from models.models import User, VocabPackage, Vocabulary

# Blueprint cho main routes
main_bp = Blueprint('main', __name__)

# Blueprint cho auth routes
auth_bp = Blueprint('auth', __name__)

# Blueprint cho vocab routes
vocab_bp = Blueprint('vocab', __name__)


# ===== MAIN ROUTES =====
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')


@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


# ===== AUTH ROUTES =====
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Email hoặc mật khẩu không đúng!', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # Kiểm tra user đã tồn tại
        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng!', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username đã được sử dụng!', 'danger')
            return render_template('register.html')
        
        # Tạo user mới
        new_user = User(username=username, email=email, password=password, name=name)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất!', 'info')
    return redirect(url_for('auth.login'))


# ===== VOCAB ROUTES =====
@vocab_bp.route('/packages')
@login_required
def packages():
    user_packages = VocabPackage.query.filter_by(user_id=current_user.id).all()
    return render_template('packages.html', packages=user_packages)


@vocab_bp.route('/package/<int:package_id>')
@login_required
def package_detail(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    
    # Kiểm tra quyền truy cập
    if package.user_id != current_user.id:
        flash('Bạn không có quyền truy cập gói từ này!', 'danger')
        return redirect(url_for('vocab.packages'))
    
    return render_template('package_detail.html', package=package)


@vocab_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_package():
    if request.method == 'POST':
        package_name = request.form.get('package_name')
        description = request.form.get('description')
        
        # Tạo package mới
        new_package = VocabPackage(
            package_name=package_name,
            package_description=description,
            user_id=current_user.id
        )
        db.session.add(new_package)
        db.session.commit()
        
        flash('Tạo gói từ thành công!', 'success')
        return redirect(url_for('vocab.package_detail', package_id=new_package.id))
    
    return render_template('create_package.html')


@vocab_bp.route('/edit/<int:package_id>', methods=['GET', 'POST'])
@login_required
def edit_package(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    
    # Kiểm tra quyền
    if package.user_id != current_user.id:
        flash('Bạn không có quyền chỉnh sửa gói từ này!', 'danger')
        return redirect(url_for('vocab.packages'))
    
    if request.method == 'POST':
        package.package_name = request.form.get('package_name')
        package.package_description = request.form.get('description')
        db.session.commit()
        
        flash('Cập nhật gói từ thành công!', 'success')
        return redirect(url_for('vocab.package_detail', package_id=package.id))
    
    return render_template('edit_package.html', package=package)
