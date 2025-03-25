from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json
import time
import os
import logging
import uuid
import base64
from logs import setup_logging

# Setup logging
logger = setup_logging("social_scraper")

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
    
    logger.info(f"Extracting caption from {platform} post: {url}")
            
    match os.getenv("BROWSER"):
        case "firefox":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            browser = webdriver.Firefox(options=options)
            logger.info("Using Firefox browser")
        case "chrome":
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            browser = webdriver.Chrome(options=options)
            logger.info("Using Chrome browser")
        case "edge":
            options = webdriver.EdgeOptions()
            options.add_argument("--headless")
            browser = webdriver.Edge(options=options)
            logger.info("Using Edge browser")
        case "safari":
            options = webdriver.SafariOptions()
            options.add_argument("--headless")
            browser = webdriver.Safari(options=options)
            logger.info("Using Safari browser")
        case "docker":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            service = webdriver.firefox.service.Service(executable_path="/usr/local/bin/geckodriver")
            browser = webdriver.Firefox(options=options, service=service)
            logger.info("Using Firefox browser in Docker environment")
        case _:
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            browser = webdriver.Firefox(options=options)
            logger.info("Using default Firefox browser")
    
    logger.info(f"Loading URL: {url}")
    browser.get(url)

    if platform == "instagram" or platform == "i":
        # Make div with class "x1n2onr6 xzkaem6" visibility hidden
        try:
            logger.info("Waiting for Instagram overlay element to appear")
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "xzkaem6"))
            )
            div = browser.find_element(By.CLASS_NAME, "xzkaem6")
            browser.execute_script("arguments[0].style.visibility='hidden'", div)
            logger.info("Successfully hidden Instagram overlay")
        except Exception as e:
            logger.info(f"Failed to hide Instagram overlay: {e}")
    
    logger.info("Waiting for the website to load")
    time.sleep(0.5)
    
    thumbnail_filename = None
        
    if os.getenv("BROWSER") != "docker":
        # Try to capture video thumbnail
        try:
            logger.info("Attempting to capture video thumbnail")
            # Create thumbnails directory if it doesn't exist
            os.makedirs('thumbnails', exist_ok=True)
            
            # Generate a unique filename
            thumbnail_filename = f"thumbnails/thumbnail_{int(time.time())}.png"
            
            # Wait for video element to be present
            logger.info("Waiting for video element")
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # Find the video element
            video = browser.find_element(By.TAG_NAME, "video")
            
            # Take screenshot of the video element
            video.screenshot(thumbnail_filename)
            logger.info(f"Thumbnail saved to {thumbnail_filename}")
        except Exception as e:
            logger.info(f"Failed to capture thumbnail: {e}")
    else:
        # For Docker environment, use JavaScript instead of direct screenshot
        logger.info("Running in Docker, using JavaScript to capture thumbnail")
        try:
            # Wait longer for content to load in Docker
            time.sleep(5)
            
            # Check what elements are available (for debugging)
            elements_debug = browser.execute_script("""
                return {
                    hasVideo: document.querySelector('video') !== null,
                    hasSource: document.querySelector('source') !== null,
                    hasIframe: document.querySelector('iframe') !== null,
                    hasImg: document.querySelector('img') !== null
                };
            """)
            logger.info(f"Available elements in DOM: {elements_debug}")
            
            # Try to capture frame using JavaScript
            thumbnail_data = browser.execute_script("""
                function captureElement() {
                    // Try different media elements in order of preference
                    let element = document.querySelector('video') || 
                                document.querySelector('img[src*="instagram"]') ||
                                document.querySelector('img');
                                
                    if (!element) return null;
                    
                    const canvas = document.createElement('canvas');
                    const width = element.tagName === 'VIDEO' ? element.videoWidth || 640 : element.width || 640;
                    const height = element.tagName === 'VIDEO' ? element.videoHeight || 480 : element.height || 480;
                    
                    canvas.width = width;
                    canvas.height = height;
                    
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(element, 0, 0, width, height);
                    
                    return canvas.toDataURL('image/png');
                }
                return captureElement();
            """)
            
            if thumbnail_data:
                # Create thumbnails directory if it doesn't exist
                os.makedirs('thumbnails', exist_ok=True)
                
                # Generate a unique filename
                thumbnail_filename = f"thumbnails/thumbnail_{uuid.uuid4()}.png"
                
                # Convert base64 data to image and save
                img_data = thumbnail_data.replace('data:image/png;base64,', '')
                with open(thumbnail_filename, 'wb') as f:
                    f.write(base64.b64decode(img_data))
                
                logger.info(f"Successfully captured thumbnail in Docker: {thumbnail_filename}")
            else:
                logger.info("No suitable element found for thumbnail capture in Docker")
        except Exception as e:
            logger.info(f"Failed to capture thumbnail in Docker: {e}", exc_info=True)
            
    logger.info("Parsing page content")
    source = browser.page_source
    data = BeautifulSoup(source, 'html.parser')
    
    logger.info(f"Page title: {platform}")
    # Handle Instagram captions
    if (platform == "instagram" or platform == "i"):
        logger.info("Extracting Instagram caption")
        caption = None
        try:
            for span in data.findAll('h1'):
                if span.get_text():
                    caption = span.get_text()
                    logger.info(f"Found Instagram caption: {caption[:50]}...")
                    break
        except Exception as e:
            logger.info(f"Error extracting Instagram caption: {e}", exc_info=True)
    else:
        # Handle TikTok captions
        logger.info("Extracting TikTok caption")
        caption = None
        try:
            # First, try to find caption in <img> alt attributes within <picture> elements
            pictures = data.find_all('picture')
            for picture in pictures:
                img = picture.find('img')
                caption = img.get('alt')
                if caption:  # Ensure it's a meaningful caption
                    logger.info(f"Found TikTok caption from image alt: {caption[:50]}...")
                    break
        except Exception as e:
            logger.info(f"Error extracting TikTok caption: {e}", exc_info=True)
                    
    logger.info("Closing browser")
    browser.close()
        
    if caption:
        logger.info(f"Caption found ({len(caption)} chars) and thumbnail saved to {thumbnail_filename}")
        return caption, thumbnail_filename
    else:
        logger.info("Caption not found")
        return None