from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import requests as request
import os
from dotenv import load_dotenv

load_dotenv()

def get_caption_from_post(url):
    browser = webdriver.Firefox()
    browser.get(url)
    time.sleep(5) 
    source = browser.page_source
    data = BeautifulSoup(source, 'html.parser')
    
    caption = None
    for span in data.findAll('h1'):
        if span.get_text():
            caption = span.get_text()
    
    browser.close()
    
    if caption:
        print("Caption found:", caption)
        return caption
    else:
        print("Caption not found")
        return None
        
def prompt_chatgpt(caption, part, isStep=False, step_number=None):
    browser = webdriver.Firefox()
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
            prompt = f"Please fill out this JSON document {part} using the following data: {caption}. Only complete the specified sections of the document. Only complete step {step_number} of the recipe. If the step has more then 3 ingredients, only complete the first 3 and finish the json object. The name of the step should be 'x. Step' where x is the step number e.g. 'name': '1. Step'. Only include the current instruction description in the instruction field. The amount value of the ingredient can only be a whole number, please round up if the amount is a decimal."
        else:
            prompt = f"Please fill out this JSON document {part} using the following data: {caption}. Only complete the specified sections of the document."
        textarea.send_keys(prompt)
        textarea.send_keys(Keys.RETURN)
        
        # Wait for the "Send" button to be enabled        
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Senden' and @disabled]")))
        
        response = browser.page_source
        
        # Extract the JSON response from the page source
        soup = BeautifulSoup(response, 'html.parser')
        code_block = soup.find('code', {'class': 'language-json'})
        if code_block:
            json_response = code_block.get_text()
            return json.loads(json_response)
        else:
            return None
        
    except Exception as e:
        print("An error occurred:", e)
        browser.close()
        return None
    finally:
        browser.close()
    
def get_number_of_steps(caption):
    browser = webdriver.Firefox()
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
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Senden' and @disabled]")))
        
        response = browser.page_source
                
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
        browser.close()
        return None
    finally:
        browser.close()
        
def send_to_tandoor(data):
    headers = {'Authorization': f'Bearer {os.getenv('TOKEN')}', 'Content-Type': 'application/json'}
    answer = request.post(f'{os.getenv('BASE_URL')}/api/recipe/', json=data, headers=headers)
    print(json.dumps(answer.json(), indent=2))
        
    
if __name__ == '__main__':
    url = os.getenv('TEST_URL')
    caption = get_caption_from_post(url)
    if caption:
        number_of_steps = get_number_of_steps(caption)
        print(f"Number of steps in the recipe: {number_of_steps}")
        if number_of_steps:
            json_parts = [
                {
                    "name": "string",
                    "description": "string",
                    "keywords": [
                        {
                        "name": "string",
                        "description": "string"
                        }
                    ],
                },
                {
                "name": "string",
                "instruction": "string",
                "ingredients": [
                    {
                    "food": {
                        "name": "string",
                        "plural_name": "string"
                    },
                    "unit": {
                        "name": "string",
                        "plural_name": "string",
                        "description": "string",
                        "base_unit": "string",
                        "open_data_slug": "string"
                    },
                    "amount": "string",
                    "note": "string",
                    "order": 0,
                    "is_header": True,
                    "no_amount": True
                    }
                ],
                "time": 0,
                "order": 0,
                "show_as_header": True,
                "show_ingredients_table": True
                },
                {
                    "servings": 0,
                    "servings_text": "string"
                },
                {
                    "working_time": 0,
                    "waiting_time": 0,
                    "source_url": "string",
                    "internal": True,
                    "show_ingredient_overview":  True,
                } 
            ]
        
            full_json = {}
            
            name_res = prompt_chatgpt(caption, json_parts[0])
            if name_res:
                    full_json.update(name_res)
                    
            print(json.dumps(full_json, indent=2))
                    
            steps = {"steps": []}
            for i in range(1, number_of_steps + 1):
                instruction_res = prompt_chatgpt(caption, json_parts[1], True, i)
                if instruction_res:
                    steps["steps"].append(instruction_res)
                print(json.dumps(steps, indent=2))
            
            full_json.update(steps)
            print(json.dumps(full_json, indent=2))
            
            servings_res = prompt_chatgpt(caption, json_parts[2])
            if servings_res:
                full_json.update(servings_res)
                
            print(json.dumps(full_json, indent=2))
                
            nutrition_res = prompt_chatgpt(caption, json_parts[3])
            if nutrition_res:
                full_json.update(nutrition_res)
                
            full_json["source_url"] = url
                            
            print(json.dumps(full_json, indent=2))
            with open('./output.json', 'w') as outfile:
                json.dump(full_json, outfile, indent=2)
                
            send_to_tandoor(full_json)
                
                

        
        
        
        
