import requests
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
from pokemontcgsdk import Rarity
from pokemontcgsdk import RestClient

RestClient.configure('3ba6f406-4bd1-4b37-ad93-64fef7a956d3')

def process_set(set_name):
    set = Set.find(set_name)
    set_json = set.images.logo
    images = []
    images.append(set_json)
    cards = Card.where(q='(set.id:swsh12 OR set.id:swsh12tg) rarity:"Rare Ultra"')
    card_ids = []
    for card in cards:
        card_ids.append(card.id)
        images.append(card.images.large)
    print(card_ids)
    return images

images = process_set('swsh1')
print(Card.find('swsh12pt5gg-GG05').rarity)
#print(Rarity.all())
html_content = "<html><body>" + "".join(f'<img src="{url}" style="width:300px;"><br>' for url in images) + "</body></html>"

with open("images.html", "w") as f:
    f.write(html_content)

print("Open images.html in your browser")



