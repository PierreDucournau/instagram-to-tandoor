import requests as request
import os
import json
from dotenv import load_dotenv

load_dotenv()

def create_recipe(create_json):
    headers = {'Authorization': f'Bearer {os.getenv("TOKEN_MEALIE")}', 'Content-Type': 'application/json'}
    answer = request.post(f'{os.getenv("BASE_URL_MEALIE")}/api/recipes', json=create_json, headers=headers)
    response_text = answer.text.strip().strip('"')
    print(response_text)
    
    return response_text
    
def put_recipe(slug, put_json):
    headers = {'Authorization': f'Bearer {os.getenv("TOKEN_MEALIE")}', 'Content-Type': 'application/json'}
    answer = request.patch(f'{os.getenv("BASE_URL_MEALIE")}/api/recipes/{slug}', json=put_json, headers=headers)
    print(json.dumps(answer.json(), indent=2))


def send_to_mealie(create_json, put_json):
    slug = create_recipe(create_json)
    put_recipe(slug, put_json)