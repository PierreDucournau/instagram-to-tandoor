import argparse
import re
from dotenv import load_dotenv
from scrapers.scrape_for_mealie import scrape_recipe_for_mealie
from scrapers.scrape_for_tandoor import scrape_recipe_for_tandoor

load_dotenv()


def is_valid_url(url, platform):
    """
    Check if the given URL is a valid Instagram URL.
    Args:
        url (str): The URL to be validated.
    Returns:
        bool: True if the URL matches the Instagram URL pattern, False otherwise.
    """
    
    match platform:
        case "instagram" | "i":
            url_pattern = re.compile(r'^(https?:\/\/)?(www\.)?instagram\.com\/[A-Za-z0-9_\-\/]+\/?(\?.*)?$')
        case "tiktok" | "t":
            url_pattern = re.compile(r'^(https?:\/\/)?(www\.)?tiktok\.com\/@?[A-Za-z0-9_\-\/]+\/video\/[0-9]+(\?.*)?$')
            
    return re.match(url_pattern, url) is not None
    
def main():
    """
    Main function to extract recipe information from an Instagram post.
    This function uses argparse to parse command-line arguments for the URL of the Instagram post
    and the mode of recipe extraction (either 'mealie' or 'tandoor'). It validates the provided
    Instagram URL and calls the appropriate scraping function based on the specified mode.
    Raises:
        ValueError: If the provided Instagram URL is invalid or if the mode is not 'mealie'/'m' or 'tandoor'/'t'.
    Command-line Arguments:
        -url (str): The URL of the Instagram post.
        -mode (str): The mode of the recipe extraction ('mealie'/'m' or 'tandoor'/'t').
    """
    parser = argparse.ArgumentParser(description='Extract recipe information from an post')
    parser.add_argument('-url', type=str, required=True, help='The URL of the Instagram post')
    parser.add_argument('-mode', type=str, required=True, help='The mode of the recipe extraction (mealie or tandoor)')
    parser.add_argument('-platform', type=str, required=True, help='The platform of the URL (instagram or tiktok)')
    args = parser.parse_args()
    
    if not is_valid_url(args.url, args.platform):
        raise ValueError("Invalid URL. Please provide a valid post URL.")
    
    if args.mode == 'mealie' or args.mode == 'm':
        scrape_recipe_for_mealie(args.url, args.platform)
    elif args.mode == 'tandoor' or args.mode == 't':
        scrape_recipe_for_tandoor(args.url, args.platform)
    else:
        raise ValueError("Invalid mode. Please specify either 'mealie'/'m' or 'tandoor'/'t'")

if __name__ == '__main__':
    main()