from bs4 import BeautifulSoup
import requests
import csv
import re
import sys


class Scraper():
    def __init__(self, search_term, num_pages):
        self.cur_page = 1
        self.total_pages = num_pages
        self.search_term = search_term.replace(" ","+")
        self.baseUrl = f"https://www.etsy.com/search?q={search_term}"
        self.url = self.baseUrl
        self.headers = {'User-Agent':'Mozilla/5.0 ' +
            '(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' + 
            '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
        self.data = []
        self.num_requests = 0

    def get_request(self):
        self.num_requests += 1
        page = requests.get(self.url, headers = self.headers).content
        self.doc = BeautifulSoup(page, "lxml")

    def pagination(self):
        self.cur_page += 1
        self.url = self.baseUrl + f"%page={self.cur_page}&ref=pagination"

    def get_listings(self):
        parent = self.doc.find("div","wt-bg-white wt-display-block wt-pb-xs-2 wt-mt-xs-0")
        self.listings = parent.find_all("div", class_=re.compile("^js-merch"))
    
    def iterate(self):
        for listing in self.listings:
            i_data = {}
            a = listing.find("a")
            i_data["item_name"] = a.get("title")
            i_data["item_id"] = a.get("data-listing-id")
            i_data["shop_name"] = listing.find("span", 
                text=re.compile("^From shop")).string[10:]
            i_data["shop_id"] = a.get("data-shop-id")
            reviews = listing.find("span",
                class_="wt-text-body-01 wt-nudge-b-1 " +
                "wt-text-gray wt-display-inline-block" + 
                " wt-nudge-l-3 wt-pr-xs-1")
            if reviews != None:
                i_data["shop_reviews"] = reviews.string.strip()[1:-1]
                i_data["shop_reviews"] = int(i_data["shop_reviews"].replace(',',''))
            else:
                reviews = "N/A"
            prices = listing.find_all("span", class_="currency-value")
            i_data["price"] = float(prices[0].string.replace(',',''))
            if len(prices) > 1:
                i_data["on_sale"] = True
                i_data["sale_price"] = float(prices[1].string.replace(',',''))
            else:
                i_data["on_sale"] = False
                i_data["sale_price"] = "N/A"
            i_data["image"] = listing.find("img").get("src")
            i_data["link"] = a.get("href")
            self.data.append(i_data)
            
    
    def export_csv(self):
        fields = ["item_name", "item_id", "shop_name", "shop_id", 
            "shop_reviews", "price", "on_sale", "sale_price", "image", "link"]
        with open('output.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = fields)
            writer.writeheader()
            writer.writerows(self.data)

    def execute(self):
        while (self.cur_page <= self.total_pages 
               and self.num_requests < self.total_pages):
            print(self.cur_page)
            self.get_request()
            self.get_listings()
            self.iterate()
            self.pagination()
        self.export_csv()




def main():
    result = Scraper("stickers", 1)
    result.execute()
    sys.stdout = open("html.txt", "w")
    print(result.doc.find("main"))
    sys.stdout.close()

if __name__ == "__main__":
    main()
