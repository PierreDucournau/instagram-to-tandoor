from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
import time


def get_caption_from_post(url):
    """
    Extracts the caption from an Instagram post given its URL.
    Args:
        url (str): The URL of the Instagram post.
    Returns:
        str: The caption of the Instagram post if found, otherwise None.
    """
    
    print("Extracting caption from Instagram post")
    
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)
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