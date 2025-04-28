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
load_dotenv()
API_KEY = os.getenv("POKEMON_API_KEY")
RestClient.configure(API_KEY)
load_dotenv()

key_path = os.getenv("FIREBASE_KEY_PATH")



cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://pullratetracker-default-rtdb.firebaseio.com'
})
def process_request(set_name, rarity):
    card_ref = db.reference('/Cards')
    
    match = re.match(r"(\w+)\sRare", rarity)
    word = match.group(1)  
    reverse = f"Rare {word}"
    set_ref = db.reference(f'/Sets/{set_name}/{rarity}')
    images_urls = []
    data_snapshot = set_ref.get()
    if data_snapshot is not None:
        print("We have a set")
        
        for card_id in data_snapshot:
            card_data = db.reference(f'/Cards/{card_id}/images/large').get()
            if card_data:
                images_urls.append(card_data)
    else:
        set_ref = db.reference(f'/Sets/{set_name}/{reverse}')
        data_snapshot = set_ref.get()
        if data_snapshot is not None:
            print("We have a set")
            
            for card_id in data_snapshot:
                card_data = db.reference(f'/Cards/{card_id}/images/large').get()
                if card_data:
                    images_urls.append(card_data)
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
    match = re.match(r"(\w+)\sRare", rarity)
    images = []
    if 'Gallery' in rarity:
        print("We have a gallery")
        set_name = set_name+' '+rarity
        print(set_name)
        set_ref = db.reference(f'/Sets/{set_name}')
        data_snapshot = set_ref.get()
        if data_snapshot is not None:
            print("We have a set")
            
        
        
        if(data_snapshot is not None):
            # Loop through rarities, and for each card, add its image URLs to the list
            for rarity, cards in data_snapshot.items():
                for card_id, card_data in cards.items():
                    # Get image URLs (small and large) and add them to the list
                    card_data = db.reference(f'/Cards/{card_id}/images/large').get()
                    if card_data:
                        images.append(card_data)
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
    app.run(host='0.0.0.0', port=8080)
