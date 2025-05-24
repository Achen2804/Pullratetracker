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
from pokemontcgsdk import Set
from pokemontcgsdk import RestClient
def get_articles():
# Headless mode (optional)
    op = Options()
    op.add_argument('--headless')  # Run in headless mode
    op.add_argument('--disable-gpu')  # Disable GPU acceleration (optional)
    driver = webdriver.Chrome(options=op)
    url = "https://infinite.tcgplayer.com/search?q=pull%20rates&p=1&contentMode=article&game=all%20games&ac=1"
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
    
    content_container = driver.find_element(By.XPATH, "//table[.//th[contains(text(), 'Rarity') or contains(text(), 'Card Type') or contains(text(), 'Subrarity')]]")
    table_body = content_container.find_element(By.TAG_NAME,"tbody")
    
    data = []
    supertype = None
    subtype = None
    
    specificData = {}
    Rarity_Lists = articleBody.find_elements(By.TAG_NAME, "li")
    if(len(Rarity_Lists) == 0):
        Rarity_Lists = articleBody.find_elements(By.TAG_NAME, "table")
        for table in Rarity_Lists:
            rows = table.find_elements(By.TAG_NAME, "tr")
            cells = rows[2].find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                if "Specific" in cells[0].text:
                    match = re.search(r"Specific (.*) Card",cells[0].text)
                    subrarity = match.group(1)
                    match = re.search(r"(\d+) in (\d+) .*",cells[2].text)
                    if match:
                        if(subrarity == "ACE SPEC"):
                            subrarity = "ACE SPEC Rare"
                        first = match.group(1)
                        second = match.group(2)
                        percent = int(first)/int(second)
                        specificData[subrarity] = percent


    else:
        Rarity_Lists = articleBody.find_elements(By.TAG_NAME, "li")
        h2_elements = articleBody.find_elements(By.TAG_NAME, "h2")
        h3_elements = articleBody.find_elements(By.TAG_NAME, "h3")
        Rarities = h2_elements + h3_elements
        index = 0
        for rarityData in Rarity_Lists:
            rarity = Rarities[index]
            cleaned_text = re.sub(r"\(\d+\s*in\s*\d+\)", "", rarity.text)
            if "specific" in rarityData.text:
                index += 1
                match = re.search(r".+: (\d+) in (\d+)",rarityData.text)
                if match:
                    first = match.group(1)
                    second = match.group(2)
                    percent = int(first)/int(second)
                    percent = round(percent*100,2)
                    if(cleaned_text == "Rainbow Rare"):
                        cleaned_text = "Gold Rare"
                    specificData[cleaned_text] = percent
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
        print(f"Rarity: {rarity}, {setName}")
        chance = cells[1].text
        match = re.search(r"(\d+\.?\d*)(?=%)",chance)
        if match:
            percent=match.group()
            if (bolding):
                supertype = rarity
                data.append({'Rarity':rarity,'Chances':percent,'Subrarities':[],'SpecificRarity':specificData[rarity]})
            elif(supertype):
                data[-1]['Subrarities'].append({'Rarity':rarity,'Chances':percent,'SpecificRarity':specificData[rarity]}) 
            else:
                data.append({'Rarity':rarity,'Chances':percent,'Subrarities':[],'SpecificRarity':specificData[rarity]})
    driver.quit()
    #print(data)
    return (setName,data) 

def upload_image_data(setName):

    #print(ref.get())
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
    #get_pullrates(dataToParse[0])
    #print(dataCollected)
    load_dotenv()
    API_KEY = os.getenv("POKEMON_API_KEY")
    RestClient.configure(API_KEY)
    key_path = os.getenv("FIREBASE_KEY_PATH")
    


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
    dataToParse = list(dataToParse.items())
    #print(dataToParse)
    if(len(dataToParse) == 0):
        print("No new sets to parse")
        exit(0)
    data = []
    try:
        for args in dataToParse:
            data.append(get_pullrates(args))
    except Exception as e:
        print(f"Error: {e}")
    results_dict= {}
    #print(data)
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

