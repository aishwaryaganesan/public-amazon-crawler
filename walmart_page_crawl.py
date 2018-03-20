import dryscrape
from bs4 import BeautifulSoup
from walmart_crawler import ProductRecord


def main():
	url = 'https://www.walmart.com/ip/Epik-Teqnio-ELL1201T-12-5-Laptop-Windows-10-Home-Intel-Atom-x5-Z8350-Processor-2GB-RAM-32GB-Flash-Drive/55474689?action=product_interest&action_type=title&beacon_version=1.0.2&bucket_id=irsbucketdefault&client_guid=2958b3c2-d328-4b97-3eca-f8bd4754ca28&config_id=2&customer_id_enc&findingMethod=p13n&guid=2958b3c2-d328-4b97-3eca-f8bd4754ca28&item_id=55474689&parent_anchor_item_id=55358399&parent_item_id=55358399&placement_id=irs-2-m2&reporter=recommendations&source=new_site&strategy=PWVUB&visitor_id=UKeUDDZV8YPnOASxRYRKhg'
	# different type of table in 2nd link
	url = 'https://www.walmart.com/ip/Samsung-32-Class-HD-720P-LED-TV-UN32J4002/843122266'
	session = dryscrape.Session()
	session.visit(url)
	response = session.body()
	soup = BeautifulSoup(response, "html5lib")

	# title
	try:
		product_title = soup.find('h1',{'class':'prod-ProductTitle no-margin heading-a'}).get_text()
	except:
		product_title = 'N/A'
	# price
	try:
		box = soup.find('div',{'class','prod-BotRow prod-showBottomBorder prod-OfferSection prod-OfferSection-twoPriceDisplay'})
		product_price = box.find('span',{'class':'Price-group'}).get_text()
	except:
		product_price = 'N/A'
		pass

	# url
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
		try:
			for tr in soup.find("tbody").findAll("tr"):
				properties[tr.find('th').get_text()] = tr.find('td').get_text()
		# print properties
		except:
			pass

	product = ProductRecord(
		title=product_title,
		product_url=product_url,
		price=product_price,
		properties=properties
	)

	print(product_title)
	print(product_url)
	print(product_price)
	print(properties)



if __name__=='__main__':
	main()
