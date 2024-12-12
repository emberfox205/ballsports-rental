from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
import tensorflow as tf
from datetime import timedelta , datetime
import sqlite3, json
import base64
from io import BytesIO
from PIL import Image
from libs.img_handling import process_image, logo_check
from initialize import initial

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ballstorage.db'
app.permanent_session_lifetime = timedelta(minutes= 5)
app.config['SECRET_KEY'] = 'averysecretkey'
db = SQLAlchemy(app)
model = tf.keras.models.load_model('model/model.keras', compile=False)
logo = tf.keras.models.load_model('model/logo.keras', compile=False)

with open("check_database.json") as f:
    data = json.load(f)
    if data.get("database_init") == 0:
        initial()
        data["database_init"] = 1
        with open("check_database.json", "w") as fw:
            json.dump(data, fw)
    else:
        pass

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    def __init__(self, email, password):
        self.email = email
        self.password = password

def connectDb():
    try:
        connect = sqlite3.connect('instance/ballstorage.db')
        cur = connect.cursor()
        return connect,cur
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

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
    if "email" in session:
        return render_template("dashboard.html")
    else:
        return redirect(url_for("login"))
    
@app.route('/rent')
def rent():
    if "email" in session:
        connect, cur = connectDb()
        gmail = session.get('email')
        cur.execute("SELECT returned FROM ballRent WHERE email = ? ORDER BY ID DESC LIMIT 1", (gmail,))
        returned = cur.fetchone()
        connect.commit()
        if not returned or returned[0] == 1:
            return render_template('rent.html')
        else:
            return '''
            <script>
                window.location.href = '/returnning';
                alert("Please return the item first.");
            </script>
            '''
    else:
        return redirect(url_for("login"))   
    
@app.route('/returnning')
def returnning():
    if "email" in session:
        connect, cur = connectDb()
        gmail = session.get('email')
        cur.execute("SELECT returned FROM ballRent WHERE email = ? ORDER BY ID DESC LIMIT 1", (gmail,))
        returned = cur.fetchone()
        connect.commit()
        if returned[0] == 0:
            return render_template('return.html')
        else:
            return '''
            <script>
                window.location.href = '/rent';
                alert("You have nothing to return.");
            </script>
            '''
    else:
        return redirect(url_for("login"))  
    
@app.route('/finalRent')
def finalRent():
    if "email" in session: #and session.get("redirect_flag") == 1: # You can only access this page through redirection, commented for dev purposes
        return render_template("finalRent.html")
    else:
        return redirect(url_for("login"))

@app.route('/confirmRent', methods = ["POST"])
def confirmRent():
    data = request.json()
    if not data or not all(k in data for k in ("ball_name", "confidence", "date")):
        print("Received Unsuccessfully")
        return jsonify({'error': 'No data provided'}), 400
    
    print("Successfully Received")
    connect, cur = connectDb()
    data["date"] /= 1000 # Convert ms to m 
    values = [data["ball_name"], data["date"], session.get('email'), 0]
    cur.execute('''CREATE TABLE IF NOT EXISTS ballRent 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, ball TEXT, date TEXT, email TEXT, returned INT)''')
    cur.execute("""INSERT INTO ballRent (ball, date, email, returned) VALUES (?, ?, ?, ?)""", values)
    connect.commit()
    connect.close()

@app.route('/confirmReturn', methods = ["POST"])
def confirmReturn():

    data = request.json()
    if not data or not all(k in data for k in ("ball_name", "confidence", "date")):
        print("Received Unsuccessfully")
        return jsonify({'error': 'No data provided'}), 400
    
    print("Successfully Received")
    connect, cur = connectDb()
    cur.execute("""UPDATE ballRent SET returned = ? WHERE ball = ? AND email = ?""", 
                    (1, data["ball_name"], session.get('email')))
    connect.commit()
    connect.close()

@app.route('/finalReturn')
def finalReturn():
    if "email" in session: #and session.get("redirect_flag") == 1: # You can only access this page through redirection, commented for dev purposes
        
        return render_template("finalReturn.html")
    else:
        return redirect(url_for("login"))
    
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
            # Check if the count reaches the threshold then reset it
            if recognition_data['recognition_count'] >= 3:
                recognition_data['ball_name'] = None
                recognition_data['confidence'] = None
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

@app.route("/detectReturn", methods=["POST", "GET"])
def detectReturn():
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
        
        if is_recognized and is_recognized["confidence"] > 0.70:
            check_logo = logo_check(logo, image)
            connect, curr = connectDb()
            curr.execute("select ball from ballRent ")
            gmail = session.get('email')
            curr.execute("SELECT ball FROM ballRent WHERE email = ? ORDER BY ID DESC LIMIT 1", (gmail,))
            rentedBall = curr.fetchone()
            connect.commit()
            if rentedBall and rentedBall[0] == is_recognized["class_name"]:
                print("YESSSS")
                # First recognition with logo
                if recognition_data['ball_name'] is None and check_logo:
                    recognition_data['ball_name'] = is_recognized["class_name"]
                    recognition_data['confidence'] = is_recognized["confidence"]
                    recognition_data['recognition_count'] = 1
                    is_recognized["logo_flag"] = 1
                
                # If next recognition produce same result with logo
                elif recognition_data['ball_name'] == is_recognized["class_name"] and check_logo:
                    # Increment count if the same ball is recognized
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
            else:
                is_recognized["class_name"] = "Not Rented Ball"
            
            # Return result regardless the accuracy
        if is_recognized:
            print(is_recognized["logo_flag"])
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

