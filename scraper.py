from bs4 import BeautifulSoup
import requests
import csv
import re
import sys


class SearchScraper():
    def __init__(self, search_term, num_pages, search_type):
        self.cur_page = 1
        self.total_pages = num_pages
        self.search_term = search_term.replace(" ","+")
        if search_type != "Detailed":
            self.search_type = "Quick"
        else:
            self.search_type = "Detailed"
        self.baseUrl = f"https://www.etsy.com/search?q={search_term}"
        self.url = self.baseUrl
        self.headers = {'User-Agent':'Mozilla/5.0 ' +
            '(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' + 
            '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
        self.data = []
        self.num_requests = 0
        self.fields = ["item_name", "item_id", "shop_name", "shop_id", 
            "shop_reviews", "price", "on_sale", "sale_price", "image", "link", "tags"]

    # Requests the search webpage and creates a BeautifulSoup object
    def get_request(self):
        self.num_requests += 1
        page = requests.get(self.url, headers = self.headers).content
        self.doc = BeautifulSoup(page, "lxml")

    # Requests a listing webpage and creates a BeautifulSoup object
    def get_list_request(self, item_id):
        url = "https://www.etsy.com/listing/" + str(item_id)
        page = requests.get(url, headers = self.headers).content
        self.listing_doc = BeautifulSoup(page, "lxml")

    # Changes the url to the url for the next page of search results
    def pagination(self):
        self.cur_page += 1
        self.url = self.baseUrl + f"%page={self.cur_page}&ref=pagination"

    # Gets all listing containers
    def get_listings(self):
        parent = self.doc.find("div","wt-bg-white wt-display-block wt-pb-xs-2 wt-mt-xs-0")
        self.listings = parent.find_all("div", class_=re.compile("^js-merch"))
    
    # Searches for the tags in a listing and returns a list of the tags
    def search_listing(self):
        cur_html = self.listing_doc.find("div", 
            class_ = "tags-section-container " + 
            "tag-cards-section-container-with-images")
        tag_html = cur_html.find_all("li", class_ ="wt-display-flex-xs " + 
            "wt-flex-direction-column-xs wt-ml-xs-1 wt-mr-xs-1 wt-mt-xs-2 " + 
            "wt-mb-xs-4")
        tags = []
        for tag in tag_html:
            tags.append(tag.text.strip())
        return tags
    
    # Loops through all listings on the page and gets the data for each listing
    # If "Detailed" mode is turned on, it will also find the tags of each
    # listing
    def iterate(self):
        for listing in self.listings:
            i_data = {}
            a = listing.find("a")
            i_data["item_id"] = a.get("data-listing-id")
            i_data["item_name"] = a.get("title")
            i_data["shop_name"] = listing.find("span", 
                text=re.compile("^From shop")).string[10:]
            i_data["shop_id"] = a.get("data-shop-id")
            reviews = listing.find("span",
                class_="wt-text-body-01 wt-nudge-b-1 " +
                "wt-text-gray wt-display-inline-block" + 
                " wt-nudge-l-3 wt-pr-xs-1")
            # handles error due to reviews not being displayed on some shops
            if reviews != None:
                i_data["shop_reviews"] = reviews.string.strip()[1:-1]
                i_data["shop_reviews"] = int(i_data["shop_reviews"]
                    .replace(',',''))
            else:
                reviews = "N/A"
            prices = listing.find_all("span", class_="currency-value")
            i_data["price"] = float(prices[0].string.replace(',',''))
            # adds sale price to data if on sale
            if len(prices) > 1:
                i_data["on_sale"] = True
                i_data["sale_price"] = float(prices[1]
                    .string.replace(',',''))
            else:
                i_data["on_sale"] = False
                i_data["sale_price"] = "N/A"
            i_data["image"] = listing.find("img").get("src")
            i_data["link"] = a.get("href")
            # detailed view adds tags to data by requesting the listing page
            if (self.search_type == "Detailed"):
                self.get_list_request(i_data["item_id"])
                if self.listing_doc != None:
                    tags = self.search_listing()
                    i_data["tags"] = ', '.join(tags)
            self.data.append(i_data)
            
    # Export the data to a csv file
    def export_csv(self):
        with open('output.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = self.fields)
            writer.writeheader()
            writer.writerows(self.data)

    # Executes the scraper
    def execute(self):
        while (self.cur_page <= self.total_pages 
               and self.num_requests < self.total_pages):
            self.get_request()
            self.get_listings()
            self.iterate()
            self.pagination()
        self.export_csv()
     


def main():
    args = sys.argv[1:]
    result = SearchScraper(args[0], int(args[1]), args[2])
    result.execute()

if __name__ == "__main__":
    main()
