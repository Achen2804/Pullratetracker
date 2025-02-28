from flask import Flask, jsonify
from flask_cors import CORS
import requests
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
from pokemontcgsdk import Rarity


app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return "Hello Folks"

@app.route('/api/data')
def send_message():
    message = jsonify({'message':'hello'})
    return message

@app.route('/api/getcard')
def get_data():
    url = "https://api.pokemontcg.io/v2/cards/"
    headers = {
        "X-Api-Key": "3ba6f406-4bd1-4b37-ad93-64fef7a956d3"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    card = Card.find('sv8pt5-16')
    return jsonify(card)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
