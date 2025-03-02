from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import os
import json

def prompt_chatgpt(caption, part, mode="", step_number=None):
    """
    Prompts Duck AI with a specific task and retrieves the JSON response.
    Args:
        caption (str): The data to be used in the prompt.
        part (str): The JSON document part to be filled out.
        mode (str, optional): The mode of the prompt, which determines the specific task. 
                              Options are "info", "ingredients", "name", "nutrition", "instructions", or "".
                              Defaults to "".
        step_number (int, optional): An optional step number for additional context. Defaults to None.
    Returns:
        dict or None: The JSON response from Duck AI if successful, otherwise None.
    """
    
    print("Prompting Duck AI and waiting for response...")

    match os.getenv("BROWSER"):
        case "firefox":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            browser = webdriver.Firefox(options=options)
        case "chrome":
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            browser = webdriver.Chrome(options=options)
        case "edge":
            options = webdriver.EdgeOptions()
            options.add_argument("--headless")
            browser = webdriver.Edge(options=options)
        case "safari":
            options = webdriver.SafariOptions()
            options.add_argument("--headless")
            browser = webdriver.Safari(options=options)
        case _:
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            browser = webdriver.Firefox(options=options)
        
    browser.get("https://duck.ai/")
    
    try:
        # click through the initial steps
        start_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/div[4]/div/div[2]/main/div/div/div[2]/div/button"))
        )
        start_button.click()
        
        continue_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/div[4]/div/div[2]/main/div/div/div[3]/div/div[2]/button"))
        )
        continue_button.click()
        
        # Wait for the textarea and enter the prompt
        textarea = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@name='user-prompt']"))
        )
        
        match mode:
            case "info":
                prompt = f"Write your Response in the languge {os.getenv('LANGUAGE_CODE')}. Please fill out this JSON document {part} using the following data: {caption}. Only fill out author, description, recipeYield, prepTime and cooktime. The cooktime and pretime should have the format e.g. PT1H for one hour or PT15M for 15 Minutes."
            case "ingredients":
                prompt = f"Write your Response in the languge {os.getenv('LANGUAGE_CODE')}. Please fill out this JSON document {part} using the following data: {caption}. Append the ingredients to the 'recipeIngredient' list. One ingredient per line."
            case "name":  
                prompt = f"Write your Response in the languge {os.getenv('LANGUAGE_CODE')}. Please fill out this JSON document {part} using the following data: {caption}. Keep the name of the recipe short."
            case "nutrition":
                prompt = f"Write your Response in the languge {os.getenv('LANGUAGE_CODE')}. Please fill out this JSON document {part} using the following data: {caption}. Only fill out calories and fatContent with a string."
            case "instructions":
                prompt = f"Write your Response in the languge {os.getenv('LANGUAGE_CODE')}. Please fill out this JSON document {part} using the following data: {caption}. Write the instruction as one long string. No string seperation, just one long text!. Dont add ingredients here. JSON FORMAT IN CODE WINDOW!"
            case "":
                prompt = f"Write your Response in the languge {os.getenv('LANGUAGE_CODE')}. Please fill out this JSON document {part} using the following data: {caption}. Only complete the specified sections of the document."
        
        textarea.send_keys(prompt)
        textarea.send_keys(Keys.RETURN)
        
        # Wait for the "Send" button to be enabled        
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Senden' and @disabled]")))
        
        # Wait for the "Stopp" button to disappear
        WebDriverWait(browser, 60).until_not(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Stopp']")))
        
        # Extract the JSON response from the page source
        response = browser.page_source
        soup = BeautifulSoup(response, 'html.parser')
        code_block = soup.find('code', {'class': 'language-json'})
        if code_block:
            json_response = code_block.get_text()
            return json.loads(json_response)
        else:
            return None
        
    except Exception as e:
        print("An error occurred:", e)
        return None
    finally:
        browser.close()