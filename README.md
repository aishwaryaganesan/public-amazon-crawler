## Getting it Setup
[dryscrape dependency] - do this first
sudo apt-get install qt5-default libqt5webkit5-dev build-essential python-lxml python-pip xvfb
sudo pip install dryscrape

After you get a copy of this codebase pulled down locally (either downloaded as a zip or git cloned), you'll need to install the python dependencies:

    pip install -r requirements.txt

Then you'll need to go into the `settings.py` file and update a number of values:
 * total_crawl - no of total products to crawl
 * start_file - start urls for amazon
 * w_start_file - start urls for walmart
 * a_products_path - path to dump pickled amazon product files
 * a_URL_file - file to dump the list of URLs
## How it Works
You begin the crawler for the first time by running:

    python amazon_crawler.py crawl

Or,if using the walmart crawler:
    
    xvfb-run python walmart_crawler.py start  

This looks at the laptop category start URL stored in the `start-urls.txt` file, and get all the product URLs from that page and then visits the next page by looking for the link to next page on the current web page and so on till it finds total_crawl number of product URLs. The list of URLs is dumped into a_URL_file or w_URL_file for amazon and walmart respectively.

To crawl products, 
    
    python amazon_crawler.py start begin_index end_index

This will crawl all the product pages using the URLs in a_URL_file from begin_index to end_index and dump each product information into a pickle file.

The fields that are stored for each product are the following:
 * title
 * product_url *(URL for the detail page)*
 * price
 * dictionary of product properties like average battery life, brand, color, display resolution, operating system, processor (cpu) manufacturer,processor count, etc.


Finally, merge_columns.py produces a uniform schema for both amazon and walamrt
