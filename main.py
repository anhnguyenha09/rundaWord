import os
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-rundaword-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rundaword.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_vocab_file(file_content, filename):
    words = []
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'csv':
        try:
            text = file_content.decode('utf-8-sig')
        except UnicodeDecodeError:
            text = file_content.decode('latin-1')
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        start = 0
        if rows and rows[0] and rows[0][0].strip().lower() in ['english', 'tiếng anh', 'word_en', 'từ tiếng anh', 'en']:
            start = 1
        for row in rows[start:]:
            if len(row) >= 2:
                en, vi = row[0].strip(), row[1].strip()
                if en and vi:
                    words.append((en, vi))
    elif ext in ('xlsx', 'xls'):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True)
            ws = wb.active
            first = True
            for row in ws.iter_rows(values_only=True):
                if first:
                    first = False
                    if row[0] and str(row[0]).strip().lower() in ['english', 'tiếng anh', 'word_en', 'từ tiếng anh', 'en']:
                        continue
                if row[0] and row[1]:
                    en, vi = str(row[0]).strip(), str(row[1]).strip()
                    if en and vi:
                        words.append((en, vi))
        except Exception as e:
            return f"Lỗi đọc file Excel: {str(e)}"
    if not words:
        return "File không có dữ liệu hợp lệ"
    return words


