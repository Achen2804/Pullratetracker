from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend access

@app.route('/')
def home():
    return "Hello fuckers"

@app.route('/api/data')
def get_data():
    return jsonify({"message": "Hello from Flask!", "status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
