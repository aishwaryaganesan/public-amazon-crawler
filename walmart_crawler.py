import sys
import eventlet
import settings
from helpers import make_request, log, format_url
from extractors import get_title, get_url, get_price, get_primary_img
from collections import deque
from datetime import datetime
import pickle

crawl_time = datetime.now()
pool = eventlet.GreenPool(settings.max_threads)
pile = eventlet.GreenPile(pool)
queue = deque()
product_list = []

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
        print str(len(product_list)+1) + "\t" + self.pretty_print()
        product_list.append(self)
        if (len(product_list) >= settings.total_crawl):
            pickle.dump(product_list, open("products.p", "wb" ))
            sys.exit(0)

def enqueue_url(url):
    queue.append(url)

def dequeue_url():
    return queue.popleft() 

def begin_crawl():
    # explode out all of our category `start_urls` into subcategories
    with open(settings.start_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip blank and commented out lines
            page, html = make_request(line)
            count = 0
            # look for subcategory links on this page
            subcategories = page.findAll("div", "bxc-grid__image")  # downward arrow graphics
            subcategories.extend(page.findAll("li", "sub-categories__list__item"))  # carousel hover menu
            sidebar = page.find("div", "browseBox")
            if sidebar:
                subcategories.extend(sidebar.findAll("li"))  # left sidebar

            for subcategory in subcategories:
                link = subcategory.find("a")
                if not link:
                    continue
                link = link["href"]
                count += 1
                enqueue_url(link)
            log("Found {} subcategories on {}".format(count, line))

def fetch_listing():
    global crawl_time
    url = dequeue_url()
    if not url:
        log("WARNING: No URLs found in the queue. Retrying...")
        pile.spawn(fetch_listing)
        return

    	session = dryscrape.Session()
	session.visit(url)
	response = session.body()
	soup = BeautifulSoup(response, "html5lib")

	# title
	product_title = soup.find('h1',{'class':'prod-ProductTitle no-margin heading-a'}).get_text()

	# price
	try:
		box = soup.find('div',{'class','prod-BotRow prod-showBottomBorder prod-OfferSection prod-OfferSection-twoPriceDisplay'})
		product_price = box.find('span',{'class':'Price-group'}).get_text()
	except:
		product_price = 'N/A'
		pass
	product_url = url

	# get properties
	try:
		keys = []
		for s in soup.findAll("td", "ComparisonKey-cell"):
			s = s.get_text().strip('')
			try:
				# Keep ascii chars.
				ss = ''.join([c for c in s if ord(c) < 128])
				if len(ss):
					keys.append(ss)
			except UnicodeEncodeError:
				pass

		values = []
		for s in soup.findAll("table", "comparison-values table no-margin")[0].findAll("td"):
			s = s.get_text().strip()
			try:
				# Keep ascii chars.
				ss = ''.join([c for c in s if ord(c) < 128])
				if len(ss):
					values.append(ss.strip(''))
			except UnicodeEncodeError:
				pass

		properties = {k:v for k,v in zip(keys, values)}

		if not len(properties):
			raise "Empty properties"

		# print properties

	except Exception as e:
		properties = {}
		for tr in soup.find("tbody").findAll("tr"):
			properties[tr.find('th').get_text()] = tr.find('td').get_text()
		# print properties


	product = ProductRecord(
		title=product_title,
		product_url=product_url,
		price=product_price,
		properties=properties
	)

    product.save()



    # add next page to queue
    # TODO
    # next_link = page.find("a", id="pagnNextLink")
    # if next_link:
    #     log(" Found 'Next' link on {}: {}".format(url, next_link["href"]))
    #     enqueue_url(next_link["href"])
    #     pile.spawn(fetch_listing)

if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "start":
        log("Seeding the URL frontier with subcategory URLs")
        begin_crawl()  # put a bunch of subcategory URLs into the queue

        log("Beginning crawl at {}".format(crawl_time))
        [pile.spawn(fetch_listing) for _ in range(settings.max_threads)]
        pool.waitall()
    else:
        print "Usage: python crawler.py start"
