from scrapers.social_scraper import get_caption_from_post
from scrapers.mealie.mealie_api import send_to_mealie
from scrapers.mealie.duckai_mealie import prompt_chatgpt
import json
from datetime import datetime

def scrape_recipe_for_mealie(url):
    """
    Function to process an Instagram post URL and extract recipe information.
    Args:
        url (str): The URL of the Instagram post containing the recipe.
    The function performs the following steps:
    1. Extracts the caption from the Instagram post.
    2. Uses a duck ai to extract and populate various parts of the recipe:
        - Recipe name and description
        - Instructions and ingredients for each step
        - Servings information
        - Nutrition and other metadata
    3. Updates the JSON structure with the extracted information.
    4. Sends the JSON structure to the Mealie API.
    Returns:
        None
    """
    
    caption = get_caption_from_post(url)
    if caption:
        json_parts = [
            {
                "@context": "https://schema.org",
                "@type": "Recipe",
                "author": "string",
                "cookTime": "PT1H",
                "prepTime": "PT15M",
                "datePublished": "string",
                "description": "",
                "image": None,
                "recipeYield": "",
            },
            {
                "recipeIngredient": [
                    "string",
                ],
            },
            {
                "interactionStatistic": 
                    {
                        "@type": "InteractionCounter",
                        "interactionType": "https://schema.org/Comment",
                        "userInteractionCount": "140"
                    },
            },
            {
                "name": "Mom's World Famous Banana Bread",
            },
            {
                "nutrition": {
                    "@type": "NutritionInformation",
                    "calories": "string",
                    "fatContent": "string"
                },
            },
            {
                "suitableForDiet": None
            },
            {
                "recipeInstructions": "string",
            }
            ]
    
        full_json = {}
        
        instructions_res = prompt_chatgpt(caption, json_parts[6], "instructions")
        if instructions_res:
            full_json.update(instructions_res)
            
        print(json.dumps(full_json, indent=2))
        
        info_res = prompt_chatgpt(caption, json_parts[0], "info")
        if info_res:
            full_json.update(info_res)
                
        print(json.dumps(full_json, indent=2))
        
        ingredients_res = prompt_chatgpt(caption, json_parts[1], "ingredients")
        if ingredients_res:
            full_json.update(ingredients_res)
            
        print(json.dumps(full_json, indent=2))
        
        full_json.update(json_parts[2])
        
        name_res = prompt_chatgpt(caption, json_parts[3], "name")
        if name_res:
            full_json.update(name_res)
            
        print(json.dumps(full_json, indent=2))
        
        nutrition_res = prompt_chatgpt(caption, json_parts[4], "nutrition")
        if nutrition_res:
            full_json.update(nutrition_res)
            
        print(json.dumps(full_json, indent=2))
        
        full_json.update(json_parts[5])
            
        print(json.dumps(full_json, indent=2))
                
        full_json["datePublished"] = datetime.now().strftime("%Y-%m-%d")
        
        json_ld_script = f'<script type="application/ld+json">{json.dumps(full_json)}</script>'
        
        final_json = {
            "includeTags": False,
            "data": json_ld_script
        }
                        
        print(json.dumps(final_json, indent=2))
        with open('./scrapers/mealie/final_json.json', 'w') as outfile:
            json.dump(final_json, outfile, indent=2)
            
        send_to_mealie(final_json)