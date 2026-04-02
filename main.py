import os
import csv
import io
import unicodedata
import re
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.sql import func
import random

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


# ==================== HELPERS ====================

def normalize_text(text: str) -> str:
    """
    Normalize Vietnamese text for fuzzy search:
    - Lowercase
    - Strip accents / diacritics (NFD → remove combining chars)
    - Collapse whitespace
    """
    text = text.lower().strip()
    # NFD decomposition then remove combining diacritical marks
    nfd = unicodedata.normalize('NFD', text)
    stripped = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    # Collapse multiple spaces
    return re.sub(r'\s+', ' ', stripped)


def search_packages(q: str, user_id_exclude=None):
    """
    Full search across package names AND owner usernames.
    Matches both accented and unaccented queries.
    Returns public packages sorted by updated_at desc.
    """
    q_norm = normalize_text(q)
    # Fetch all public packages with their owners loaded
    base = VocabPackage.query.filter(VocabPackage.is_public == True)
    if user_id_exclude:
        # still include own packages in search so user can find their own
        pass
    all_pkgs = base.order_by(VocabPackage.updated_at.desc()).all()

    results = []
    for pkg in all_pkgs:
        name_norm = normalize_text(pkg.package_name)
        owner_norm = normalize_text(pkg.user.username) if pkg.user else ''
        if q_norm in name_norm or q_norm in owner_norm:
            results.append(pkg)
    return results[:20]


# ==================== MODELS ====================

# Association table: user bookmarks a public package (no data copy)
user_saved_packages = db.Table(
    'user_saved_packages',
    db.Column('user_id',    db.Integer, db.ForeignKey('users.id'),          nullable=False),
    db.Column('package_id', db.Integer, db.ForeignKey('vocab_packages.id'), nullable=False),
    db.PrimaryKeyConstraint('user_id', 'package_id')
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50),  unique=True, nullable=False)
    name          = db.Column(db.String(100))
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    packages = db.relationship(
        'VocabPackage', backref='user', lazy=True, cascade='all, delete-orphan',
        foreign_keys='VocabPackage.user_id'
    )
    saved_packages = db.relationship(
        'VocabPackage', secondary=user_saved_packages,
        backref=db.backref('saved_by', lazy='dynamic'), lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_saved(self, package):
        return self.saved_packages.filter(
            user_saved_packages.c.package_id == package.id
        ).count() > 0


class VocabPackage(db.Model):
    __tablename__ = 'vocab_packages'
    id                  = db.Column(db.Integer, primary_key=True)
    package_name        = db.Column(db.String(100), nullable=False)
    package_description = db.Column(db.Text)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow)
    user_id             = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public           = db.Column(db.Boolean, default=True)
    vocabularies = db.relationship(
        'Vocabulary', backref='package', lazy=True, cascade='all, delete-orphan'
    )


class Vocabulary(db.Model):
    __tablename__ = 'vocabularies'
    id         = db.Column(db.Integer, primary_key=True)
    word_en    = db.Column(db.String(150), nullable=False)
    word_vi    = db.Column(db.String(255), nullable=False)
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
        if rows and rows[0] and rows[0][0].strip().lower() in [
            'english', 'tiếng anh', 'word_en', 'từ tiếng anh', 'en'
        ]:
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
                    if row[0] and str(row[0]).strip().lower() in [
                        'english', 'tiếng anh', 'word_en', 'từ tiếng anh', 'en'
                    ]:
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
    # Guest → landing page
    return render_template('landing.html')


# Thêm route mới cho trang Explore (public packages cho guest):
@app.route('/explore')
def explore():
    q = request.args.get('q', '').strip()
    active_filter = request.args.get('filter', 'all')
    search_query = None

    if q:
        search_query = q
        public_packages = search_packages(q)
    else:
        public_packages = VocabPackage.query.filter(
            VocabPackage.is_public == True
        ).order_by(VocabPackage.updated_at.desc()).limit(12).all()

    return render_template(
        'explore.html',
        public_packages=public_packages,
        search_query=search_query,
        active_filter=active_filter
    )

