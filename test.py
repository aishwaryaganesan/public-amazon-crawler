from helpers import make_request
import json

url = "https://www.walmart.com/ip/ELAIO-17-3-Touchscreen-All-In-One-4GB-Memory-32GB-Hard-Drive-Intel-Atom-Celeron-Processor-with-Windows-10-Home-Silver/56148677"
url = "https://www.walmart.com/ip/Lenovo-Gaming-Laptop-15-6-FHD-Screen-Intel-core-i7-7700hq-2-8-3-8-GHZ-Nvidia-GeForce-GTX-1050-Ti-Graphic-Card-8GB-DDR4-Memory-1TB-HDD-80WK00T2US/366996887"
value =  make_request(url)
try:
    page, html = value[0], value[1]
except:
    print(value)
    exit(1)

text = str(page)
while text.find("\n!function()") > 0:
    a = text.find("\n!function()")
    b = text.find("\n", a+1)
    line = text[a:b]
    c = line.find("Specifications\":{")

    if c >= 0:
        line = line[c:]
        stack = []
        for i in range(len(line)):
            if line[i] == '{':
                stack.append('{')
            elif line[i] == '}':
                stack.pop()
                if len(stack) == 0:
                    final = line[len("Specifications\":"):i+1]
                    break

        d = json.loads(final)['specifications']['values'][0]
        # print(d)  
        for i in d:
            for key in i.keys():
                v = i[key]
                print(v['displayName'] + ' : ' + v['displayValue'])



    text = text[b:]
    # page.find("Specifications")