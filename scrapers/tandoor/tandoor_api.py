import requests as request
import os
import json
from io import BytesIO
from PIL import Image
from logs import setup_logging

logger = setup_logging("tandoor_api")

def send_to_tandoor(json_file, thumbnail_filename):
    """
    Sends a JSON file to the Tandoor API to create recipe.
    And uploads a thumbnail image if present.
    Args:
        json_file (dict): The JSON data to be sent to the Mealie API.
        thumbnail_filename (str): The filename of the thumbnail image to be uploaded.
    Returns:
        None
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """    
    headers = {'Authorization': f'Bearer {os.getenv("TOKEN_TANDOOR")}', 'Content-Type': 'application/json'}
    try:
        response = request.post(f'{os.getenv("BASE_URL_TANDOOR")}/api/recipe/', json=json_file, headers=headers)
        recipe_data = response.json()
        recipe_id = recipe_data.get('id')
        
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
        logger.info("Successfully created recipe in Tandoor with content:")
        logger.info(json.dumps(json_file, indent=2))
        
def upload_thumbnail(recipe_id, thumbnail_filename):
    """
    Upload a thumbnail image to an existing Tandoor recipe
    Args:
        recipe_id (int): The ID of the recipe to update
        thumbnail_filename (str): Path to the local image file
    """
    headers = {'Authorization': f'Bearer {os.getenv("TOKEN_TANDOOR")}'}
    
    try:
        # Check if the file exists and prepare the image
        if not os.path.exists(thumbnail_filename):
            logger.info(f"Thumbnail file not found: {thumbnail_filename}")
            return
            
        # Open and optimize the image
        with Image.open(thumbnail_filename) as img:
            # Convert to RGB if needed (in case of PNG with alpha channel)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            
            # Save to a BytesIO object
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            
            # Create the multipart form data
            files = {
                'image': (os.path.basename(thumbnail_filename), img_byte_arr, 'image/jpeg')
            }
            
            # Send the request to the specific image endpoint
            response = request.put(
                f'{os.getenv("BASE_URL_TANDOOR")}/api/recipe/{recipe_id}/image/',
                files=files,
                headers=headers
            )
            response.raise_for_status()
            logger.info(f"Successfully uploaded thumbnail for recipe {recipe_id}")
            
    except Exception as e:
        logger.info(f"Failed to upload thumbnail: {e}")
        logger.info(f"Thumbnail path: {thumbnail_filename}")