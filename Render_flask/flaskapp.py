from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
from pokemontcgsdk import Rarity
from pokemontcgsdk import RestClient

RestClient.configure('3ba6f406-4bd1-4b37-ad93-64fef7a956d3')

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
    card = Card.find('sv8pt5-16')
    return jsonify(card.images.large)

@app.route('/api/getset')
def get_set():
    set_name = request.args.get('set_name','None',type=str)
    rarity = request.args.get('rarity','Rare Ultra',type=str)
    print(f"Received set_name: {set_name}")
    print(f"Received rarity: {rarity}")
    if(set_name == 'None'):
        return jsonify({'error':'Something went wrong and no set name was provided. Please try again'})
    cards = []
    if 'Gallery' in rarity:
        set_name = set_name+' '+rarity
        cards = Card.where(q=f'(set.name:"{set_name}")')
    else:
        cards = Card.where(q=f'(set.name:"{set_name}") rarity:"{rarity}"')
    card_ids = []
    images = []
    for card in cards:
        card_ids.append(card.id)
        images.append(card.images.large)
    return jsonify(images)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
