# Instagram-scraper

## About the project 

This is a scraper that automatically scraps posts data (image, text, comments, likes) of a given hashtag
with [Selenium](https://selenium-python.readthedocs.io) and store them in a MongoDB database.

## Installation

1. Download and install [MongoDB](https://www.mongodb.com/try/download/community)
2. Either clone this repo or download all these files by going to _Code -> Download ZIP_.
3. Open the terminal inside project folder and install the required packages
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Launch your MongoDB server
2. Launch **chromedriver.exe**
3. Run InstagramScraper.py with the desired parameters
   ```sh
   InstagramScraper [database name][hashtag][number of posts]
   ```
4. A chrome window will automatically open, sit back and enjoy watching the posts being scrapped 





## License
[MIT](https://choosealicense.com/licenses/mit/)
