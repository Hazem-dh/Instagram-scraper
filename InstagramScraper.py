import requests
import time
from payloads import EMAIL,PASSWORD,SERVER
from MongoConnector import MongoConnector
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import argparse



BASE_URL="http://www.instagram.com"

class InstaScraper():
    """
    Instagram scraper Class wrapper 
    """
    def __init__(self,driver,hashtag,email,password,n_posts):
        self.driver=driver
        self.hashtag=hashtag
        self.email=email
        self.password=password
        self.n_posts=n_posts
        
    def get_posts_links(self):
        """
        function that automates search of links for the wanted hashtag posts
        """
        #open the webpage
        self.driver.get(BASE_URL)
        alert = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept All")]'))).click()
        username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
        password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
        
        #enter username and password
        username.clear()
        username.send_keys(EMAIL)
        password.clear()
        password.send_keys(PASSWORD)
        
        #target the login button and click it
        button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        #click buttonsto accept of cookies
        alert_cookies = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()
        #click button to dismiss notification alert
        alert_notification = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()
        
        searchbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']")))
        searchbox.clear()
        
        #search for the hashtag 
        keyword = "#"+self.hashtag
        searchbox.send_keys(keyword)
        time.sleep(5) # Wait for 5 seconds
        my_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/" + keyword[1:] + "/')]")))
        my_link.click()
        
        n_scrolls = self.n_posts%9 # the pages only shows 9 posts at first if want more pages we need to scroll to display more posts 
        for j in range(0, n_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        #target all the link elements on the page
        links = driver.find_elements_by_tag_name('a')
        links = [a.get_attribute('href') for a in links]
        #narrow down all links to image links only
        links = [link for link in links if str(link).startswith("https://www.instagram.com/p/")]
        
        return links
    
    def scrape_posts(self,links,n_posted):
        """
        function data return a list containing dictionaries with data of each post
        
        links: a list containt urls of the posts to scrap  
        n_posted: int number of available links  in the database (needed to avoid index conflict)
        """
        posts=[]
        
        for i in range(n_posted,n_posted+self.n_posts):
            driver.get(links[i])
            account_name=driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/h2/div/span/a").text
            text=driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span").text
            comments={}
            j=1 # counter for the comment number
            while(True):
                try:
                    comment_content=driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/ul["+str(j)+"]").text.split("\n")
                    comments[comment_content[0].replace(".","")]=comment_content[1]
                    j+=1
                except:
                    break
            n_comments=len(comments)
            
            try: #check if post has likes
                likes=driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/section[2]/div/div/a").text.split(' ')[0]
            except:
                likes=0 
                
            imgs = driver.find_elements_by_tag_name('img')
            img = imgs[1].get_attribute('src')
            image_data = requests.get(img).content
            data={"_id":i+n_posted,
                    "account_name":account_name,
                    "post":text,
                    "image":image_data,
                    "number_of_likes":likes,
                    "number_of_comments":n_comments,
                    "comments":comments,
                    }
            posts.append(data)
            print('post',i,"scrapped")
        return posts
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='scrap instagram posts of a chosen hashtag')
    parser.add_argument("database",type=str ,help='database name')
    parser.add_argument("hashtag",type=str ,help='the searched hashtag')
    parser.add_argument("N_posts",type=int ,help='number of posts to scrap')
    args = parser.parse_args()
    
    driver = webdriver.Chrome()
    connector=MongoConnector(SERVER,args.database)
    scraper=InstaScraper(driver,args.hashtag,EMAIL,PASSWORD,args.N_posts)
    links=scraper.get_posts_links()
    collection=connector.get_collection(args.hashtag)
    n_posted=connector.get_number_of_post(collection)
    posts=scraper.scrape_posts(links,n_posted)
    connector.insert_posts(collection,posts)
    