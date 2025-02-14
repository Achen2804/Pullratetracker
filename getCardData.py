import requests
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
from pokemontcgsdk import Rarity

url = "https://api.pokemontcg.io/v2/cards/"
headers = {
    "X-Api-Key": "3ba6f406-4bd1-4b37-ad93-64fef7a956d3"
}

response = requests.get(url, headers=headers)
data = response.json()
card = Card.find('sv8pt5-16')
# Process the data
print(card)