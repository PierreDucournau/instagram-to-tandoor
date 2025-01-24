import requests as request
import os
import json

def send_to_tandoor(json_file):
    """
    Sends a JSON file to the Tandoor API to create recipe.
    Args:
        json_file (dict): The JSON data to be sent to the Mealie API.
    Returns:
        None
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """    
    headers = {'Authorization': f'Bearer {os.getenv("TOKEN_TANDOOR")}', 'Content-Type': 'application/json'}
    try:
        response = request.post(f'{os.getenv("BASE_URL_TANDOOR")}/api/recipe/', json=json_file, headers=headers)
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
        print("Successfully created recipe in Tandoor with content:")
        print(json.dumps(json_file, indent=2))