# ==================== ROUTES ====================
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        identifier = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Email/username hoặc mật khẩu không đúng!', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        name = request.form.get('name', '').strip()
        if password != confirm:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
            return render_template('register.html')
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
        flash('Đăng ký thành công!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    recent_packages = VocabPackage.query.filter_by(user_id=current_user.id)\
        .order_by(VocabPackage.updated_at.desc()).limit(4).all()
    return render_template('index.html', packages=recent_packages)


@app.route('/profile')
@login_required
def profile():
    package_count = VocabPackage.query.filter_by(user_id=current_user.id).count()
    return render_template('profile.html', package_count=package_count)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        if request.form.get('action') == 'cancel':
            return redirect(url_for('profile'))
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        existing = User.query.filter_by(username=username).first()
        if existing and existing.id != current_user.id:
            flash('Username đã được sử dụng!', 'danger')
            return render_template('edit_profile.html')
        current_user.name = name
        current_user.username = username
        db.session.commit()
        flash('Cập nhật hồ sơ thành công!', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html')


@app.route('/packages')
@login_required
def packages():
    user_packages = VocabPackage.query.filter_by(user_id=current_user.id)\
        .order_by(VocabPackage.updated_at.desc()).all()
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
        package_name = request.form.get('package_name', '').strip()
        description = request.form.get('description', '').strip()
        if not package_name:
            flash('Vui lòng nhập tên gói từ!', 'danger')
            return render_template('create_package.html')
        new_package = VocabPackage(
            package_name=package_name,
            package_description=description,
            user_id=current_user.id
        )
        db.session.add(new_package)
        db.session.flush()

        file = request.files.get('vocab_file')
        imported_count = 0
        if file and file.filename and allowed_file(file.filename):
            result = parse_vocab_file(file.read(), file.filename)
            if isinstance(result, str):
                flash(f'Lỗi file: {result}', 'warning')
            else:
                for en, vi in result:
                    db.session.add(Vocabulary(word_en=en, word_vi=vi, package_id=new_package.id))
                imported_count = len(result)

        db.session.commit()
        flash(f'Tạo gói từ thành công!' + (f' Đã import {imported_count} từ.' if imported_count else ''), 'success')
        return redirect(url_for('package_detail', package_id=new_package.id))
    return render_template('create_package.html')


@app.route('/edit/<int:package_id>', methods=['GET', 'POST'])
@login_required
def edit_package(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    if package.user_id != current_user.id:
        flash('Bạn không có quyền!', 'danger')
        return redirect(url_for('packages'))

    if request.method == 'POST':
        if request.form.get('action') == 'cancel':
            return redirect(url_for('package_detail', package_id=package_id))

        package_name = request.form.get('package_name', '').strip()
        if not package_name:
            flash('Vui lòng nhập tên gói từ!', 'danger')
            return render_template('edit_package.html', package=package)

        package.package_name = package_name
        package.package_description = request.form.get('description', '').strip()
        package.updated_at = datetime.utcnow()

        # File upload replaces all words
        file = request.files.get('vocab_file')
        if file and file.filename and allowed_file(file.filename):
            result = parse_vocab_file(file.read(), file.filename)
            if isinstance(result, str):
                flash(f'Lỗi file: {result}', 'warning')
            else:
                Vocabulary.query.filter_by(package_id=package.id).delete()
                for en, vi in result:
                    db.session.add(Vocabulary(word_en=en, word_vi=vi, package_id=package.id))
                flash(f'Đã cập nhật {len(result)} từ vựng từ file.', 'info')
        else:
            # Inline word edits
            word_ids = request.form.getlist('word_id[]')
            word_ens = request.form.getlist('word_en[]')
            word_vis = request.form.getlist('word_vi[]')
            for wid, en, vi in zip(word_ids, word_ens, word_vis):
                vocab = Vocabulary.query.get(int(wid))
                if vocab and vocab.package_id == package.id and en.strip() and vi.strip():
                    vocab.word_en = en.strip()
                    vocab.word_vi = vi.strip()

            # New words added inline
            new_ens = request.form.getlist('new_word_en[]')
            new_vis = request.form.getlist('new_word_vi[]')
            for en, vi in zip(new_ens, new_vis):
                if en.strip() and vi.strip():
                    db.session.add(Vocabulary(word_en=en.strip(), word_vi=vi.strip(), package_id=package.id))

        db.session.commit()
        flash('Cập nhật gói từ thành công!', 'success')
        return redirect(url_for('package_detail', package_id=package.id))

    return render_template('edit_package.html', package=package)


@app.route('/delete_package/<int:package_id>', methods=['POST'])
@login_required
def delete_package(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    if package.user_id != current_user.id:
        return redirect(url_for('packages'))
    db.session.delete(package)
    db.session.commit()
    flash(f'Đã xóa gói từ "{package.package_name}".', 'success')
    return redirect(url_for('packages'))


@app.route('/word/<int:word_id>/delete', methods=['POST'])
@login_required
def delete_word(word_id):
    vocab = Vocabulary.query.get_or_404(word_id)
    if vocab.package.user_id != current_user.id:
        return redirect(url_for('packages'))
    package_id = vocab.package_id
    db.session.delete(vocab)
    db.session.commit()
    return redirect(url_for('edit_package', package_id=package_id))


@app.route('/package/<int:package_id>/flashcard')
@login_required
def flashcard(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    if package.user_id != current_user.id:
        return redirect(url_for('packages'))
    if not package.vocabularies:
        flash('Gói từ này chưa có từ vựng nào!', 'warning')
        return redirect(url_for('package_detail', package_id=package_id))
    package.updated_at = datetime.utcnow()
    db.session.commit()
    return render_template('flashcard.html', package=package)


@app.route('/package/<int:package_id>/quiz')
@login_required
def quiz(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    if package.user_id != current_user.id:
        return redirect(url_for('packages'))
    if len(package.vocabularies) < 4:
        flash('Cần ít nhất 4 từ vựng để làm trắc nghiệm!', 'warning')
        return redirect(url_for('package_detail', package_id=package_id))
    package.updated_at = datetime.utcnow()
    db.session.commit()
    return render_template('quiz.html', package=package)


@app.route('/download_template')
@login_required
def download_template():
    content = "Tiếng Anh,Tiếng Việt\napple,quả táo\nbook,quyển sách\ncar,xe hơi\n"
    return send_file(
        io.BytesIO(content.encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='template_tu_vung.csv'
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✓ Database initialized!")
    print("Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)