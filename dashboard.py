from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import timedelta , datetime
import sqlite3, json
from libs.video import scanner


markers = []
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ballstorage.db'
app.permanent_session_lifetime = timedelta(minutes= 5)
app.config['SECRET_KEY'] = 'averysecretkey'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100))
    def __init__(self, email, password, date = None):
        self.email = email
        self.password = password
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Ball(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sport = db.Column(db.String(50), nullable = False)
    condition = db.Column(db.String(10), nullable = False)
    def __init__(self, sport, condition):
        self.sport = sport
        self.condition = condition

    
@app.route("/" , methods = ["POST", "GET"])
@app.route("/login" , methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
    
        session.permanent = True
        session["email"] = email
        found_user = User.query.filter_by(email = email).first()
        
        if found_user:
            
            if password == found_user.password:
                return redirect(url_for('dashboard'))
            else:
                flash("Please type the correct PASSWORD !")
                session.pop("email",None)
                session.pop("pass", None)
                return render_template("login.html")
        
        else:
            flash("You've not register yet")
            session.pop("email",None)
            session.pop("pass", None)
            return render_template("login.html")
    
    else:
        if "email" in session:
            flash("Already Logged in")
            return redirect(url_for("dashboard"))
        
    return render_template('login.html')
    
@app.route("/register" , methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        found_user = User.query.filter_by(email = email).first()
        if found_user:
            flash(" ACCOUNT EXISTED, PLEASE LOG IN!")
            session.pop("email",None)
            session.pop("pass", None)
            return redirect(url_for("login"))

        else:
            flash(f'Successfully registered!')
            account = User(email=email, password=password)
            db.session.add(account)
            db.session.commit()
            flash("User created successfully!")
            return redirect(url_for("login"))
    else:
        return render_template("register.html")
    
    
    
@app.route('/scan')
def index():
    return render_template('scan.html')

@app.route("/video")
def video():
    return Response(scanner(), mimetype="multipart/x-mixed-replace; boundary=frame")   

if __name__ == "__main__":          
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8080, debug=True)
	