from flask import Flask, render_template, request, redirect, url_for, make_response, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key'

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

init_db()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Пользователь уже существует", 400
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            response = make_response(redirect(url_for('welcome')))
            response.set_cookie('username', user[1])
            return response
        else:
            error = "Неверные учетные данные"
    
    return render_template('login.html', error=error)

@app.route('/welcome')
def welcome():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    return render_template('welcome.html', username=username)

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.set_cookie('username', '', expires=0)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
