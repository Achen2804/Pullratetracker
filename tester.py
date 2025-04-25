import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
import os
from pokemontcgsdk import Set
from pokemontcgsdk import RestClient
from pokemontcgsdk import Card
import json
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
ref = db.reference('Sets')
print(ref.get())
cardTable = db.reference('Cards')
setTable = db.reference('Sets')
set_name = 'Crown Zenith'
cards = Card.where(q=f'set.name:"{set_name}"')
print(cards)