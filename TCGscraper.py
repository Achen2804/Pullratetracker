import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
from multiprocessing import Pool


def get_articles():
# Headless mode (optional)
    op = Options()
    op.add_argument('--headless')  # Run in headless mode
    op.add_argument('--disable-gpu')  # Disable GPU acceleration (optional)
    driver = webdriver.Chrome(options=op)
    url = "https://infinite.tcgplayer.com/search?q=pull%20rates&p=1&contentMode=article&game=all%20games&ac=1"
    driver.implicitly_wait(10)

    driver.get(url)

    content_container = driver.find_element(By.CSS_SELECTOR, "[data-testid = 'search-results__content-card-grid']")

    relevant_articles = content_container.find_elements(By.XPATH, "//div[@class='grid' and @data-testid='search-results__content-card-grid']//a[@class='martech-base-link'][.//text()[contains(., 'Pokémon TCG')] and .//text()[contains(., 'Pull Rates')]]")
    set_to_link = []
    for article in relevant_articles:
        link = article.get_attribute("href")
        article_title = article.find_element(By.CLASS_NAME,"martech-heading-sm")
        title = article_title.text
        match = re.search(r"Pokémon TCG: (.*?) Pull Rates", title)
        if match:
            setName = match.group(1)
            set_to_link.append([setName,link])
    driver.quit()
    return set_to_link

def get_pullrates(args):
    setName, source = args
    op = Options()
    op.add_argument('--headless')  # Run in headless mode
    op.add_argument('--disable-gpu')  
    driver = webdriver.Chrome(options=op)
    driver.implicitly_wait(5)
    driver.get(source)
    content_container = driver.find_element(By.XPATH, "//table[.//th[contains(text(), 'Rarity') or contains(text(), 'Card Type') or contains(text(), 'Subrarity')]]")
    table_body = content_container.find_element(By.TAG_NAME,"tbody")
    rows = table_body.find_elements(By.TAG_NAME, "tr")
    data = []
    supertype = None
    subtype = None
    # Iterate through each row to get the cells (td elements)
    print(len(rows))
    for row in rows:
        # Get all cells (td elements) in the row
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 3:
            continue

        Rarity_cell = cells[0]
        bolding = bool(Rarity_cell.find_elements(By.TAG_NAME, "strong"))

        # Extract text from each cell and print it
        rarity = Rarity_cell.text
        chance = cells[1].text
        match = re.search(r"(\d+\.?\d*)(?=%)",chance)
        if match:
            percent=match.group()
            if (bolding):
                supertype = rarity
                data.append({'Rarity':rarity,'Chances':percent,'Subrarities':[]})
            elif(supertype):
                data[-1]['Subrarities'].append({'Rarity':rarity,'Chances':percent}) 
            else:
                data.append({'Rarity':rarity,'Chances':percent,'Subrarities':[]})
        
        
        #print(data)
    driver.quit()
    #print(data)
    return (setName,data) 
if __name__ == "__main__":
    dataToParse = get_articles()
    processes = []
    get_pullrates(dataToParse[0])


    with Pool(processes=len(dataToParse)) as pool:
        data = pool.map(get_pullrates, dataToParse)
    results_dict= {}
    print(data)
    for set,numbers in data:
        results_dict[set] = numbers
    with open("./FrontEnd/pokedata.json", "w") as json_file:
        json.dump(results_dict, json_file, indent=4)
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

