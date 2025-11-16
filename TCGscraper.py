import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
from multiprocessing import Pool
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
import os
from pokemontcgsdk import Card
from pokemontcgsdk import RestClient
exceptions_list = ["Black Bolt and White Flare"]
def get_articles():
# Headless mode (optional)
    op = Options()
    #op.add_argument('--headless')  # Run in headless mode
    op.add_argument('--disable-gpu')  # Disable GPU acceleration (optional)
    driver = webdriver.Chrome(options=op)
    url = "https://www.tcgplayer.com/search/articles?q=pull+rates&productLineName=pokemon&page=1"
    driver.implicitly_wait(10)

    driver.get(url)

    content_container = driver.find_element(By.CLASS_NAME, "search-results")

    relevant_articles = content_container.find_elements(By.XPATH, "//div[@class='grid']//a[@class='martech-base-link'][.//text()[contains(., 'Pokémon TCG')] and .//text()[contains(., 'Pull Rates')]]")
    set_to_link = {}
    for article in relevant_articles:
        
        link = article.get_attribute("href")
        article_title = article.find_element(By.CLASS_NAME,"martech-heading-sm")
        title = article_title.text
        match = re.search(r"Pokémon TCG: (.*?) Pull Rates", title)
        if match:
            setName = match.group(1)
            set_to_link[setName] = link
            print(f"Set Name: {setName}")
    driver.quit()
    return set_to_link

def get_pullrates(args):
    setName, source = args
    op = Options()
    print(setName)
    op.add_argument('--headless')  # Run in headless mode
    op.add_argument('--disable-gpu')  
    driver = webdriver.Chrome(options=op)
    driver.implicitly_wait(5)
    driver.get(source)
    try:
        articleBody = driver.find_element(By.CLASS_NAME, "article-body")
    except Exception as e:

        print(f"Error: {e}")
        driver.quit()
        return (setName, [])
    
    content_container = driver.find_element(By.XPATH, "(.//th[starts-with(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'pull rate')])")
    table_body = content_container.find_element(By.TAG_NAME,"tbody")
    
    data = []
    supertype = None
    subtype = None    
    
    pattern = re.compile(r".+specific.+\d+\s*in\s*\d+", re.IGNORECASE)
    Rarity_Lists = articleBody.find_elements(By.XPATH, "h3 | h2")
    Entries = {}
    translator = {
        'Pokémon V': 'Normal Pokémon V',
        'Pokémon VMAX or VSTAR': 'Normal Pokémon VMAX or VSTAR',
        'Pokémon V, Pokémon VMAX, or Trainer': 'V, VMAX, or Trainer',
        'Gold-and-Black VMAX': 'Gold-and-Black Pokémon VMAX',
        'Gold-and-Black VSTAR': 'Gold-and-Black Pokémon VSTAR',
    }
    for i, rarity in enumerate(Rarity_Lists):
        
        next_rarity = Rarity_Lists[i + 1] if i + 1 < len(Rarity_Lists) else None
        current_element = rarity
        val = rarity.text.strip()
        rarityText = re.sub(r"\(\d+\s*in\s*\d+\)$", "", val).strip()
        if rarityText in translator:
            rarityText = translator[rarityText]

            
        Entries[rarityText] = ''
        while (current_element and current_element != next_rarity):
            try:
                current_element = current_element.find_element(By.XPATH, "following-sibling::*[1]")
            except:
                break
            
            if current_element.tag_name == 'ul' or current_element.tag_name == 'ol':
                list_items = current_element.find_elements(By.TAG_NAME, "li")
                for item in list_items:
                    entryText = item.text
                    if 'specific' in entryText:
                        percentage = re.search(r'.*(\d+)\s*in\s*(\d+).*', entryText)
                        if percentage:
                            first = percentage.group(1)
                            second = percentage.group(2)
                            Entries[rarityText] = int(first)/int(second)
            if current_element.tag_name == 'table':
                rows = current_element.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    rowText = row.text
                    if 'Specific' in rowText:
                        Entries[rarityText] = (rowText)
    print(Entries)
    rows = table_body.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        # Get all cells (td elements) in the row
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 3:
            continue

        Rarity_cell = cells[0]
        bolding = bool(Rarity_cell.find_elements(By.TAG_NAME, "strong"))

        # Extract text from each cell and print it
        rarity = Rarity_cell.text
        rarity = rarity.strip()
        if rarity in translator:
            rarity = translator[rarity]
        chance = cells[1].text
        match = re.search(r"(\d+\.?\d*)(?=%)",chance)
        if match:
            percent=match.group()
            try:
                percent=match.group()
                if (bolding):
                    supertype = rarity
                    data.append({'Rarity':rarity,'Chances':percent,'Subrarities':[],'SpecificRarity':Entries[rarity]})
                elif(supertype):
                    data[-1]['Subrarities'].append({'Rarity':rarity,'Chances':percent,'SpecificRarity':Entries[rarity]}) 
                else:
                    data.append({'Rarity':rarity,'Chances':percent,'Subrarities':[],'SpecificRarity':Entries[rarity]})
            except Exception as e:
                print(f"Error: {e}")
                data.append({'Rarity':rarity,'Chances':chance,'Subrarities':[],'SpecificRarity':"Error"})
                continue
    driver.quit()
    #print(data)
    return (setName,data) 

def upload_image_data(setName):

    setTable = db.reference('Sets2')
    relevantSet = setTable.child(setName)
    cards = Card.where(q=f'set.name:"{setName}"')
    updates = {}
    
    # Loop through cards and prepare the updates
    for card in cards:
        if card.rarity is not None:
            # Update the relevant set with card data
            if card.rarity not in updates:
                updates[card.rarity] = []
            updates[card.rarity].append(card.images.large)
    
    # Perform the update in one go
    if updates:
        setTable.child(setName).update(updates)
    return

if __name__ == "__main__":
    dataCollected = get_articles()
    processes = []
    load_dotenv()
    API_KEY = os.getenv("POKEMON_API_KEY")
    RestClient.configure(API_KEY)
    key_path = os.getenv("FIREBASE_KEY_PATH")
    
    print(f"Using Firebase key path: {key_path}")

    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://pullratetracker-default-rtdb.firebaseio.com'
    })
    try:
        with open('./FrontEnd/pokedata.json', 'r') as file:
            currentdata = json.load(file)
    except FileNotFoundError:
        print("File not found. Creating a new one.")
        currentdata = {}
    currentSets = currentdata.keys()
    dataToParse = {key: value for key, value in dataCollected.items() if key not in currentSets}
    dataToParse = {key: value for key, value in dataToParse.items() if key not in exceptions_list}
    dataToParse = list(dataToParse.items())
    #print(dataToParse)
    if(len(dataToParse) == 0):
        print("No new sets to parse")
    data = []
    for args in dataToParse:
        
        try:
            data.append(get_pullrates(args))
            upload_image_data(args[0])
        except Exception as e:
            print(f"Error: {e}")
    results_dict= {}
    print(data)
    for set,numbers in data:
        results_dict[set] = numbers
    currentdata.update(results_dict)
    with open("./FrontEnd/pokedata.json", "w+") as json_file:
        json.dump(currentdata, json_file, indent=4)

    """
    

for data in dataToParse:
    setName = data[0]
    url = data[1]
    process = Process(target=get_pullrates, args=(url,q))
    process.start()
    processes.append(process)
for process in processes:
    process.join()

"""

"""
for row in dataToParse:
    setName = row[0]
    link = row[1]
    print(link)
    print(setName)
    
    data.append([setName,get_pullrates(link)])
"""

