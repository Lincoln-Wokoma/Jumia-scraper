from datetime import datetime
import requests
import csv
import bs4
import concurrent.futures
from tqdm import tqdm

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
REQUEST_HEADER = {
    "User-Agent" : USER_AGENT,
    "Accept-Language" : "en-US, en;q=0.5"
}

NO_THREADS = 10

def get_page_html(url):
    res = requests.get(url=url, headers =REQUEST_HEADER)
    return res.content



def get_product_price(soup):
    main_price_span = soup.find('div', attrs={'class': "df -i-ctr -fw-w"})
    price_spans = main_price_span.findAll('span')
    for span in price_spans:
        price = span.text.strip().replace(',', '').replace('₦', '')
        try:
            return float(price)
        except ValueError:
            print('Value obtained for price could not be parsed')
            exit()

def get_product_name(soup):
      name = soup.find('h1', attrs={'class': "-fs20 -pts -pbxs"}).text.strip()
      return name


def get_product_rating(soup):
    product_rating_div = soup.find('div', attrs = {'class':'-df -i-ctr -pbs'})
    product_rating_sub = product_rating_div.findAll('div')
    for div in product_rating_sub:
        try:
            product_rating_percent = div.text.strip()
            product_str = product_rating_percent.split(" ")
            product_rating = product_str[0]
            if float(product_rating) > 0:
                return product_rating
            else:
                return 'Rating not available'
            
        except:
            return 'Rating not available'
        

def get_product_description(soup):
    description = {}
    description_section = soup.find('div', class_ = 'row -pas')
    description_box_1 = description_section.find('div', class_ = "markup -pam")
    description_box1 = description_box_1.findAll('li')
    for items in description_box1:
        box_details = items.text.strip().split(':')
        description[box_details[0]]  = box_details[-1]
    description_box_2 = description_section.find('ul', attrs = {'class': '-pvs -mvxs -phm -lsn'})
    description_box2 = description_box_2.findAll('li', class_ = '-pvxs')
    for items in description_box2:
        box_details = items.text.strip().split(':')
        description[box_details[0]] = box_details[1]
    return description


    
                  
    
def extract_product_info(url, output):
    product_info = {}
    #print(f'Scraping URL: {url}')
    html = get_page_html(url = url)
    soup = bs4.BeautifulSoup(html, "lxml")
    product_info["price"] = get_product_price(soup)
    product_info["Name"] = get_product_name(soup)
    product_info["Rating"] = get_product_rating(soup)
    product_info.update(get_product_description(soup))
    output.append(product_info)


if __name__ == "__main__":
    products_data = []
    urls = []
    with open("amazon_products_urls.csv", newline="") as csvfile:
        urls = list(csv.reader(csvfile, delimiter=",")) 
    with concurrent.futures.ThreadPoolExecutor(max_workers = NO_THREADS) as executor:
        for wkn in tqdm(range(0, len(urls))):
            executor.submit(extract_product_info, urls[wkn][0], products_data)
    output_file_name = 'output-{}.csv'.format(
            datetime.today().strftime('%m-%d-%Y'))
    with open(output_file_name, 'w') as outputfile:
            writer = csv.writer(outputfile)
            writer.writerow(products_data[0].keys())
            for product in products_data:
                writer.writerow(product.values())
