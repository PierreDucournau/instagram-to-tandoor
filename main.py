import json
import argparse
from dotenv import load_dotenv
import re
from mealie.scrape_for_mealie import scrape_recipe_for_mealie
from tandoor.scrape_for_tandoor import scrape_recipe_for_tandoor

load_dotenv()

def is_valid_instagram_url(url):
        instagram_url_pattern = re.compile(
            r'^(https?:\/\/)?(www\.)?instagram\.com\/p\/[A-Za-z0-9_\-]+\/?$'
        )
        return re.match(instagram_url_pattern, url) is not None
    
    
def main():
    parser = argparse.ArgumentParser(description='Extract recipe information from an Instagram post')
    parser.add_argument('-url', type=str, required=True, help='The URL of the Instagram post')
    parser.add_argument('-mode', type=str, required=True, help='The mode of the recipe extraction (mealie or tandoor)')
    args = parser.parse_args()
    
    if not is_valid_instagram_url(args.url):
        raise ValueError("Invalid Instagram URL. Please provide a valid Instagram post URL.")
    
    if args.mode == 'mealie' or args.mode == 'm':
        scrape_recipe_for_mealie(args.url)
    elif args.mode == 'tandoor' or args.mode == 't':
        scrape_recipe_for_tandoor(args.url)
    else:
        raise ValueError("Invalid mode. Please specify either 'mealie'/'m' or 'tandoor'/'t'")

if __name__ == '__main__':
    main()