from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # إضافة Flask-Migrate

# نماذج قاعدة البيانات
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile_image = db.Column(db.String(120), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file_url = db.Column(db.String(120))  # العمود الجديد
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# تسجيل الأحداث
def log_event(user_id, event_type, event_data=None):
    new_event = Event(user_id=user_id, event_type=event_type, event_data=event_data)
    db.session.add(new_event)
    db.session.commit()

# الصفحة الرئيسية
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

# صفحة جميع المنشورات
@app.route('/allposts')
def all_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('allposts.html', posts=posts)

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            log_event(user.id, 'login')
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('index'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة!', 'danger')
    return render_template('login.html')

# تسجيل المستخدم
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        log_event(new_user.id, 'register')
        flash('تم التسجيل بنجاح!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# تسجيل الخروج
@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_event(session['user_id'], 'logout')
        session.pop('user_id', None)
    flash('تم تسجيل الخروج بنجاح!', 'success')
    return redirect(url_for('index'))

# صفحة الملف الشخصي
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('المستخدم غير موجود!', 'danger')
        return redirect(url_for('index'))

    return render_template('profile.html', user=user)

# صفحة نشر منشور جديد
@app.route('/addpost', methods=['GET', 'POST'])
def add_post():
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files.get('file')
        file_url = None
        if file and file.filename != '':
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = filename
        new_post = Post(user_id=session['user_id'], title=title, content=content, file_url=file_url)
        db.session.add(new_post)
        db.session.commit()
        log_event(session['user_id'], 'create_post', f'Post ID: {new_post.id}')
        flash('تم نشر المنشور بنجاح!', 'success')
        return redirect(url_for('all_posts'))

    return render_template('addpost.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)