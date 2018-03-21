import sys
import eventlet
import settings
from helpers import make_request, log, format_url
from collections import deque
from datetime import datetime
import pickle
import dryscrape
from bs4 import BeautifulSoup

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
    with open(settings.w_start_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip blank and commented out lines
            url = line
            page, html = make_request(line)
            count = 0

            i = 1 # starting page
            while page != None:
                print 'page %d of link: %s' %(i, line)
                # look for products listed on this page
                results = page.findAll('div', 'search-result-gridview-item clearfix')  # items in gridview

                for result in results:
                    link = result.find('a')
                    if not link:
                        continue
                    link = link['href']
                    count += 1
                    enqueue_url(link)
                
                i += 1
                # go to list of pages at bottom    
                p_list = page.find('ul', 'paginator-list').findAll('li')
                for p in p_list:
                    # search for 'next' ordinal page
                    if not p.has_attr('class') and str(i) in p.find('a').text:
                        next_page = '?page=%d#searchProductResult' % i # href is wrong because it is dynamically generated
                        url = line + next_page
                        page, html = make_request(url)
                        break
                    else:
                        page = None

            log("Found {} results on {}".format(count, line))

def fetch_listing():
	global crawl_time
	url = dequeue_url()
	if not url:
		log("WARNING: No URLs found in the queue. Retrying...")
		pile.spawn(fetch_listing)
		return

	# need to add host to url
	url = format_url(url, walmart=True)

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
        print "Usage: python walmart_crawler.py start"
