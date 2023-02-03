from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.sqlite3'
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/')
@login_required
def index():
    todos = Todo.query.filter_by(user_id=current_user.id, complete=False).all()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
@login_required
def add():
    todo = Todo(text=request.form['todoitem'], complete=False, user_id=current_user.id)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<id>')
@login_required
def complete(id):
    todo = Todo.query.filter_by(id=int(id), user_id=current_user.id).first()
    todo.complete = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<id>')
@login_required
def delete(id):
    todo = Todo.query.filter_by(id=int(id), user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user is not None:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__== '__main__':
    app.run(debug=True)
