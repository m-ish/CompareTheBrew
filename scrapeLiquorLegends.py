from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import concurrent.futures as threadingPool
from classItem import Item, ItemCollection
import logging

def download_liquorland(url, target_filename, filename_extension, total, listBWS):
    """
    Function to parse BWS site (circa November 2019) and return all drinks
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    drinks = soup.findAll('div', {'class':'productTile'})
    print('SCRAPED ' + str(len(drinks)))
    threads = 0
    with threadingPool.ThreadPoolExecutor(max_workers=3) as executor:
        for item in drinks:
            print("INIT_THREAD[" + str(threads) + "]")
            threads += 1
            executor.submit(item_thread_liquorland, item, listBWS)


def item_thread_liquorland(item, ):
    """
    Thread function to control parsing of BWS drink details
    """
    # brand
    brand = item.find('h2', {'class': 'productTile_brand ng-binding'})
    # name
    name = item.find('div', {'class': 'productTile_name ng-binding'})
    # price
    dollar = item.find('span', {'class': 'productTile_priceDollars ng-binding'})
    cents = item.find('span', {'class': 'productTile_priceCents ng-binding'})
    price = str(dollar.text) + '.' + str(cents.text)
    # link
    link = item.find('a', {'class':'link--no-decoration'})

    # alcohol content
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://bws.com.au" + link['href'])
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    detailsRaw = soup.find('div', {'class':'product-additional-details_container text-center ng-isolate-scope'})
    list = detailsRaw.find('ul', {'class':'text-left'})
    keys = list.findAll('strong', {'class':'list-details_header ng-binding'})
    values = list.findAll('span', {'class':'pull-right list-details_info ng-binding ng-scope'})
    details = dict()
    for x in range(0, len(keys)):
        details[keys[x].text] = values[x].text

    size = 0
    if details['Liquor Size'].find('mL') != -1:
        # measurement in mL
        strSize = details['Liquor Size'][0:len(details['Liquor Size']) - 2]
        size = int(strSize) / 1000
    else:
        # measurement in L
        strSize = details['Liquor Size'][0:len(details['Liquor Size']) - 1]
        size = int(strSize)

    efficiency = float(details['Standard Drinks']) / float(price)

    entry = Item("BWS", brand.text, name.text, price, "https://bws.com.au" + link['href'], details['Liquor Size'],
                 details['Alcohol %'], details['Standard Drinks'], efficiency)

    listBWS.append(entry)
    print("FOUND: " + entry.name + " " + entry.stdDrinks + " " + entry.price + " " + str(size) + " " + str(price) + " " + efficiency)