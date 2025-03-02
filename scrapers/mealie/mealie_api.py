import requests as request
import os
import json

def send_to_mealie(json_file):
    """
    Sends a JSON file to the Mealie API to create a recipe.
    Args:
        json_file (dict): The JSON data to be sent to the Mealie API.
    Returns:
        None
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    print("URL: ", os.getenv("BASE_URL_MEALIE"))

    headers = {'Authorization': f'Bearer {os.getenv("TOKEN_MEALIE")}', 'Content-Type': 'application/json'}
    try:
        response = request.post(f'http://100.79.78.112:3333/api/recipes/create/html-or-json', json=json_file, headers=headers)
        response.raise_for_status()

    except request.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.content}")
    except request.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except request.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except request.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    finally:
        print("Successfully created recipe in Mealie with content:")
        print(json.dumps(json_file, indent=2))