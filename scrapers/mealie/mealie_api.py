import requests as request
import os
import json
from io import BytesIO
from PIL import Image

def send_to_mealie(json_file, thumbnail_filename):
    """
    Sends a JSON file to the Mealie API to create a recipe.
    Args:
        json_file (dict): The JSON data to be sent to the Mealie API.
        thumbnail_filename (str): The filename of the thumbnail image to be uploaded.
    Returns:
        None
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    print("URL: ", os.getenv("BASE_URL_MEALIE"))

    headers = {'Authorization': f'Bearer {os.getenv("TOKEN_MEALIE")}', 'Content-Type': 'application/json'}
    try:
        response = request.post(f'{os.getenv("BASE_URL_MEALIE")}/api/recipes/create/html-or-json', json=json_file, headers=headers)
        recipe_id = response.content.decode('utf-8').strip('"')
        print("Recipe ID: ", recipe_id)
        
        # If thumbnail exists, upload it 
        if thumbnail_filename and recipe_id and os.path.exists(thumbnail_filename):
            upload_thumbnail(recipe_id, thumbnail_filename)
            
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
        
def upload_thumbnail(recipe_slug, thumbnail_filename):
    """
    Upload a thumbnail image to an existing mealie recipe
    Args:
        recipe_slug (str): The slug of the recipe to update (from the created recipe response)
        thumbnail_filename (str): Path to the local image file
    """
    headers = {'Authorization': f'Bearer {os.getenv("TOKEN_MEALIE")}'}
    
    try:
        # Check if the file exists
        if not os.path.exists(thumbnail_filename):
            print(f"Thumbnail file not found: {thumbnail_filename}")
            return
        
        # Get file extension
        _, extension = os.path.splitext(thumbnail_filename)
        extension = extension.lstrip('.').lower()
        
        # Clean up the recipe slug - remove quotes if present
        recipe_slug = recipe_slug.strip('"\'')
        
        # Prepare the files for upload
        with open(thumbnail_filename, 'rb') as img_file:
            files = {
                'image': (f'image.{extension}', img_file, f'image/{extension}'),
                'extension': (None, extension)
            }
            
            # Send the request
            response = request.put(
                f'{os.getenv("BASE_URL_MEALIE")}/api/recipes/{recipe_slug}/image',
                files=files,
                headers=headers
            )
            
            print(f"Image upload response status: {response.status_code}")
            print(f"Image upload response: {response.text}")
            response.raise_for_status()
            print(f"Successfully uploaded thumbnail for recipe {recipe_slug}")
            
    except Exception as e:
        print(f"Failed to upload thumbnail: {e}")
        print(f"Thumbnail path: {thumbnail_filename}")
        print(f"Recipe slug: {recipe_slug}")