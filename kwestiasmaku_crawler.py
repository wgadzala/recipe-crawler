import re
import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
import time
import random
from proxyscrape import create_collector

# the header could be replaced using fake_useragent module
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
}

# initializing proxy list collector
collector = create_collector("my-collector", "http")
raw_data = collector.get_proxies()
home_page = "https://www.kwestiasmaku.com"

# storing a queue of internal links for processing
internal_links =  set()

def parse_html(url):
    # listing proxy ip, port to be fed into requests
    proxies = []
    for i in raw_data:
      proxies.append(str(i[0]) + ":" + str(i[1]))

    # selecting random proxy ip, port
    def random_proxy():
        return random.randint(0, len(proxies) - 1)
    proxy_index = random_proxy()
    print("Feeding " + proxies[proxy_index])
    proxy = {
     "http": "http://{}".format(proxies[proxy_index]),
     "https": "http://{}".format(proxies[proxy_index]),
    }

    # looping through proxies until successful connection
    while True:
        try:
            page_data = requests.get(urljoin(home_page, url), proxies=proxy, headers=HEADERS).content
            soup = BeautifulSoup(page_data, "html.parser")
            return soup
            break

        # If error, proxy is deleted and a new random is being fed into requests
        except Exception as e:
            print(e)
            print("Proxy: " + proxies[proxy_index] + " deleted.")
            del proxies[proxy_index]
            proxy_index = random_proxy()
            print("Processing: "+ proxies[proxy_index])
            proxy = {
             "http": "http://{}".format(proxies[proxy_index]),
             "https": "http://{}".format(proxies[proxy_index]),
            }

# recipe scrapers below
def get_title(soup):
    title = soup.find(
        'h1',
        {'class':'page-header'}
    ).get_text().strip()
    print(title)

def get_portions(soup):
    portions = soup.find(
        'div',
        {'class':'field field-name-field-ilosc-porcji field-type-text field-label-hidden'}
    ).get_text().strip()
    print(portions)

def get_ingredients(soup):
    """
    Some recipe pages divide ingredient list into sub-lists for each food component
    (e.g. dough, cream, icing for a cake); in such case the func will return a dictionary
    with the component names as keys and ingredient lists as values.

    If ingredients are not broken down into sub-list, the func will return a list.
    """

    ingredient_bar = soup.find(
        'div',
        {'class': 'field field-name-field-skladniki field-type-text-long field-label-hidden'})

    component_list = [component_name.get_text().strip() for component_name in ingredient_bar.find_all('div')]

    if len(component_list) > 0:
        component_ingredients = []
        for ul in ingredient_bar.find_all('ul'):
            component_ingredients.append([li.get_text().strip() for li in ul.find_all('li')])
        ingredients = dict(zip(component_list, component_ingredients))

    else:
        ingredients = [ingredient.get_text().strip() for ingredient in ingredient_bar.find_all('li')]

    print(ingredients)

def get_instructions(soup):
    instruction_list = soup.find(
                'div',
                {'class': 'field field-name-field-przygotowanie field-type-text-long field-label-above'}
                ).find_all('li')

    instructions = []
    for li in instruction_list:
        instructions.append(li.get_text().strip())

    instructions = "\n".join(instructions)

    print(instructions)

def get_image(soup):
    image = soup.find(
            'div',
            {'class': 'field field-name-zdjecie-z-linikem-do-bloga field-type-ds field-label-hidden'}
    ).img['src']

    print(image)

def get_rating(soup):
    rating = round(float(soup.find('span', {'class': 'average-rating'}).span.get_text()), 2)

    print(rating)

# main scraper functiom
def scraper(url):
    soup = parse_html(url)
    # only scrape recipe (pl: 'przepis') pages:
    if url.startswith("/przepis/"):
        get_title(soup)
        # exception handling as some recipes do not provide portions
        try:
            get_portions(soup)
        except Exception as e:
            print(e)
            pass
        get_ingredients(soup)
        get_instructions(soup)
        get_image(soup)
        get_rating(soup)

    # extracting all internal links and storing them in a queue for later processing
    for link in soup.findAll("a", href=re.compile("^(/)")):
        if "href" in link.attrs:
            #
            if link.attrs["href"] not in internal_links:
                new_link = link.attrs['href']
                internal_links.add(new_link)
                print("Processing %s" % new_link)
                # crawl-delay can be implemented
                # time.sleep(10)
                scraper(new_link)

scraper(home_page)
