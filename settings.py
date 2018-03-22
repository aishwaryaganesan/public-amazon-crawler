import os
current_dir = os.path.dirname(os.path.realpath(__file__))

# Request
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
}
allowed_params = ["node", "rh", "page"]

# Proxies
proxies = [
    # your list of proxy IP addresses goes here
    # check out https://proxybonanza.com/?aff_id=629
    # for a quick, easy-to-use proxy service
]
proxy_user = ""
proxy_pass = ""
proxy_port = ""

# Crawling Logic
start_file = os.path.join(current_dir, "start-urls.txt")
w_start_file = os.path.join(current_dir, 'w-start-urls.txt')
w_URL_file = os.path.join(current_dir, 'walmart-product-URLs.txt')
w_products_path = os.path.join(current_dir, 'walmart_products/')
max_requests = 2 * 10**6  # two million
max_details_per_listing = 9999

# Threads
max_threads = 20

# Logging & Storage
log_stdout = True

#total items to crawl
total_crawl = 3000
host = "www.amazon.com"
w_host = 'www.walmart.com'