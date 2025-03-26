import json
import os
import re
from bs4 import BeautifulSoup
from logs import setup_logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = setup_logging("duck_ai")

def initialize_chat(browser, caption):
    """
    Initialize a chat with Duck.ai by providing the recipe caption as context.
    
    Args:
        browser (WebDriver): The browser window object.
        caption (str): The recipe caption to use as context.
    
    Returns:
        bool: True if initialization is successful, False otherwise.
    """
    logger.info("Initializing chat with recipe context...")
    
    try:
        # Wait for the textarea and enter the context prompt
        textarea = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@name='user-prompt']"))
        )
        
        # Set up context for all future interactions
        context_prompt = f"I'm going to ask you questions about this recipe. Please use this recipe information as context for all your responses: {caption}"
        textarea.send_keys(context_prompt)
        textarea.send_keys(Keys.RETURN)
        
        # Wait for the response to complete
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit' and @disabled]")))
        WebDriverWait(browser, 60).until_not(EC.presence_of_element_located((By.XPATH, "//button//rect[@width='10' and @height='10']")))
        
        logger.info("Chat initialized successfully with recipe context")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize chat: {e}", exc_info=True)
        return False

def send_raw_prompt(browser, prompt):
    """
    Send a prompt to Duck.ai and get the raw HTML response.
    Basic low-level function used by other functions.
    
    Args:
        browser (WebDriver): The browser window object.
        prompt (str): The prompt text to send.
    
    Returns:
        str or None: The raw HTML response if successful, otherwise None.
    """
    logger.info(f"Sending raw prompt: {prompt[:50]}...")
    
    try:
        # Wait for the textarea and enter the prompt
        textarea = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@name='user-prompt']"))
        )
        
        # Clear any existing text
        textarea.clear()
        
        # Enter the new prompt
        textarea.send_keys(prompt)
        textarea.send_keys(Keys.RETURN)
        
        # Wait for the response to complete
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit' and @disabled]")))
        WebDriverWait(browser, 60).until_not(EC.presence_of_element_located((By.XPATH, "//button//rect[@width='10' and @height='10']")))
        
        # Get the page source after the response is complete
        response = browser.page_source
        return response
        
    except Exception as e:
        logger.error(f"Failed to send prompt: {e}", exc_info=True)
        return None

def extract_json_from_response(response):
    """
    Extract JSON from a Duck AI HTML response.
    
    Args:
        response (str): The HTML response from Duck AI.
    
    Returns:
        dict or None: Parsed JSON if found, otherwise None.
    """
    if not response:
        return None
        
    try:
        soup = BeautifulSoup(response, 'html.parser')
        code_blocks = soup.find_all('code', {'class': 'language-json'})
        
        if code_blocks:
            # Get the last (most recent) code block
            json_response = code_blocks[-1].get_text()
            return json.loads(json_response)
        else:
            logger.warning("No JSON code block found in the response")
            return None
    except Exception as e:
        logger.error(f"Failed to extract JSON: {e}", exc_info=True)
        return None

def send_json_prompt(browser, prompt):
    """
    Send a prompt to Duck AI and extract JSON from the response.
    
    Args:
        browser (WebDriver): The browser window object.
        prompt (str): The prompt text to send.
        
    Returns:
        dict or None: The parsed JSON if successful, otherwise None.
    """
    response = send_raw_prompt(browser, prompt)
    return extract_json_from_response(response)

