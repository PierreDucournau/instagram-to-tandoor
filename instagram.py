from selenium import webdriver
from bs4 import BeautifulSoup
import time


def get_caption_from_post(url):
    browser = webdriver.Firefox()
    browser.get(url)
    time.sleep(5) 
    source = browser.page_source
    data = BeautifulSoup(source, 'html.parser')
    
    caption = None
    for span in data.findAll('h1'):
        if span.get_text():
            caption = span.get_text()
    
    browser.close()
    
    if caption:
        print("Caption found:", caption)
        return caption
    else:
        print("Caption not found")
        return None