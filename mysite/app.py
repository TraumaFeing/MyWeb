from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# 数据库初始化函数
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# 在应用启动时初始化数据库
init_db()

# 注册API
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    # 验证用户名和密码长度
    if len(username) < 4 or len(password) < 6:
        return jsonify({"message": "Username must be at least 4 characters and password 6 characters"}), 400
    
    hashed_password = generate_password_hash(password)
    
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                       (username, hashed_password))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Username already exists"}), 409
    except Exception as e:
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# 登录API
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row and check_password_hash(row[0], password):
            return jsonify({
                "message": "Login successful",
                "username": username
            }), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"message": f"Login failed: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)