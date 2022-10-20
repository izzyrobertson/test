from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, request, url_for, redirect, logging, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
login_manager = LoginManager(app)
# SQLITE Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contactappdb.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/contactappdb'  # added the users database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Secret Key
# to use the form correctly, you need to set a secret key
app.config['SECRET_KEY'] = "secret_key"

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
    # here I suggest you use return redirect(url_for('login')) instead of render_template

    # I'll show you a neat trick
    # this way, if someone goes to your '/' route, if he's logged in, he goes to home page
    # if not, he goes to login page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/home', methods=["POST", "GET"])
@login_required
# if you use the current_user but not the @login_required decorator you might get that AnonymousUserMixin error
def home():
    return render_template('home.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        print(user)
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            # when using redirect(url_for()) you send as parameter the function name, not the route
            # so in this case, you should use redirect(url_for('login')), not '/login'
            return redirect(url_for('login'))  # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=True)
        return redirect(url_for('home'))
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
        # before saving the user to the database, you need to hash the password
        hash_pw = generate_password_hash(user_password, method='sha256')
        # create a new user with the form data. Save the hashed password so the plaintext version isn't saved
        new_user = User(email=user_email, f_name=user_f_name, l_name=user_l_name, password=hash_pw)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/signup')

    else:
        users = User.query.order_by(User.date_added)
        return render_template('signup.html', user=users)


@app.route('/adduser')
def adduser():
    return render_template('adduser.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
