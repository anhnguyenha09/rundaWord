import os
import io
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.sql import func
import random

from services.file_service import allowed_file, parse_vocab_file
from services.package_service import search_packages
from services.quiz_service import build_quiz_words
from services.stats_service import learner_counts_for_packages
from services.study_service import get_study_package
from services.text_service import normalize_text
from services.topic_service import ensure_topic_catalog, get_available_topics, get_topics_for_user

load_dotenv()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY']                = os.environ.get('SECRET_KEY') or 'dev-secret-key-rundaword-2025'
app.config['SQLALCHEMY_DATABASE_URI']   = 'sqlite:///' + os.path.join(basedir, 'rundaword.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER']             = os.path.join(basedir, 'uploads')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['MAX_CONTENT_LENGTH']        = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

ROLE_USER  = 0
ROLE_ADMIN = 1
PACKAGE_TOPICS = (
    'Beginner English',
    'Education & Learning',
    'Work & Career',
    'Business & Management',
    'Technology & Digital Life',
    'Environment & Sustainability',
    'Health & Lifestyle',
    'Communication & Social Skills',
    'Travel & Cultural Experience',
    'Society & Social Issues',
    'Economics & Finance',
    'Law & Government',
    'Innovation & Entrepreneurship',
    'IELTS Common Topics',
    'Others',
)

db           = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != ROLE_ADMIN:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ==================== MODELS ====================

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
    role          = db.Column(db.Integer, default=ROLE_USER, nullable=False)
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

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN


class VocabPackage(db.Model):
    __tablename__ = 'vocab_packages'
    id                  = db.Column(db.Integer, primary_key=True)
    package_name        = db.Column(db.String(100), nullable=False)
    package_description = db.Column(db.Text)
    topic               = db.Column(db.String(80))          # NEW: topic/category field
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


class TopicCatalog(db.Model):
    __tablename__ = 'topic_catalog'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))





# ==================== ROUTES ====================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('guest_home'))


# ──────────────────────────────────────────────
# GUEST ROUTES
# ──────────────────────────────────────────────

@app.route('/home')
def guest_home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    public_packages = VocabPackage.query \
        .filter(VocabPackage.is_public == True) \
        .order_by(func.random()) \
        .limit(12).all()
    return render_template('landing.html', public_packages=public_packages)


@app.route('/explore')
def explore():
    """
    Public explore page — accessible to both guests and logged-in users.
    Shows all public packages with search and topic filtering.
    """
    q            = request.args.get('q', '').strip()
    topic_filter = request.args.get('topic', '').strip()
    available_topics = get_available_topics(TopicCatalog)
    if topic_filter and topic_filter not in available_topics:
        topic_filter = ''

    # Base query: all public packages
    pkg_query = VocabPackage.query.filter(VocabPackage.is_public == True)

    # Apply topic filter
    if topic_filter:
        pkg_query = pkg_query.filter(VocabPackage.topic == topic_filter)

    # Apply text search (name, author, description)
    if q:
        public_packages = search_packages(VocabPackage, q)
        # Re-apply topic filter on search results if needed
        if topic_filter:
            public_packages = [p for p in public_packages if p.topic == topic_filter]
    else:
        public_packages = pkg_query.order_by(VocabPackage.updated_at.desc()).all()

    return render_template(
        'explore.html',
        public_packages=public_packages,
        search_query=q,
        topic_filter=topic_filter,
        available_topics=available_topics,
    )


# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────

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
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
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
        user = User(username=username, email=email, name=name, role=ROLE_USER)
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
    return redirect(url_for('guest_home'))


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    q            = request.args.get('q', '').strip()
    topic_filter = request.args.get('topic', '').strip()
    available_topics = get_topics_for_user(TopicCatalog, current_user.id)
    if topic_filter and topic_filter not in available_topics:
        topic_filter = ''
    search_results = None

    if q or topic_filter:
        # Search public packages + user's own packages
        if q:
            results = search_packages(VocabPackage, q, include_private_for_user=current_user.id)
        else:
            results = VocabPackage.query.filter(
                (VocabPackage.is_public == True) |
                (VocabPackage.user_id == current_user.id)
            ).order_by(VocabPackage.updated_at.desc()).all()

        # Apply topic filter on top
        if topic_filter:
            results = [p for p in results if (p.topic or '') == topic_filter]

        search_results = results

    recent_packages = VocabPackage.query \
        .filter_by(user_id=current_user.id) \
        .order_by(VocabPackage.updated_at.desc()) \
        .limit(4).all()

    saved_recent = current_user.saved_packages \
        .order_by(VocabPackage.updated_at.desc()) \
        .limit(4).all()

    public_packages = VocabPackage.query \
        .filter(VocabPackage.is_public == True, VocabPackage.user_id != current_user.id) \
        .order_by(func.random()) \
        .limit(6).all()

    # Build 3-question quick quiz
    user_packages = VocabPackage.query.filter_by(user_id=current_user.id).all()
    quiz_package  = random.choice(user_packages) if user_packages else None
    quiz_words = build_quiz_words(list(quiz_package.vocabularies)) if quiz_package else []

    return render_template(
        'index.html',
        recent_packages=recent_packages,
        saved_recent=saved_recent,
        public_packages=public_packages,
        quiz_words=quiz_words,
        quiz_package=quiz_package,
        search_results=search_results,
        search_query=q,
        topic_filter=topic_filter,
        available_topics=available_topics,
    )


# ──────────────────────────────────────────────
# PROFILE
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
# PACKAGES (library)
# ──────────────────────────────────────────────

@app.route('/packages')
@login_required
def packages():
    q   = request.args.get('q', '').strip()
    tab = request.args.get('tab', 'mine')

    if q:
        pkgs = search_packages(VocabPackage, q, include_private_for_user=current_user.id)
        saved_pkgs = []
        if not pkgs:
            flash('Không tìm thấy gói từ phù hợp.', 'warning')
    else:
        if tab == 'saved':
            pkgs       = []
            saved_pkgs = current_user.saved_packages \
                .order_by(VocabPackage.updated_at.desc()).all()
        else:
            pkgs = VocabPackage.query.filter_by(user_id=current_user.id) \
                .order_by(VocabPackage.updated_at.desc()).all()
            saved_pkgs = []

    all_visible_pkgs = pkgs + saved_pkgs
    learner_counts = learner_counts_for_packages(
        db, user_saved_packages, func, list({p.id for p in all_visible_pkgs})
    )

    return render_template(
        'packages.html',
        packages=pkgs, saved_packages=saved_pkgs,
        tab=tab, search_query=q,
        learner_counts=learner_counts
    )


@app.route('/package/<int:package_id>')
@login_required
def package_detail(package_id):
    package  = VocabPackage.query.get_or_404(package_id)
    is_owner = (package.user_id == current_user.id)
    if not is_owner and not package.is_public and not current_user.is_admin:
        flash('Bạn không có quyền truy cập gói từ này!', 'danger')
        return redirect(url_for('packages'))
    is_saved = current_user.has_saved(package) if not is_owner else False
    return render_template(
        'package_detail.html', package=package, is_owner=is_owner, is_saved=is_saved
    )


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_package():
    available_topics = get_available_topics(TopicCatalog)
    if request.method == 'POST':
        action = (request.form.getlist('action') or ['preview'])[-1]
        if action == 'discard':
            flash('Đã hủy tạo gói từ.', 'info')
            return redirect(url_for('packages'))

        package_name = request.form.get('package_name', '').strip()
        description  = request.form.get('description',  '').strip()
        topic        = request.form.get('topic', '').strip()
        is_public    = request.form.get('is_public') == 'true'

        if not package_name:
            flash('Vui lòng nhập tên gói từ!', 'danger')
            return render_template('create_package.html', available_topics=available_topics)

        if topic and topic not in available_topics:
            topic = None

        file = request.files.get('vocab_file')
        if action == 'preview' and file and file.filename and allowed_file(file.filename, ALLOWED_EXTENSIONS):
            result = parse_vocab_file(file.read(), file.filename)
            if isinstance(result, str):
                flash(f'Lỗi file: {result}', 'warning')
                return render_template('create_package.html', available_topics=available_topics)

            return render_template(
                'create_package_review.html',
                package_name=package_name,
                description=description,
                topic=topic or '',
                is_public=is_public,
                available_topics=available_topics,
                words=result
            )

        # Create directly (without review) if no valid file is uploaded.
        words = []
        if action == 'create_final':
            word_ens = request.form.getlist('word_en[]')
            word_vis = request.form.getlist('word_vi[]')
            for en, vi in zip(word_ens, word_vis):
                en, vi = en.strip(), vi.strip()
                if en and vi:
                    words.append((en, vi))

        new_package = VocabPackage(
            package_name=package_name,
            package_description=description,
            topic=topic or None,
            user_id=current_user.id,
            is_public=is_public
        )
        db.session.add(new_package)
        db.session.flush()

        for en, vi in words:
            db.session.add(Vocabulary(word_en=en, word_vi=vi, package_id=new_package.id))

        db.session.commit()
        flash('Tạo gói từ thành công!', 'success')
        return redirect(url_for('package_detail', package_id=new_package.id))

    return render_template('create_package.html', available_topics=available_topics)


