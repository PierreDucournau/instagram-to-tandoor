import requests as request
import os
import json


def send_to_tandoor(data):
    """
    Sends recipe data to the Tandoor API.
    This function takes a dictionary containing recipe data and sends it to the Tandoor API using a POST request.
    The API endpoint and authorization token are retrieved from environment variables.
    Args:
        data (dict): A dictionary containing the recipe data to be sent to the Tandoor API.
    Returns:
        None
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    headers = {'Authorization': f'Bearer {os.getenv("TOKEN")}', 'Content-Type': 'application/json'}
    answer = request.post(f'{os.getenv("BASE_URL")}/api/recipe/', json=data, headers=headers)
    print(json.dumps(answer.json(), indent=2))