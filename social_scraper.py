from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
import time
import os


def get_caption_from_post(url):
    """
    Extracts the caption from an Instagram post given its URL.
    Args:
        url (str): The URL of the Instagram post.
    Returns:
        str: The caption of the Instagram post if found, otherwise None.
    """
    
    print("Extracting caption from social media post")
            
    match os.getenv("BROWSER"):
        case "firefox":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            browser = webdriver.Firefox(options=options)
        case "chrome":
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            browser = webdriver.Chrome(options=options)
        case "edge":
            options = webdriver.EdgeOptions()
            options.add_argument("--headless")
            browser = webdriver.Edge(options=options)
        case "safari":
            options = webdriver.SafariOptions()
            options.add_argument("--headless")
            browser = webdriver.Safari(options=options)
        case _:
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
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