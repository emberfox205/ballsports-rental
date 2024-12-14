import sqlite3
import os

def initial():
    class_names = [
        'american_football',
        'baseball',
        'basketball',
        'football',
        'table_tennis_ball',
        'tennis_ball',
        'volleyball'
    ]

    # Correct the file path
    db_path = r'instance/ballstorage.db'

    # Check if the directory exists
    if not os.path.exists(os.path.dirname(db_path)):
        raise FileNotFoundError(f"Directory does not exist: {os.path.dirname(db_path)}")

    try:
        connect = sqlite3.connect(db_path)
        cur = connect.cursor()
        
        cur.execute("DROP TABLE IF EXISTS stock") # Comment if you dont want do drop
        cur.execute("DROP TABLE IF EXISTS ballRent")  # Comment if you dont want do drop
        
        cur.execute('''CREATE TABLE IF NOT EXISTS stock 
                        (ball TEXT PRIMARY KEY , quantity INTEGER)''')

        for i in class_names:
            values = [i, 10]
            cur.execute("""INSERT INTO stock (ball, quantity) VALUES (?, ?)""", values)

        cur.execute('''CREATE TABLE IF NOT EXISTS ballRent 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, ball TEXT, date TEXT, email TEXT, returned INT)''')
        
        connect.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":   
    initial()
