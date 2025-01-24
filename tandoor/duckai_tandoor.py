from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import os
import json

def prompt_chatgpt(caption, part, isStep=False, step_number=None):
    """
    Interacts with the Duck.ai website to generate a JSON response based on the provided caption and part.
    Args:
        caption (str): The caption or data to be used for generating the JSON response.
        part (str): The part of the JSON document to be filled out.
        isStep (bool, optional): Indicates whether the prompt is for a specific step in a recipe. Defaults to False.
        step_number (int, optional): The step number to be completed if isStep is True. Defaults to None.
    Returns:
        dict or None: The JSON response from Duck.ai if successful, otherwise None.
    """
    
    print("Prompting Duck AI and waiting for response...")

    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)
    browser.get("https://duck.ai/")
    
    try:
        # click through the initial steps
        start_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/div[4]/div/div[2]/main/div/div/div[2]/div/button"))
        )
        start_button.click()
        
        continue_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/div[4]/div/div[2]/main/div/div/div[3]/div/button"))
        )
        continue_button.click()
        
        agree_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/div[4]/div/div[2]/main/div/div/div[4]/div/div[2]/button"))
        )
        agree_button.click()
        
        # Wait for the textarea and enter the prompt
        textarea = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@name='user-prompt']"))
        )
        
        if isStep:
            prompt = f"Write your Response in the languge {os.getenv('LANGUAGE_CODE')}. Please fill out this JSON document {part} using the following data: {caption}. Only complete the specified sections of the document. Only complete step {step_number} of the recipe. If the step has more then 3 ingredients, only complete the first 3 and finish the json object. The name of the step should be the step number e.g. 'name': '1.'. Only include the current instruction description in the instruction field. The amount value of the ingredient can only be a whole number, please round up if the amount is a decimal."
        else:
            prompt = f"Write your Response in the languge {os.getenv('LANGUAGE_CODE')}. Please fill out this JSON document {part} using the following data: {caption}. Only complete the specified sections of the document."
        textarea.send_keys(prompt)
        textarea.send_keys(Keys.RETURN)
        
        # Wait for the "Send" button to be enabled        
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit' and @disabled]")))        
        # Wait for the "Stopp" button to disappear
        WebDriverWait(browser, 60).until_not(EC.presence_of_element_located((By.XPATH, "//button//rect[@width='10' and @height='10']")))
        
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

def get_number_of_steps(caption):
    """
    Extracts the number of steps from an Instagram recipe caption using the Duck.ai website.
    Args:
        caption (str): The Instagram recipe caption to analyze.
    Returns:
        int: The number of steps in the recipe caption if successfully extracted, otherwise None.
    Raises:
        Exception: If an error occurs during the web scraping process.
    """
    
    print("Prompting Duck AI and waiting for response...")
    
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)
    browser.get("https://duck.ai/")
    
    try:
        # click through the initial steps

        start_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/div[4]/div/div[2]/main/div/div/div[2]/div/button"))
        )
        start_button.click()
        
        continue_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/div[4]/div/div[2]/main/div/div/div[3]/div/button"))
        )
        continue_button.click()
        
        agree_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/div[4]/div/div[2]/main/div/div/div[4]/div/div[2]/button"))
        )
        agree_button.click()
        
        # Wait for the textarea and enter the prompt
        textarea = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@name='user-prompt']"))
        )
        
        prompt = f"How many steps are in the following Instagram recipe caption? Please return only a number: {caption}"
        textarea.send_keys(prompt)
        textarea.send_keys(Keys.RETURN)
        
        # Wait for the "Send" button to be enabled        
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit' and @disabled]")))        
        # Wait for the "Stopp" button to disappear
        WebDriverWait(browser, 60).until_not(EC.presence_of_element_located((By.XPATH, "//button//rect[@width='10' and @height='10']")))
        
        # Extract the response from the page source
        response = browser.page_source
        soup = BeautifulSoup(response, 'html.parser')
        div_with_heading = soup.find('div', {'heading': 'GPT-4o mini'})
        if div_with_heading:
            number_div = div_with_heading.find('div', {'class': 'VrBPSncUavA1d7C9kAc5'})
            if number_div:
                paragraph = number_div.find('p')
                if paragraph:
                    try:
                        number_of_steps = int(paragraph.get_text().strip())
                        return number_of_steps
                    except ValueError:
                        print("An error occurred: The extracted text is not a valid number.")
                        return None
        return None
        
    except Exception as e:
        print("An error occurred:", e)
        return None
    finally:
        browser.close()