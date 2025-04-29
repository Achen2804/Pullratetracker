import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
import os
from pokemontcgsdk import Set
from pokemontcgsdk import RestClient
from pokemontcgsdk import Card
import json
import re
from dotenv import load_dotenv
import time
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
    word = match.group(1)  
    reverse = f"Rare {word}"
    set_ref = db.reference(f'/Sets/{set_name}/{rarity}')
    images_urls = []
    data_snapshot = set_ref.get()
    if data_snapshot is not None:
        print("We have a set")
        
        for card_id in data_snapshot:
            card_data = db.reference(f'/Cards/{card_id}').get()
            images = card_data.get('images', {})
            large_url = images.get('large')
            if large_url:
                images_urls.append(large_url)
    else:
        set_ref = db.reference(f'/Sets/{set_name}/{reverse}')
        data_snapshot = set_ref.get()
        if data_snapshot is not None:
            print("We have a set")
            for card_id in data_snapshot:
                card_data = db.reference(f'/Cards/{card_id}').get()
                images = card_data.get('images', {})
                large_url = images.get('large')
                if large_url:
                    images_urls.append(large_url)
        else:
            print("No data found for this set.")
    return images_urls
set_name = 'Paldea Evolved'
rarity = 'Double Rare'
print(f"Received set_name: {set_name}")
print(f"Received rarity: {rarity}")
if(set_name == 'None'):
    exit("Something went wrong and no set name was provided. Please try again")
cards = []
match = re.match(r"(\w+)\sRare", rarity)
start_time = time.time()

if 'Gallery' in rarity:
    print("We have a gallery")
    set_name = set_name+' '+rarity
    print(set_name)
    set_ref = db.reference(f'/Sets/{set_name}')
    data_snapshot = set_ref.get()
    if data_snapshot is not None:
        print("We have a set")
    
    image_urls = []
    if(data_snapshot is not None):
        # Loop through rarities, and for each card, add its image URLs to the list
        for rarity, cards in data_snapshot.items():
            for card_id, card_data in cards.items():
                # Get image URLs (small and large) and add them to the list
                card_data = db.reference(f'/Cards/{card_id}').get()
                images = card_data.get('images', {})
                large_url = images.get('large')
                if large_url:
                    image_urls.append(large_url)
                #print(card_id)
        json_data = json.dumps(image_urls)
    else:
        print("No data found for this set.") 
    end_time = time.time()
    print(f"Query took {end_time - start_time} seconds")






elif set_name == 'Scarlet & Violet\u2014151':
    print("We have a special set")
    set_name = '151'
    process_request(set_name, rarity)
elif match:
    print("We might have to swap our wording around")
    print(rarity)
    process_request(set_name, rarity)
else:
    print("We have a normal rarity")
    process_request(set_name, rarity)
#card_ids = [card.id for card in cards]
images = [card.images.large for card in cards]
#print(card_ids)