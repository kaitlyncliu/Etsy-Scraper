# Etsy Scraper
 
* A program to scrape search results from www.etsy.com

# RUN
* Execute the following code to download this scraper and install dependencies.
```
git clone https://github.com/kaitlyncliu/Etsy-Scraper
pip install bs4
```
* Execute a command of the format `python scraper.py search_term num_pages search_type` in the cloned directory.
* The results will be exported to a .csv in your directory. Each page returns ~8 results.

* Example:
```
python scraper.py "stickers" 2 "Quick"
```
* Results of this example are in the example.csv file.
* For listing tags, please use `search_type = "Detailed"`.

