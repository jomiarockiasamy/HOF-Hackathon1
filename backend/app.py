from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend')
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Database configuration
db_config = {
    'host': 'localhost',
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'user_info')
}

# Root route to serve the frontend
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'home.html')

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Test route
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is running!'})

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'email', 'phone', 'cashapp', 'zipcode', 'username', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor()

        # Check if username already exists
        cursor.execute("SELECT username FROM Users WHERE username = %s", (data['username'],))
        if cursor.fetchone():
            return jsonify({'error': 'Username already exists'}), 400

        # Insert new user
        insert_query = """
        INSERT INTO Users (name, email, phone, cashapp, zipcode, username, password)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            data['name'], data['email'], data['phone'],
            data['cashapp'], data['zipcode'], data['username'],
            data['password']
        ))
        
        connection.commit()
        return jsonify({'message': 'User registered successfully'}), 201

    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE username = %s", (data['username'],))
        user = cursor.fetchone()

        if user and user['password'] == data['password']:
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()
        
        return jsonify(users), 200

    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000) 