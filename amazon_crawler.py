import sys
import settings
from helpers import make_request, format_url
from collections import deque
from datetime import datetime
import pickle
from HTMLParser import HTMLParser
htmlparser = HTMLParser()

crawl_time = datetime.now()
queue = deque()
product_list = []
product_urls = []

class ProductRecord(object):
    def __init__(self, title, product_url, price, properties):
        super(ProductRecord, self).__init__()
        self.title = title
        self.product_url = product_url
        self.price = price
        self.properties = properties

    def pretty_print(self):
        return self.title  + ":" +  str(self.price) + ":" +str(self.properties.keys())

    def save(self):
        product_list.append(self)

def enqueue_url(url):
    queue.append(url)

def dequeue_url():
    return queue.popleft() 

def get_title(item):
    title = item.find("h2", "s-access-title")
    if title:
        return htmlparser.unescape(title.text.encode("utf-8"))
    else:
        return "<missing product title>"

def get_url(item):
    link = item.find("a", "s-access-detail-page")
    if link:
        return link["href"]
    else:
        return "<missing product url>"

def get_price(item):
    price = item.find("span", "s-price")
    if price:
        return price.text
    return None

def get_primary_img(item):
    thumb = item.find("img", "s-access-image")
    if thumb:
        src = thumb["src"]

        p1 = src.split("/")
        p2 = p1[-1].split(".")

        base = p2[0]
        ext = p2[-1]

        return "/".join(p1[:-1]) + "/" + base + "." + ext
    return None

def begin_crawl(crawl_more):

    visited = {}
    product_dict = {}
    if crawl_more:
        with open('amazon-products.p', 'rb') as pf:
            product_dict = pickle.load(pf)

        with open(settings.a_URL_file, 'r') as w:
            urls = (w.readlines())
        for url in urls:
            url = url.strip()
            visited[url] = True

    w = open(settings.a_URL_file, 'a')
    with open(settings.start_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip blank and commented out lines
            page, html = make_request(line)
            url = line
            count = 0
            while page != None and count <= 50:
                items = page.findAll("li", "s-result-item")
                for item in items[:settings.max_details_per_listing]:
                    product_image = get_primary_img(item)
                    if not product_image:
                        continue
                    product_title = get_title(item)
                    product_url = get_url(item)
                    product_price = get_price(item)
                    if product_url not in visited:
                        count += 1
                        print product_url, product_price, product_title
                        visited[product_url] = True # mark that we've seen it
                        # need to add host to url
                        product_url = format_url(product_url)
                        w.write('%s\n' % product_url)
                        product_dict[product_url] = (product_title, product_price)
                        print count, product_url, product_dict[product_url]

                next_link = page.find("a", id="pagnNextLink")
                if next_link:
                    page, html = make_request(next_link["href"])
                    url = next_link["href"]
    w.close()
    pickle.dump(product_dict, open("amazon-products.p", "wb" ))

def gather_urls(start, end):
    with open(settings.a_URL_file, 'r') as w:
        urls = (w.readlines()[start:end])
    i = start
    for url in urls:
        url = url.strip()
        product_urls.append(url)
        i += 1

def print_product(index):
    file = '%s%d.p' % (settings.a_products_path, index)
    with open(file, 'rb') as f:
        product = pickle.load(f)

    print product.title
    print product.price
    print product.properties

def fetch_listing(start, end):
    global crawl_time
    with open('amazon-products.p', 'rb') as pf:
        product_dict = pickle.load(pf)
    index = start-1
    count = 0
    for product_url in product_urls:
        #print product_url
        index += 1
        page1, html1 = make_request(product_url)
        try:
        # visit the page specified by product_url
            temp_dict = {}
            product_title = product_dict[product_url]
            product_price = page1.find("span", "a-size-medium a-color-price").get_text().strip()

            #extract product info from comparison_table
            table = page1.find("table", "a-bordered a-horizontal-stripes a-spacing-mini a-size-base comparison_table")
            for i in table.findAll("tr"):
                if "a-span3 comparison_attribute_name_column comparison_table_first_col" in str(i):
                    k = i.find("td").find("span").get_text()
                    v = i.find("th").find("span").get_text()
                    temp_dict[v] = k

            #extract product info from product details Table
            tables = page1.findAll("table", "a-keyvalue prodDetTable")
            for table2 in tables:
                for i in table2.findAll("tr"):
                    k = i.find("td").get_text().strip()
                    v = i.find("th").get_text().strip()
                    temp_dict[v] = k

            product = ProductRecord(
            title=product_title,
            product_url=format_url(product_url),
            price=product_price,
            properties=temp_dict
            )
            product_name = settings.a_products_path +  str(index) + ".p"
            pickle.dump(product, open(product_name, 'wb'))
            #print_product(index)
            count += 1
            print (count, index, product_price)
            sys.stdout.flush()
        except Exception as e:
            print "Exception##:" +str(index) + '\t' + str(e)
        
        
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "crawl":
        begin_crawl(crawl_more = False)
    elif len(sys.argv) > 1 and sys.argv[1] == "start":
        gather_urls(int(sys.argv[2]), int(sys.argv[3]))
        fetch_listing(int(sys.argv[2]), int(sys.argv[3]))
    else:
        print "Usage: python walmart_crawler.py start"
