from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话加密
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite 数据库路径
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 创建数据库模型：用户和评论
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        
        new_user = User(username=username, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功！请登录。', 'success')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash('注册失败，用户名可能已存在。', 'error')
    return render_template('register.html')

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('登录成功！', 'success')
            return redirect(url_for('game'))
        else:
            flash('用户名或密码错误！', 'error')
    return render_template('login.html')

# 游戏页面，用户可以在此评论
@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'user_id' not in session:
        flash('Please Login in！', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        content = request.form['content']
        new_comment = Comment(content=content, user_id=session['user_id'])
        db.session.add(new_comment)
        db.session.commit()
        flash('评论发布成功！', 'success')

    comments = Comment.query.all()
    return render_template('game.html', comments=comments)

# 退出登录
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('您已退出登录', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    db.create_all()  # 创建数据库
    app.run(debug=True)
