from flask import Flask, render_template, request, url_for, redirect
# import mysql
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)  # created flask instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/moneyappdb'  # added the users database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)  # initialise the database


class Users(db.Model):  # creating model
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    f_name = db.Column(db.String(200), nullable=False)
    l_name = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    income = db.relationship('Income', backref='users')
    expense = db.relationship('Expense', backref='users')
    goal = db.relationship('Goal', backref='users')
    budget = db.relationship('Budget', backref='users')

    def __repr__(self):  # creating a string
        return '<name %r>' % self.id


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    income_amount = db.Column(db.Integer, nullable=False)
    income_source = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_amount = db.Column(db.Integer, nullable=False)
    expense_source = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_amount = db.Column(db.Integer, nullable=False)
    goal_info = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    budget_amount = db.Column(db.Integer, nullable=False)
    budget_length = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))


@app.route("/", methods=['GET', 'POST', 'DELETE'])
def login():
    if request.method == "POST":
        user_email = request.form.get("email")
        user_f_name = request.form.get("first_name")
        user_l_name = request.form.get("last_name")
        user_password = request.form.get("password")
        new_user = Users(email=user_email, f_name=user_f_name, l_name=user_l_name, password=user_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/')

    else:
        users = Users.query.order_by(Users.date_added)
        return render_template('login.html', users=users)


@app.route("/registration")
def menu():
    return render_template('registration.html')


if __name__ == "__main__":
    app.run(debug=True)
