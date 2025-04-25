import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
import os

load_dotenv()

key_path = os.getenv("FIREBASE_KEY_PATH")



cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://pullratetracker-default-rtdb.firebaseio.com'
})
ref = db.reference('Sets')