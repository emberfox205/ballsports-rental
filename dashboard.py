from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
import tensorflow as tf
from datetime import timedelta , datetime
import sqlite3, json
import base64
from io import BytesIO
from PIL import Image
from libs.img_handling import process_image, logo_check

markers = []
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ballstorage.db'
app.permanent_session_lifetime = timedelta(minutes= 5)
app.config['SECRET_KEY'] = 'averysecretkey'
db = SQLAlchemy(app)
model = tf.keras.models.load_model('model/model.keras', compile=False)
logo = tf.keras.models.load_model('model/logo.keras', compile=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100))
    def __init__(self, email, password, date = None):
        self.email = email
        self.password = password
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Ball(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100),nullable = False)
    sport = db.Column(db.String(50), nullable = False)
    condition = db.Column(db.String(10), nullable = False)
    def __init__(self, email, sport, condition):
        self.email = email
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
    
@app.route('/logout')
def logout():
    session.pop("email", None)
    session.pop("thing_id", None)
    return redirect(url_for('login'))

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
    
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route('/rent')
def rent():
    return render_template('rent.html')

@app.route('/returnning')
def returnning():
    return render_template('return.html')

@app.route('/finalRent')
def finalRent():
    return render_template("finalRent.html")

@app.route('/finalReturn')
def finalReturn():
    return render_template("finalReturn.html")


@app.route("/detect", methods=["POST", "GET"])
def detect():
    if request.method == "POST":
       # Create a dict in the session to store the recognized ball, accuracy and recognition count  
        if 'recognition_data' not in session:
           session['recognition_data'] = {
               'ball_name': None,  
               'confidence': None,
               'recognition_count': 0
               }
        # Get image
        data = request.json
        print(dict(data).keys())
        if data is None or "image" not in data:
            print("Received Unsuccessfully ")
            return jsonify({'error': 'No images provided'}), 400
        print("Successfully Received")

        # Decode image
        try:
            image = data["image"]
            image = base64.b64decode(image.split(',')[1])  # Skip the data URI prefix
            image = Image.open(BytesIO(image))
            image = image.convert('RGB')
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        
        # Detect the ball
        is_recognized = process_image(model, image)  # return dict {"class_name": ,"confidence": }
        is_recognized["logo_flag"] = 0
        print(f"Recognised {is_recognized['class_name']}, with {round(is_recognized['confidence'],4)} confidence")
        recognition_data = session['recognition_data']
        print(f"Repeated {recognition_data['recognition_count']} times.")
        
        if is_recognized and is_recognized["confidence"] > 0.85 :
            check_logo = logo_check(logo, image)
            # First recognition with logo
            if recognition_data['ball_name'] is None and check_logo:
                recognition_data['ball_name'] = is_recognized["class_name"]
                recognition_data['confidence'] = is_recognized["confidence"]
                recognition_data['recognition_count'] = 1
                is_recognized["logo_flag"] = 1
            
            # If next recognition produce same result with logo
            elif recognition_data['ball_name'] == is_recognized["class_name"] and check_logo:
                # Increment count if the same face is recognized
                recognition_data['confidence'] = is_recognized["confidence"]
                recognition_data['recognition_count'] += 1
                is_recognized["logo_flag"] = 1
            
            # Reset if different result is detected with logo
            elif recognition_data['ball_name'] != is_recognized["class_name"] and check_logo:
                recognition_data['ball_name'] = is_recognized["class_name"]
                recognition_data['confidence'] = is_recognized["confidence"]
                recognition_data['recognition_count'] = 1
                is_recognized["logo_flag"] = 1
                # Reset if no logo is detected
            elif not check_logo:
                recognition_data['recognition_count'] = 0
                
            session.modified = True  # Mark session as modified

            # Check if the count reaches the threshold
            if recognition_data['recognition_count'] >= 3:
                recognition_data['recognition_count'] = 0
                return jsonify({'redirect': 1}), 200

        # Return result regardless the accuracy
        if is_recognized:
            print( is_recognized["logo_flag"])
            return jsonify({
                'ball_name': is_recognized["class_name"],
                'confidence': is_recognized["confidence"]
                #,'logo_flag': is_recognized["logo_flag"]
            }), 200
        else:
            return jsonify({'error': 'Error processing image'}), 400
    else:
        return jsonify({'error': 'Method Not Allowed'}), 405
    

  

if __name__ == "__main__":          
    with app.app_context():
        db.create_all()
    # cert goes before private key
    app.run(host="0.0.0.0", port=8080, debug=True, ssl_context=("certs/certificate.crt", "certs/private.key"))
	