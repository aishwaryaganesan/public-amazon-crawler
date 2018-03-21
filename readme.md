# Amazon Crawler
A relatively simple amazon.com crawler written in python. It has the following features:
 * supports hundreds of simultaneous requests, depending on machine's limits
 * supports using proxy servers
 * supports scaling to multiple machines orchestrating the crawl and keeping in sync
 * can be paused and restarted without losing its place
 * logs progress and warning conditions to a file for later analysis

It was used to pull over 1MM+ products and their images from amazon in a few hours. [Read more]().

## Getting it Setup

[dryscrape dependency] - do this first
sudo apt-get install qt5-default libqt5webkit5-dev build-essential python-lxml python-pip xvfb
sudo pip install dryscrape

After you get a copy of this codebase pulled down locally (either downloaded as a zip or git cloned), you'll need to install the python dependencies:

    pip install -r requirements.txt

Then you'll need to go into the `settings.py` file and update a number of values:
 * **Proxy List as well as User, Password and Port** - Connection information for your list of proxy servers
 * **total_crawl - no of total items to crawl

## How it Works
You begin the crawler for the first time by running:

    python crawler.py start

If using the walmart crawler:

    xvfb-run python walmart_crawler.py start

This runs a function that looks at all of the category URLs stored in the `start-urls.txt` file, and then explodes those out into hundreds of subcategory URLs it finds on the category pages. Each of these subcategory URLs is placed in the redis queue that holds the frontier listing URLs to be crawled.

Then the program spins up the number of threads defined in `settings.max_threads` and each one of those threads pops a listing URL from the queue, makes a request to it and then stores the (usually) 10-12 products it finds on the listing page. It also looks for the "next page" URL and puts that in the queue.

The fields that are stored for each product are the following:
 * title
 * product_url *(URL for the detail page)*
 * listing_url *(URL of the subcategory listing page we found this product on)*
 * price
 * primary_img *(the URL to the full-size primary product image)*
 * crawl_time *(the timestamp of when the crawl began)*

**We additionally get the page pointed by product_url and collect product info from comparison_table and product details table

The products are pickled into a pickle file.

## Known Limitations
Amazon uses many different styles of markup depending on the category and product type. This crawler focused mostly on the "Electronics" category.
The extractors for finding product listings and their details will likely need to be changed to crawl different categories, or as the site's markup changes over time.
