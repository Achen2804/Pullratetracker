from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import RestClient
import re

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
    match = re.match(r"(\w+)\sRare", rarity)
    if 'Gallery' in rarity:
        print("We have a gallery")
        set_name = set_name+' '+rarity
        print(set_name)
        cards = Card.where(q=f'set.name:"{set_name}"')
    elif match:
        print("We might have to swap our wording around")
        print(rarity)
        word = match.group(1)  
        reverse = f"Rare {word}"
        print(reverse)
        cards = Card.where(q=f'(set.name:"{set_name}") (rarity:"{rarity}" OR rarity:"{reverse}")')
    else:
        print("We have a normal rarity")
        cards = Card.where(q=f'set.name:"{set_name}" rarity:"{rarity}"')
    card_ids = []
    images = []
    for card in cards:
        card_ids.append(card.id)
        images.append(card.images.large)
    print(card_ids)
    return jsonify(images)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
