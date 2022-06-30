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
        self.url = f"https://www.etsy.com/search?q={search_term}"
        self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; ' + 
                        'Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 ' + 
                        '(KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
        self.data = []

    def get_request(self):
        page = requests.get(self.url, headers = self.headers).content
        self.doc = BeautifulSoup(page, "lxml")
        

    def pagination(self):
        if (self.cur_page < self.total_pages):
            self.url += f"%page={self.cur_page + 1}&ref=pagination"
            return True;
        else:
            return False;

    def get_listings(self):
        parent = self.doc.find("ul","wt-grid wt-grid--block wt-pl-xs-0 tab-reorder-container");
        self.listings = parent.find_all("div", class_=re.compile("^js-merch"));
    
    def iterate(self):
        for listing in self.listings:
            i_data = {}
            a = listing.find("a")
            i_data["id"] = a.get("data-listing-id")
            i_data["item_name"] = a.get("data-listing-id")
            i_data["shop_name"] = listing.find("span", text=re.compile("^From shop")).string[10:]
            i_data["shop_id"] = a.get("data-shop-id")
            i_data["shop_reviews"] = listing.find("span",
                    class_="wt-text-body-01 wt-nudge-b-1 " +
                    "wt-text-gray wt-display-inline-block" + 
                    " wt-nudge-l-3 wt-pr-xs-1").string.strip()[1:-1]
            prices = listing.find_all("span", class_="currency-value")
            print(prices)
            i_data["price"] = prices[0].string
            if len(prices) > 1:
                i_data["sale_price"] = prices[1].string
                i_data["on_sale"] = True
            else:
                i_data["sale_price"] = "N/A"
                i_data["on_sale"] = False
            i_data["image"] = listing.find("img").get("src")
            i_data["link"] = a.get("href")
            self.data.append(i_data)
            
    
    def export_csv(self):
        i = 0





def main():
    result = Scraper("sticker sheet", 1)
    result.get_request()
    sys.stdout = open("html.txt", "w")
    print(result.doc.find("div", class_="wt-bg-white wt-display-block wt-pb-xs-2 wt-mt-xs-0"))
    sys.stdout.close()
    # result.get_listings()
    # result.iterate()
    # print(result.data)
    # print(len(result.data))

if __name__ == "__main__":
    main()
