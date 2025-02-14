import requests
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


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

def get_pullrates(source):
    op = Options()
    op.add_argument('--headless')  # Run in headless mode
    op.add_argument('--disable-gpu')  # Disable GPU acceleration (optional)
    driver = webdriver.Chrome(options=op)
    driver.implicitly_wait(5)

    driver.get(source)
    content_container = driver.find_element(By.TAG_NAME, "table")
    row_container = content_container.find_element(By.TAG_NAME, "tbody")
    rows = row_container.find_elements(By.TAG_NAME, "tr")

    # Iterate through each row to get the cells (td elements)
    for row in rows:
        # Get all cells (td elements) in the row
        cells = row.find_elements(By.TAG_NAME, "td")
        # Extract text from each cell and print it
        rarity = cells[0].text
        chance = cells[1].text
        match = re.search(r"(\d+\.?\d*)(?=%)",chance)
        if match:
            percent=match.group()
            print(rarity)
            print(percent +" Pull rate")
        
    #print("done")
    driver.quit()

    return 

dataToParse = get_articles()

for row in dataToParse:
    setName = row[0]
    link = row[1]
    print(link)
    print(setName)
    get_pullrates(link)
"""
"""

