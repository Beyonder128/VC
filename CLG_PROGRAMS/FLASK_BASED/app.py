from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'student-system-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

db = SQLAlchemy(app)


# ==================== MODELS ====================

class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    phone      = db.Column(db.String(20), nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    students   = db.relationship('Student', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Student(db.Model):
    __tablename__ = 'students'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    course     = db.Column(db.String(100), nullable=False)
    phone      = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


# ==================== DECORATOR ====================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ==================== ROUTES ====================

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name             = request.form.get('name', '').strip()
        email            = request.form.get('email', '').strip().lower()
        phone            = request.form.get('phone', '').strip()
        password         = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not all([name, email, phone, password, confirm_password]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))

        if len(password) < 8 or len(password) > 14:
            flash('Password must be 8-14 characters long!', 'danger')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered! Please login.', 'danger')
            return redirect(url_for('signup'))

        try:
            user = User(name=name, email=email, phone=phone)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('signup'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email       = request.form.get('email', '').strip().lower()
        password    = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me')

        if not email or not password:
            flash('Email and password are required!', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session.permanent = bool(remember_me)
            session['user_id']    = user.id
            session['user_name']  = user.name
            session['user_email'] = user.email
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password!', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user      = db.session.get(User, session['user_id'])
    all_users = User.query.all()
    return render_template('dashboard.html', user=user, users=all_users)


@app.route('/students')
@login_required
def students():
    user         = db.session.get(User, session['user_id'])
    student_list = Student.query.filter_by(user_id=session['user_id']).all()
    return render_template('students.html', students=student_list, user=user)


@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        name   = request.form.get('name', '').strip()
        email  = request.form.get('email', '').strip().lower()
        course = request.form.get('course', '').strip()
        phone  = request.form.get('phone', '').strip()

        if not all([name, email, course, phone]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('add_student'))

        if Student.query.filter_by(user_id=session['user_id'], email=email).first():
            flash('A student with this email already exists!', 'danger')
            return redirect(url_for('add_student'))

        try:
            student = Student(name=name, email=email, course=course,
                              phone=phone, user_id=session['user_id'])
            db.session.add(student)
            db.session.commit()
            flash(f'Student {name} added successfully!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_student'))

    return render_template('add_student.html')


@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)

    if student.user_id != session['user_id']:
        flash('Permission denied!', 'danger')
        return redirect(url_for('students'))

    if request.method == 'POST':
        name   = request.form.get('name', '').strip()
        email  = request.form.get('email', '').strip().lower()
        course = request.form.get('course', '').strip()
        phone  = request.form.get('phone', '').strip()

        if not all([name, email, course, phone]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('edit_student', id=id))

        duplicate = Student.query.filter(
            Student.user_id == session['user_id'],
            Student.email   == email,
            Student.id      != id
        ).first()

        if duplicate:
            flash('Another student already has this email!', 'danger')
            return redirect(url_for('edit_student', id=id))

        try:
            student.name   = name
            student.email  = email
            student.course = course
            student.phone  = phone
            db.session.commit()
            flash(f'Student {name} updated successfully!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('edit_student', id=id))

    return render_template('edit_student.html', student=student)


@app.route('/delete_student/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)

    if student.user_id != session['user_id']:
        flash('Permission denied!', 'danger')
        return redirect(url_for('students'))

    try:
        name = student.name
        db.session.delete(student)
        db.session.commit()
        flash(f'Student {name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('students'))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


# ==================== CONTEXT PROCESSOR ====================

@app.context_processor
def inject_user():
    if 'user_id' in session:
        return {'current_user': db.session.get(User, session['user_id'])}
    return {}


# ==================== STARTUP ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False) 