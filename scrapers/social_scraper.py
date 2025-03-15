from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
import os



def get_caption_from_post(url, platform):
    """
    Extracts the caption from an Instagram post given its URL.
    And saves a thumbnail of the video if present.
    Args:
        url (str): The URL of the Instagram post.
    Returns:
        str: The caption of the Instagram post if found, otherwise None.
        str: The filename of the thumbnail if captured, otherwise None.
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
        case "docker":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            service = webdriver.firefox.service.Service(executable_path="/usr/local/bin/geckodriver")
            browser = webdriver.Firefox(options=options, service=service)
        case _:
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            browser = webdriver.Firefox(options=options)
    
    browser.get(url)

    if platform == "instagram" or platform == "i":
        # Make div with class "x1n2onr6 xzkaem6" visibility hidden
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "xzkaem6"))
            )
            div = browser.find_element(By.CLASS_NAME, "xzkaem6")
            browser.execute_script("arguments[0].style.visibility='hidden'", div)
            print("Successfully hidden div")
        except Exception as e:
            print(f"Failed to hide div: {e}")
    
    print("Waiting for the Website to load")
    time.sleep(0.5)
        
    if os.getenv("BROWSER") != "docker":
        # Try to capture video thumbnail
        try:
            # Create thumbnails directory if it doesn't exist
            os.makedirs('thumbnails', exist_ok=True)
            
            # Generate a unique filename
            thumbnail_filename = f"thumbnails/thumbnail_{int(time.time())}.png"
            
            # Wait for video element to be present
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # Find the video element
            video = browser.find_element(By.TAG_NAME, "video")
            
            # Take screenshot of the video element
            video.screenshot(thumbnail_filename)
            print(f"Thumbnail saved to {thumbnail_filename}")
        except Exception as e:
            print(f"Failed to capture thumbnail: {e}")
    else:
        thumbnail_filename = None
        print("Running in Docker, skipping thumbnail capture")
    
    source = browser.page_source
    data = BeautifulSoup(source, 'html.parser')
    
    caption = None
    for span in data.findAll('h1'):
        if span.get_text():
            caption = span.get_text()
                
    browser.close()
    
    if caption:
        print("Caption found:", caption, " and thumbnail saved to ", thumbnail_filename)
        return caption, thumbnail_filename
    else:
        print("Caption not found")
        return None