@app.route('/package/<int:package_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_package(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    available_topics = get_topics_for_user(TopicCatalog, current_user.id)
    if package.topic and package.topic not in available_topics:
        available_topics = sorted(set(available_topics + [package.topic]))

    if package.user_id != current_user.id and not current_user.is_admin:
        flash('Bạn không có quyền chỉnh sửa gói từ này!', 'danger')
        return redirect(url_for('packages'))

    if request.method == 'POST':
        if request.form.get('action') == 'cancel':
            return redirect(url_for('package_detail', package_id=package.id))

        package.package_name        = request.form.get('package_name', '').strip()
        package.package_description = request.form.get('description', '').strip()
        selected_topic              = request.form.get('topic', '').strip()
        package.topic               = (
            selected_topic if selected_topic and selected_topic in available_topics else None
        )
        package.is_public           = request.form.get('is_public') == 'true'
        package.updated_at          = datetime.utcnow()

        file = request.files.get('vocab_file')
        if file and file.filename and allowed_file(file.filename, ALLOWED_EXTENSIONS):
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

    return render_template(
        'edit_package.html',
        package=package,
        available_topics=available_topics
    )


@app.route('/package/<int:package_id>/save', methods=['POST'])
@login_required
def save_package(package_id):
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
    package = VocabPackage.query.get_or_404(package_id)
    if current_user.has_saved(package):
        current_user.saved_packages.remove(package)
        db.session.commit()
        flash('Đã xoá khỏi thư viện.', 'info')
    return redirect(url_for('package_detail', package_id=package_id))


@app.route('/package/<int:package_id>/clone', methods=['POST'])
@login_required
def clone_package(package_id):
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


@app.route('/delete_package/<int:package_id>', methods=['POST'])
@login_required
def delete_package(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    if package.user_id != current_user.id and not current_user.is_admin:
        flash('Không có quyền xóa gói từ này!', 'danger')
        return redirect(url_for('packages'))
    db.session.delete(package)
    db.session.commit()
    flash(f'Đã xóa gói từ "{package.package_name}".', 'success')
    if current_user.is_admin and request.referrer and '/admin' in request.referrer:
        return redirect(url_for('admin_packages'))
    return redirect(url_for('packages'))


@app.route('/word/<int:word_id>/delete', methods=['POST'])
@login_required
def delete_word(word_id):
    vocab = Vocabulary.query.get_or_404(word_id)
    if vocab.package.user_id != current_user.id and not current_user.is_admin:
        flash('Không có quyền xóa từ này!', 'danger')
        return redirect(url_for('packages'))
    package_id = vocab.package_id
    db.session.delete(vocab)
    db.session.commit()
    return redirect(url_for('edit_package', package_id=package_id))


# ──────────────────────────────────────────────
# STUDY MODES
# ──────────────────────────────────────────────

@app.route('/package/<int:package_id>/flashcard')
@login_required
def flashcard(package_id):
    package, _ = get_study_package(VocabPackage, package_id, current_user)
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
    package, _ = get_study_package(VocabPackage, package_id, current_user)
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
    package, _ = get_study_package(VocabPackage, package_id, current_user)
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
    package, _ = get_study_package(VocabPackage, package_id, current_user)
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


# ══════════════════════════════════════════════
# ADMIN PANEL
# ══════════════════════════════════════════════

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users    = User.query.count()
    total_packages = VocabPackage.query.count()
    total_words    = Vocabulary.query.count()
    recent_users   = User.query.order_by(User.created_at.desc()).limit(5).all()
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_packages=total_packages,
        total_words=total_words,
        recent_users=recent_users
    )


@app.route('/admin/users')
@admin_required
def admin_users():
    q     = request.args.get('q', '').strip()
    query = User.query
    if q:
        query = query.filter(
            (User.username.ilike(f'%{q}%')) | (User.email.ilike(f'%{q}%')) | (User.name.ilike(f'%{q}%'))
        )
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, search_query=q)


