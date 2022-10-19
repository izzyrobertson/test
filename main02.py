from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, request, url_for, redirect, logging, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
pymysql.install_as_MySQLdb()


app = Flask(__name__)
login_manager = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/contactappdb'  # added the users database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # initialise the database


class User(db.Model, UserMixin):  # creating model
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    f_name = db.Column(db.String(200), nullable=False)
    l_name = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    contacts = db.relationship('Contact', backref='user')

    def __repr__(self):  # creating a string
        return '<name %r>' % self.id


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))
    phone = db.Column(db.BigInteger)
    notes = db.Column(db.String(300))
    category = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):  # creating a string
        return '<name %r>' % self.id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def mainP():
    return render_template('login.html')


@app.route('/home', methods=["POST", "GET"])
# @login_required
def home():
    return render_template('home.html', name=current_user.f_name)


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('/login'))  # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=True)
        return redirect(url_for('/home'))
    return render_template('login.html')


@app.route('/signup', methods=["POST", "GET"])
def registerForm():
    if request.method == "POST":
        user_email = request.form.get("email")
        user_f_name = request.form.get("first_name")
        user_l_name = request.form.get("last_name")
        user_password = request.form.get("password")
        print("user email")
        print(request.form.get('email'))
        print(user_f_name)
        print("password")
        new_user = User(email=user_email, f_name=user_f_name, l_name=user_l_name, password=user_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/signup')

    else:
        users = User.query.order_by(User.date_added)
        return render_template('signup.html', user=users)


@app.route('/adduser')
def adduser():
    return render_template('adduser.html')


if __name__ == "__main__":
    app.run(debug=True)