@app.route('/dashboard')
@login_required
def dashboard():
    q = request.args.get('q', '').strip()
    search_results = None
    if q:
        search_results = search_packages(q)

    recent_packages = VocabPackage.query \
        .filter_by(user_id=current_user.id) \
        .order_by(VocabPackage.updated_at.desc()) \
        .limit(4).all()

    # Also show saved (bookmarked) packages in "continue learning"
    saved_recent = current_user.saved_packages \
        .order_by(VocabPackage.updated_at.desc()) \
        .limit(4).all()

    public_packages = VocabPackage.query \
        .filter(
            VocabPackage.is_public == True,
            VocabPackage.user_id != current_user.id
        ) \
        .order_by(func.random()) \
        .limit(6).all()

    # Quick quiz: pick from own packages only
    user_packages = VocabPackage.query.filter_by(user_id=current_user.id).all()
    quiz_package = random.choice(user_packages) if user_packages else None
    quiz_words = []
    if quiz_package:
        vocabs = list(quiz_package.vocabularies)
        if len(vocabs) >= 2:
            sample = random.sample(vocabs, min(5, len(vocabs)))
            for v in sample:
                wrong_pool = [x.word_vi for x in vocabs if x.id != v.id]
                wrong = random.sample(wrong_pool, min(3, len(wrong_pool)))
                options = wrong + [v.word_vi]
                random.shuffle(options)
                quiz_words.append({
                    "word": v.word_en,
                    "correct": v.word_vi,
                    "options": options
                })

    return render_template(
        'index.html',
        recent_packages=recent_packages,
        saved_recent=saved_recent,
        public_packages=public_packages,
        quiz_words=quiz_words,
        quiz_package=quiz_package,
        search_results=search_results,
        search_query=q
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        identifier = request.form.get('email', '').strip()
        password   = request.form.get('password', '')
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
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        name     = request.form.get('name', '').strip()
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


@app.route('/profile')
@login_required
def profile():
    package_count = VocabPackage.query.filter_by(user_id=current_user.id).count()
    saved_count   = current_user.saved_packages.count()
    return render_template('profile.html', package_count=package_count, saved_count=saved_count)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        if request.form.get('action') == 'cancel':
            return redirect(url_for('profile'))
        name     = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        existing = User.query.filter_by(username=username).first()
        if existing and existing.id != current_user.id:
            flash('Username đã được sử dụng!', 'danger')
            return render_template('edit_profile.html')
        current_user.name     = name
        current_user.username = username
        db.session.commit()
        flash('Cập nhật hồ sơ thành công!', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html')


@app.route('/packages')
@login_required
def packages():
    """My library: own packages + saved (bookmarked) packages."""
    q = request.args.get('q', '').strip()
    tab = request.args.get('tab', 'mine')  # 'mine' | 'saved'

    if q:
        # Search across all public packages
        pkgs = search_packages(q)
        saved_pkgs = []
        if not pkgs:
            flash('Không tìm thấy gói từ phù hợp.', 'warning')
    else:
        if tab == 'saved':
            pkgs = []
            saved_pkgs = current_user.saved_packages \
                .order_by(VocabPackage.updated_at.desc()).all()
        else:
            pkgs = VocabPackage.query.filter_by(user_id=current_user.id) \
                .order_by(VocabPackage.updated_at.desc()).all()
            saved_pkgs = []

    return render_template(
        'packages.html',
        packages=pkgs,
        saved_packages=saved_pkgs,
        tab=tab,
        search_query=q
    )


@app.route('/package/<int:package_id>')
@login_required
def package_detail(package_id):
    package  = VocabPackage.query.get_or_404(package_id)
    is_owner = (package.user_id == current_user.id)

    # Access control: only owner or public
    if not is_owner and not package.is_public:
        flash('Bạn không có quyền truy cập gói từ này!', 'danger')
        return redirect(url_for('packages'))

    is_saved = current_user.has_saved(package) if not is_owner else False
    return render_template(
        'package_detail.html',
        package=package,
        is_owner=is_owner,
        is_saved=is_saved
    )


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_package():
    if request.method == 'POST':
        package_name = request.form.get('package_name', '').strip()
        description  = request.form.get('description',  '').strip()
        is_public    = request.form.get('is_public') == 'true'

        if not package_name:
            flash('Vui lòng nhập tên gói từ!', 'danger')
            return render_template('create_package.html')

        new_package = VocabPackage(
            package_name=package_name,
            package_description=description,
            user_id=current_user.id,
            is_public=is_public
        )
        db.session.add(new_package)
        db.session.flush()

        file = request.files.get('vocab_file')
        if file and file.filename and allowed_file(file.filename):
            result = parse_vocab_file(file.read(), file.filename)
            if isinstance(result, str):
                flash(f'Lỗi file: {result}', 'warning')
            else:
                for en, vi in result:
                    db.session.add(Vocabulary(word_en=en, word_vi=vi, package_id=new_package.id))

        db.session.commit()
        flash('Tạo gói từ thành công!', 'success')
        return redirect(url_for('package_detail', package_id=new_package.id))

    return render_template('create_package.html')


@app.route('/package/<int:package_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_package(package_id):
    package = VocabPackage.query.get_or_404(package_id)

    if package.user_id != current_user.id:
        flash('Bạn không có quyền chỉnh sửa gói từ này!', 'danger')
        return redirect(url_for('packages'))

    if request.method == 'POST':
        if request.form.get('action') == 'cancel':
            return redirect(url_for('package_detail', package_id=package.id))

        package.package_name        = request.form.get('package_name', '').strip()
        package.package_description = request.form.get('description', '').strip()
        package.is_public           = request.form.get('is_public') == 'true'
        package.updated_at          = datetime.utcnow()

        file = request.files.get('vocab_file')
        if file and file.filename and allowed_file(file.filename):
            result = parse_vocab_file(file.read(), file.filename)
            if isinstance(result, str):
                flash(f'Lỗi file: {result}', 'warning')
            else:
                Vocabulary.query.filter_by(package_id=package.id).delete()
                for en, vi in result:
                    db.session.add(Vocabulary(word_en=en, word_vi=vi, package_id=package.id))
                flash(f'Đã cập nhật {len(result)} từ vựng.', 'info')
        else:
            word_ids = request.form.getlist('word_id[]')
            word_ens = request.form.getlist('word_en[]')
            word_vis = request.form.getlist('word_vi[]')

            for wid, en, vi in zip(word_ids, word_ens, word_vis):
                vocab = Vocabulary.query.get(int(wid))
                if vocab and vocab.package_id == package.id:
                    if en.strip() and vi.strip():
                        vocab.word_en = en.strip()
                        vocab.word_vi = vi.strip()

            existing_ids = set(int(wid) for wid in word_ids if wid)
            for vocab in Vocabulary.query.filter_by(package_id=package.id).all():
                if vocab.id not in existing_ids:
                    db.session.delete(vocab)

            for en, vi in zip(
                request.form.getlist('new_word_en[]'),
                request.form.getlist('new_word_vi[]')
            ):
                if en.strip() and vi.strip():
                    db.session.add(Vocabulary(
                        word_en=en.strip(), word_vi=vi.strip(), package_id=package.id
                    ))

        db.session.commit()
        flash('Cập nhật gói từ thành công!', 'success')
        return redirect(url_for('package_detail', package_id=package.id))

    return render_template('edit_package.html', package=package)


# ── SAVE / UNSAVE (bookmark) ──────────────────────────────────────────────────

@app.route('/package/<int:package_id>/save', methods=['POST'])
@login_required
def save_package(package_id):
    """Bookmark another user's public package — no data is copied."""
    package = VocabPackage.query.get_or_404(package_id)

    if not package.is_public:
        flash('Gói từ này không công khai!', 'danger')
        return redirect(url_for('dashboard'))

    if package.user_id == current_user.id:
        flash('Đây là gói từ của bạn!', 'info')
        return redirect(url_for('package_detail', package_id=package_id))

    if current_user.has_saved(package):
        flash('Bạn đã lưu gói từ này rồi!', 'info')
        return redirect(url_for('package_detail', package_id=package_id))

    current_user.saved_packages.append(package)
    db.session.commit()
    flash(f'Đã lưu "{package.package_name}" vào thư viện!', 'success')
    return redirect(url_for('package_detail', package_id=package_id))


@app.route('/package/<int:package_id>/unsave', methods=['POST'])
@login_required
def unsave_package(package_id):
    """Remove bookmark."""
    package = VocabPackage.query.get_or_404(package_id)
    if current_user.has_saved(package):
        current_user.saved_packages.remove(package)
        db.session.commit()
        flash('Đã xoá khỏi thư viện.', 'info')
    return redirect(url_for('package_detail', package_id=package_id))


# ── LEGACY CLONE REDIRECT (keep URL working) ─────────────────────────────────

@app.route('/package/<int:package_id>/clone', methods=['POST'])
@login_required
def clone_package(package_id):
    """Redirect old clone calls to save."""
    return redirect(url_for('save_package', package_id=package_id), code=307)


# ── DELETE ────────────────────────────────────────────────────────────────────

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


# ── STUDY MODES ───────────────────────────────────────────────────────────────

def _get_study_package(package_id):
    """Shared guard for all study routes."""
    package = VocabPackage.query.get_or_404(package_id)
    is_owner = (package.user_id == current_user.id)
    has_access = is_owner or package.is_public or current_user.has_saved(package)
    if not has_access:
        return None, None
    return package, is_owner


@app.route('/package/<int:package_id>/flashcard')
@login_required
def flashcard(package_id):
    package, _ = _get_study_package(package_id)
    if not package:
        flash('Bạn không có quyền truy cập gói từ này!', 'danger')
        return redirect(url_for('packages'))
    if not package.vocabularies:
        flash('Gói từ này chưa có từ vựng nào!', 'warning')
        return redirect(url_for('package_detail', package_id=package_id))
    return render_template('flashcard.html', package=package)


@app.route('/package/<int:package_id>/quiz')
@login_required
def quiz(package_id):
    package, _ = _get_study_package(package_id)
    if not package:
        flash('Bạn không có quyền truy cập gói từ này!', 'danger')
        return redirect(url_for('packages'))
    if len(package.vocabularies) < 4:
        flash('Cần ít nhất 4 từ vựng để làm trắc nghiệm!', 'warning')
        return redirect(url_for('package_detail', package_id=package_id))
    return render_template('quiz.html', package=package)


@app.route('/package/<int:package_id>/test')
@login_required
def test_mode(package_id):
    package, _ = _get_study_package(package_id)
    if not package:
        flash('Bạn không có quyền truy cập gói từ này!', 'danger')
        return redirect(url_for('packages'))
    if not package.vocabularies:
        flash('Gói từ này chưa có từ vựng nào!', 'warning')
        return redirect(url_for('package_detail', package_id=package_id))
    return render_template('test_mode.html', package=package)


@app.route('/package/<int:package_id>/match')
@login_required
def match_mode(package_id):
    package, _ = _get_study_package(package_id)
    if not package:
        flash('Bạn không có quyền truy cập gói từ này!', 'danger')
        return redirect(url_for('packages'))
    if len(package.vocabularies) < 4:
        flash('Cần ít nhất 4 từ vựng để chơi ghép thẻ!', 'warning')
        return redirect(url_for('package_detail', package_id=package_id))
    return render_template('match_mode.html', package=package)


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