@app.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        name     = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        role     = int(request.form.get('role', ROLE_USER))

        if User.query.filter_by(username=username).first():
            flash('Username đã tồn tại!', 'danger')
            return render_template('admin/user_form.html', action='create', user=None)
        if User.query.filter_by(email=email).first():
            flash('Email đã tồn tại!', 'danger')
            return render_template('admin/user_form.html', action='create', user=None)

        user = User(username=username, email=email, name=name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f'Đã tạo người dùng "{username}".', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin/user_form.html', action='create', user=None)


@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username     = request.form.get('username', '').strip()
        email        = request.form.get('email', '').strip()
        name         = request.form.get('name', '').strip()
        role         = int(request.form.get('role', ROLE_USER))
        new_password = request.form.get('new_password', '').strip()

        existing_u = User.query.filter_by(username=username).first()
        if existing_u and existing_u.id != user_id:
            flash('Username đã được sử dụng!', 'danger')
            return render_template('admin/user_form.html', action='edit', user=user)
        existing_e = User.query.filter_by(email=email).first()
        if existing_e and existing_e.id != user_id:
            flash('Email đã được sử dụng!', 'danger')
            return render_template('admin/user_form.html', action='edit', user=user)

        user.username = username
        user.email    = email
        user.name     = name
        user.role     = role
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        flash(f'Đã cập nhật người dùng "{username}".', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin/user_form.html', action='edit', user=user)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Không thể xóa tài khoản đang đăng nhập!', 'danger')
        return redirect(url_for('admin_users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'Đã xóa người dùng "{user.username}".', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/packages')
@admin_required
def admin_packages():
    q     = request.args.get('q', '').strip()
    query = VocabPackage.query
    if q:
        q_norm   = normalize_text(q)
        all_pkgs = query.order_by(VocabPackage.updated_at.desc()).all()
        pkgs = [
            p for p in all_pkgs
            if q_norm in normalize_text(p.package_name)
            or (p.user and q_norm in normalize_text(p.user.username))
        ]
    else:
        pkgs = query.order_by(VocabPackage.updated_at.desc()).all()

    # Number of learners who saved each package (for admin table).
    if pkgs:
        learner_counts = learner_counts_for_packages(
            db, user_saved_packages, func, [p.id for p in pkgs]
        )
    else:
        learner_counts = {}

    return render_template(
        'admin/packages.html',
        packages=pkgs,
        search_query=q,
        learner_counts=learner_counts
    )


@app.route('/admin/packages/<int:package_id>/toggle_public', methods=['POST'])
@admin_required
def admin_toggle_public(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    package.is_public  = not package.is_public
    package.updated_at = datetime.utcnow()
    db.session.commit()
    state = 'công khai' if package.is_public else 'riêng tư'
    flash(f'Đã chuyển "{package.package_name}" sang {state}.', 'info')
    return redirect(url_for('admin_packages'))


@app.route('/admin/packages/<int:package_id>/delete', methods=['POST'])
@admin_required
def admin_delete_package(package_id):
    package = VocabPackage.query.get_or_404(package_id)
    name    = package.package_name
    db.session.delete(package)
    db.session.commit()
    flash(f'Đã xóa gói từ "{name}".', 'success')
    return redirect(url_for('admin_packages'))


# ── Error handlers ──────────────────────────────────────────

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


# ══════════════════════════════════════════════
# STARTUP
# ══════════════════════════════════════════════

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_topic_catalog(db, TopicCatalog, PACKAGE_TOPICS)

        if not User.query.filter_by(role=ROLE_ADMIN).first():
            admin = User(
                username='admin',
                email='admin@rundaword.local',
                name='Administrator',
                role=ROLE_ADMIN
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin created  →  admin / admin123")

        print("✓ Database initialized!")
    print("Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)