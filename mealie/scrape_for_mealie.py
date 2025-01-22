from instagram import get_caption_from_post
from mealie.mealie_api import send_to_mealie
from mealie.duckai_mealie import prompt_chatgpt, get_number_of_steps
import os
import json
from datetime import datetime


def scrape_recipe_for_mealie(url):
    """
    Function to process an Instagram post URL and extract recipe information.
    Args:
        url (str): The URL of the Instagram post containing the recipe.
    The function performs the following steps:
    1. Extracts the caption from the Instagram post.
    2. Determines the number of steps in the recipe from the caption.
    3. Initializes a JSON structure to store the recipe information.
    4. Uses a duck ai to extract and populate various parts of the recipe:
        - Recipe name and description
        - Instructions and ingredients for each step
        - Servings information
        - Nutrition and other metadata
    5. Updates the JSON structure with the extracted information.
    6. Saves the final JSON structure to a file named 'output.json'.
    7. Sends the JSON structure to the Tandoor API.
    Returns:
        None
    """
    
    caption = get_caption_from_post(url)
    if caption:
        number_of_steps = get_number_of_steps(caption)
        print(f"Number of steps in the recipe: {number_of_steps}")
        if number_of_steps:
            json_parts = [
                {
                    "name": "string"
                },
                {
                    "recipeServings": 0,
                    "recipeYieldQuantity": 0,
                    "recipeYield": "string",
                    "totalTime": "string",
                    "prepTime": "string",
                    "cookTime": "string",
                    "performTime": "string",
                    "description": "",
                },
                {
                    "recipeIngredient": [
                        {
                        "quantity": 1.0,
                        "unit": None,
                        "food": None,
                        "note": "1 Cup Flour",
                        "isFood": False,
                        "disableAmount": True,
                        "display": "1 Cup Flour",
                        "title": None,
                        "originalText": None,
                        }
                    ],
                },
                {
                    "summary": "",
                    "text": "",
                },
                ]
        
            create_json = {}
            put_json = {}
            
            name_res = prompt_chatgpt(caption, json_parts[0], "name")
            if name_res:
                create_json.update(name_res)
                    
            print(json.dumps(create_json, indent=2))
            
            servings_res = prompt_chatgpt(caption, json_parts[1], "servings")
            if servings_res:
                put_json.update(servings_res)
                
            print(json.dumps(put_json, indent=2))
            
            ingredients_res = prompt_chatgpt(caption, json_parts[2], "ingredients")
            if ingredients_res:
                put_json.update(ingredients_res)
                
            print(json.dumps(put_json, indent=2))
            
            steps_json = {"recipeInstructions": []}
            
            for i in range(1, number_of_steps + 1):
                step_res = prompt_chatgpt(caption, json_parts[3], "step", i)
                if step_res:
                    steps_json["recipeInstructions"].append(step_res)
                    print(json.dumps(steps_json, indent=2))
                    
            put_json.update(steps_json)
                    
            put_json["orgURL"] = url
            put_json["dateAdded"] = datetime.now().strftime("%Y-%m-%d")
            put_json["createdAt"] = datetime.now().isoformat() + "Z"
                            
            print(json.dumps(put_json, indent=2))
            with open('./mealie/create.json', 'w') as outfile:
                json.dump(create_json, outfile, indent=2)
            with open('./mealie/put.json', 'w') as outfile:
                json.dump(put_json, outfile, indent=2)
                
            send_to_mealie(create_json, put_json)