from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import timedelta , datetime
import sqlite3, json

markers = []
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ballusers.db'
app.permanent_session_lifetime = timedelta(minutes= 5)
app.config['SECRET_KEY'] = 'averysecretkey'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    def __init__(self, email,password):
        self.email = email
        self.password = password
        
    
@app.route("/" , methods = ["POST", "GET"])
@app.route("/login" , methods = ["POST", "GET"])
def login():
    return render_template("base.html")
    
@app.route("/register" , methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        thing_id = request.form["tid"]
        
        found_user = User.query.filter_by(email = email).first()
        if found_user:
            flash(" ACCOUNT EXISTED, PLEASE LOG IN!")
            session.pop("email",None)
            session.pop("pass", None)
            return redirect(url_for("login"))

        else:
            flash(f'Successfully registered!')
            account = User(email, password, thing_id)
            db.session.add(account)
            db.session.commit()
            return redirect(url_for("login"))
    else:
        return render_template("register.html")
    

@app.route("/data", methods=["POST", "GET"])
def data():
    
    connect = sqlite3.connect("instance/balluser.db")
    connect.row_factory = sqlite3.Row  # Set the row_factory to sqlite3.Row
    cur = connect.cursor()
    
    # This handles requests to update safe zone
    if request.method == "POST" and all(isinstance(float(request.form.get(key)), float) for key in ["lat", "lon", "safeRange"]):
        ...
       
    # This handles periodical requests from Front-end to display the saved coords, and send emails
    elif request.method == "GET":
        ...
        # Save safeZone to database

    return "OK\n"

if __name__ == "__main__":          
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8080, debug=True)
	