import dryscrape
from bs4 import BeautifulSoup
session = dryscrape.Session()
session.visit('https://www.walmart.com/ip/Samsung-32-Class-HD-720P-LED-TV-UN32J4002/843122266')
response = session.body()
soup = BeautifulSoup(response)
comparison_table = soup.findAll("table", "comparison-values table no-margin")[0]
keys = []
for i in soup.findAll("td", "ComparisonKey-cell"):
	try:
		print (str(i.get_text().strip('')))
		keys.append(str(i.get_text().strip('')))
	except UnicodeEncodeError:
		pass

values = []
for i in comparison_table.findAll("td"):
	try:
		print (str(i.get_text().strip('')))
		values.append(str(i.get_text().strip('')))
	except UnicodeEncodeError:
		pass

print (keys)
print (values)

properties = {}
for i in range(len(keys)):
	properties[keys[i]] = values[i]
print properties