from bs4 import BeautifulSoup
from logs import setup_logging
from scrapers.manage_browser import open_browser, close_browser, capture_thumbnail

# Setup logging
logger = setup_logging("social_scraper")

def get_caption_from_post(url, platform):
    """
    Extracts the caption from a social media post given its URL.
    And saves a thumbnail of the video if present.
    
    Args:
        url (str): The URL of the social media post.
        platform (str): The platform ("instagram", "tiktok", "i", etc.)
        
    Returns:
        tuple: (caption, thumbnail_filename) if successful, otherwise None.
    """
    
    logger.info(f"Extracting caption from {platform} post: {url}")
    
    # Open browser with the specified URL and platform
    browser = open_browser(url, platform)
    if not browser:
        logger.error("Failed to open browser")
        return None
    
    try:
        # Attempt to capture thumbnail
        thumbnail_filename = capture_thumbnail(browser)
        
        # Parse the page content
        logger.info("Parsing page content")
        source = browser.page_source
        data = BeautifulSoup(source, 'html.parser')
        
        # Handle platform-specific caption extraction
        if platform == "instagram" or platform == "i":
            logger.info("Extracting Instagram caption")
            caption = None
            
            try:
                meta_desc = data.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    content = meta_desc.get('content')
                    logger.info(f"Found meta description: {content[:50]}...")
                    parts = content.split('"')
                    if len(parts) >= 2:
                        caption = parts[1]
                        logger.info(f"Extracted Instagram caption from meta quotes: {caption}.")
            except Exception as e:
                logger.info(f"Error extracting caption from meta description: {e}", exc_info=True)
            
        else:
            # Handle TikTok captions
            logger.info("Extracting TikTok caption")
            caption = None
            try:
                # Find caption in <img> alt attributes within <picture> elements
                pictures = data.find_all('picture')
                for picture in pictures:
                    img = picture.find('img')
                    if img and img.get('alt'):
                        caption = img.get('alt')
                        logger.info(f"Found TikTok caption from image alt: {caption[:50]}...")
                        break
            except Exception as e:
                logger.info(f"Error extracting TikTok caption: {e}", exc_info=True)
        
        if caption:
            logger.info(f"Caption found ({len(caption)} chars) and thumbnail saved to {thumbnail_filename}")
            return caption, thumbnail_filename
        else:
            logger.info("Caption not found")
            return None
            
    finally:
        # Always close the browser
        close_browser(browser)