def get_number_of_steps(browser, caption=None):
    """
    Extracts the number of steps from a recipe caption using Duck.ai.
    
    Args:
        browser (WebDriver): The browser window object.
        caption (str, optional): The recipe caption to analyze. Not needed if chat is already initialized.
    
    Returns:
        int or None: The number of steps if successfully extracted, otherwise None.
    """
    logger.info("Getting number of recipe steps...")
    
    try:
        # No need to include caption since it's already in the chat context
        prompt = "How many steps are in this recipe? Please respond with only a number."
        
        response = send_raw_prompt(browser, prompt)
        
        if response:
            # Parse the response to extract the step count
            soup = BeautifulSoup(response, 'html.parser')
            
            # Find the most recent response
            responses = soup.find_all('div', {'heading': 'GPT-4o mini'})
            if responses:
                # Get the last (most recent) response
                last_response = responses[-1]
                response_div = last_response.find('div', {'class': 'VrBPSncUavA1d7C9kAc5'})
                
                if response_div:
                    paragraph = response_div.find('p')
                    if paragraph:
                        text = paragraph.get_text().strip()
                        # Try to extract a number from the text
                        numbers = re.findall(r'\d+', text)
                        if numbers:
                            number_of_steps = int(numbers[0])
                            logger.info(f"Found {number_of_steps} steps in the recipe")
                            return number_of_steps
                        else:
                            logger.warning(f"No number found in response: {text}")
                    else:
                        logger.warning("No paragraph found in response")
                else:
                    logger.warning("Response div not found")
            else:
                logger.warning("No GPT-4o mini heading found")
        
        logger.warning("Could not determine number of steps")
        return None
        
    except Exception as e:
        logger.error(f"Error in get_number_of_steps: {e}", exc_info=True)
        return None

def process_recipe_part(browser, part, mode="", step_number=None):
    """
    Process a part of a recipe using Duck AI and get structured data.
    Unified function that handles both Mealie and Tandoor formatting styles.
    
    Args:
        browser (WebDriver): The browser window object.
        part (dict): The JSON document part to be filled out.
        mode (str, optional): Mode of the prompt (e.g., "info", "ingredients", "step"). 
                             For Tandoor, use "step" for recipe steps.
        step_number (int, optional): The step number when mode is "step".
    
    Returns:
        dict or None: The parsed JSON response if successful, otherwise None.
    """
    try:
        # Create the appropriate prompt based on the mode
        if mode == "step" or step_number is not None:
            # Tandoor-style step prompt
            prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part}. Only complete the specified sections. Only complete step {step_number} of the recipe. If the step has more than 3 ingredients, only complete the first 3 and finish the JSON object. The name of the step should be the step number e.g. 'name': '{step_number}.'. Only include the current instruction description in the instruction field. The amount value of the ingredient can only be a whole number, please round up if the amount is a decimal. If an ingredient has already been mentioned in a previous step, do not include it again as an ingredient in this step. Respond with a JSON code block enclosed in triple backticks (```json)."
        elif mode == "info":
            prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part} Only fill out author, description, recipeYield, prepTime and cooktime. The cooktime and pretime should have the format e.g. PT1H for one hour or PT15M for 15 Minutes."
        elif mode == "ingredients":
            prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part} Append the ingredients to the 'recipeIngredient' list. One ingredient per line."
        elif mode == "name":  
            prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part} Keep the name of the recipe short."
        elif mode == "nutrition":
            prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part} Only fill out calories and fatContent with a string."
        elif mode == "instructions":
            prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part} Write the instruction as one long string. No string separation, just one long text! Don't add ingredients here. JSON FORMAT IN CODE WINDOW!"
        else:
            # General prompt
            prompt = f"Write your Response in the language {os.getenv('LANGUAGE_CODE', 'en')}. Please fill out this JSON document {part}. Only complete the specified sections of the document. Ensure the response is formatted as a JSON code block enclosed in triple backticks (```json)."
        
        # Send the prompt and get JSON response
        result = send_json_prompt(browser, prompt)
        
        if result:
            logger.info(f"{mode if mode else 'General'} data processed successfully")
            return result
        else:
            logger.warning(f"No valid response for {mode if mode else 'general'} data")
            return None
            
    except Exception as e:
        logger.error(f"Error processing {mode if mode else 'recipe part'}: {e}", exc_info=True)
        return None