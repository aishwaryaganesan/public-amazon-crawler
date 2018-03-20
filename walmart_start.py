from helpers import make_request, log, format_url

url = 'https://www.walmart.com/browse/electronics/tvs/3944_1060825_447913?povid=3944+%7C+contentZone2+%7C+2016-10-21+%7C+1+%7C+Shop_by_Cat_TVs'
page, html = make_request(url)
for item in page.findAll("div", "search-result-gridview-item clearfix"):
	print(item.find('a')['href'])