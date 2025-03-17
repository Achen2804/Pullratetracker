import requests
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
from pokemontcgsdk import Rarity
from pokemontcgsdk import RestClient
import json

RestClient.configure('3ba6f406-4bd1-4b37-ad93-64fef7a956d3')

def process_set(set_name):
    set = Set.find(set_name)
    set_json = set.images.logo
    images = []
    images.append(set_json)
    set_name = 'Crown Zenith'
    rarity = 'Rare Holo'
    cards = []
    if 'Gallery' in rarity:
        print("We have a gallery")
        set_name = set_name+' '+rarity
        print(set_name)
        cards = Card.where(q=f'set.name:"{set_name}"')
    elif 'Ultra Rare' in rarity:
        print("We have an ultra rare or rare ultra")
        cards = Card.where(q=f'set.name:"{set_name}" rarity:"Ultra Rare"')
    else:
        print("We have a normal rarity")
        cards = Card.where(q=f'set.name:"{set_name}" AND rarity:"{rarity}"')
    card_ids = []
    for card in cards:
        card_ids.append(card.id)
        images.append(card.images.large)
    #print(card_ids)
    return images

images = process_set('swsh12')
print(Card.find('swsh12pt5-160'))
#print(Rarity.all())
#images = Card.where(q=f'set.name:"Crown Zenith" rarity:"Rare Holo"')
html_content = "<html><body>" + "".join(f'<img src="{url}" style="width:300px;"><br>' for url in images) + "</body></html>"

with open("images.html", "w") as f:
    f.write(html_content)

