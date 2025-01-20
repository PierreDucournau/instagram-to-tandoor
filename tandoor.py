import requests as request
import os
import json

def send_to_tandoor(data):
    headers = {'Authorization': f'Bearer {os.getenv("TOKEN")}', 'Content-Type': 'application/json'}
    answer = request.post(f'{os.getenv("BASE_URL")}/api/recipe/', json=data, headers=headers)
    print(json.dumps(answer.json(), indent=2))