import sqlite3
import os


class_names = [
    'american_football',
    'baseball',
    'basketball',
    'football',
    'table_tennis_ball',
    'tennis_ball',
    'volleyball'
]
session = {"email" : "vguhoangvu@gmail.com"}
data = {"ball_name": "basketball", "date": "11/12/2024" }
data2 = {"ball_name": "pickled balled", "date": "56/22/3030" }
def rentconf():
    values = [data["ball_name"], data["date"], session['email'], 0]
    cur.execute('''CREATE TABLE IF NOT EXISTS ballRent 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, ball TEXT, date TEXT, email TEXT, returned INT)''')
    cur.execute("""INSERT INTO ballRent (ball, date, email, returned) VALUES (?, ?, ?, ?)""", values)
    connect.commit()
def returnconf():
    cur.execute("""UPDATE ballRent SET returned = ? WHERE ball = ? AND email = ?""", 
                    (1, data["ball_name"], session['email']))
    connect.commit()

# Correct the file path
db_path = r'instance/ballstorage.db'

# Check if the directory exists
if not os.path.exists(os.path.dirname(db_path)):
    raise FileNotFoundError(f"Directory does not exist: {os.path.dirname(db_path)}")

try:
    connect = sqlite3.connect(db_path)
    cur = connect.cursor()


    cur.execute('''CREATE TABLE IF NOT EXISTS ballRent 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, ball TEXT, date TEXT, email TEXT, returned INT)''')
    connect.commit()

    
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if connect:
        connect.close()
