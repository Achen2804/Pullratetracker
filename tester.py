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
load_dotenv()
API_KEY = os.getenv("POKEMON_API_KEY")
RestClient.configure(API_KEY)
load_dotenv()

key_path = os.getenv("FIREBASE_KEY_PATH")



cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://pullratetracker-default-rtdb.firebaseio.com'
})
"""
ref = db.reference('Sets')
#print(ref.get())
cardTable = db.reference('Cards')
setTable = db.reference('Sets')
set_name = '151'
relevantSet = setTable.child(set_name)
import time
start_time = time.time()
cards = Card.where(q=f'set.name:"{set_name}"')
for card in cards:
    print(card.name)
    print(card.rarity)
    relevantSet.child(card.rarity).child(card.id).set({
        'name': card.name,
    })
    cardTable.child(card.id).set({
        'images': {
            'large': card.images.large,
            'small': card.images.small
        }
    })

        

images = [card.images.large for card in cards]
end_time = time.time()
print(f"Query took {end_time - start_time} seconds")

"""
ref = db.reference('Sets')
#print(ref.get())
cardTable = db.reference('Cards')
setTable = db.reference('Sets')
set_name = 'Crown Zenith Galarian Gallery'
cards = Card.where(q=f'set.name:"{set_name}"')
relevantSet = setTable.child('Crown Zenith')

for card in cards:
    print(card.name)
    print(card.rarity)
    relevantSet.child('Galarian Gallery').child(card.id).set({
        'name': card.name,
        'image': card.images.large
    })