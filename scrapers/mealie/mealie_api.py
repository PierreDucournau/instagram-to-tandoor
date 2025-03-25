import requests as request
import os
import json
from io import BytesIO
from PIL import Image
from logs import setup_logging

logger = setup_logging("mealie_api")

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
    logger.info("URL: ", os.getenv("BASE_URL_MEALIE"))

    headers = {'Authorization': f'Bearer {os.getenv("TOKEN_MEALIE")}', 'Content-Type': 'application/json'}
    try:
        response = request.post(f'{os.getenv("BASE_URL_MEALIE")}/api/recipes/create/html-or-json', json=json_file, headers=headers)
        recipe_id = response.content.decode('utf-8').strip('"')
        logger.info("Recipe ID: ", recipe_id)
        
        # If thumbnail exists, upload it 
        if thumbnail_filename and recipe_id and os.path.exists(thumbnail_filename):
            upload_thumbnail(recipe_id, thumbnail_filename)
            
        response.raise_for_status()

    except request.exceptions.HTTPError as http_err:
        logger.info(f"HTTP error occurred: {http_err}")
        logger.info(f"Response content: {response.content}")
    except request.exceptions.ConnectionError as conn_err:
        logger.info(f"Connection error occurred: {conn_err}")
    except request.exceptions.Timeout as timeout_err:
        logger.info(f"Timeout error occurred: {timeout_err}")
    except request.exceptions.RequestException as req_err:
        logger.info(f"An error occurred: {req_err}")
    finally:
        logger.info("Successfully created recipe in Mealie with content:")
        logger.info(json.dumps(json_file, indent=2))
        
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
            logger.info(f"Thumbnail file not found: {thumbnail_filename}")
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
            
            logger.info(f"Image upload response status: {response.status_code}")
            logger.info(f"Image upload response: {response.text}")
            response.raise_for_status()
            logger.info(f"Successfully uploaded thumbnail for recipe {recipe_slug}")
            
    except Exception as e:
        logger.info(f"Failed to upload thumbnail: {e}")
        logger.info(f"Thumbnail path: {thumbnail_filename}")
        logger.info(f"Recipe slug: {recipe_slug}")