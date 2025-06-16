from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import RestClient
import re
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
load_dotenv()
API_KEY = os.getenv("POKEMON_API_KEY")
RestClient.configure(API_KEY)
load_dotenv()

firebase_key = os.getenv("FIREBASE_KEY_PATH")

if firebase_key and os.path.exists(firebase_key):
    cred = credentials.Certificate(firebase_key)
else:
    cred = credentials.Certificate(json.loads(firebase_key))

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://pullratetracker-default-rtdb.firebaseio.com'
})
def process_request(set_name, rarity):
    set_ref = db.reference(f'/Sets2/{set_name}/{rarity}')
    images_urls = []
    data_snapshot = set_ref.get()
    if data_snapshot is not None:
        print("We have a set")
        return data_snapshot
    else:
        words = rarity.split()  
        reverse = "Rare " + " ".join(words[:-1])
        set_ref = db.reference(f'/Sets2/{set_name}/{reverse}')
        data_snapshot = set_ref.get()
        if data_snapshot is not None:
            print("We have a set")
            return data_snapshot
        else:
            print("No data found for this set.")
    return images_urls
app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return "Hello Folks"

@app.route('/health')
def Update_Health():
    
    return "Good", 200

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
    match = re.match(r"(\S+(\s\S+)*)", rarity)
    images = []
    if 'Gallery' in rarity:
        print("We have a gallery")
        rarity = 'Trainer Gallery Rare Holo'
        images = process_request(set_name, rarity)
                    #print(card_id)
    elif set_name == 'Scarlet & Violet\u2014151':
        print("We have a special set")
        set_name = '151'
        images = process_request(set_name, rarity)
    elif match:
        print("We might have to swap our wording around")
        print(rarity)
        images = process_request(set_name, rarity)
    else:
        print("We have a normal rarity")
        images = process_request(set_name, rarity)
    #card_ids = [card.id for card in cards]
    
    #print(card_ids)
    return jsonify(images)
if __name__ == '__main__':
    app.run(host='0.0.0.0')
