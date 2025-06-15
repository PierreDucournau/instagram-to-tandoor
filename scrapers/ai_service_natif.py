import os
import re
import json
from openai import OpenAI
from logs import setup_logging
from dotenv import load_dotenv
logger = setup_logging("openai_ai")
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

# Simule une mémoire de conversation pour chaque session de navigateur
chat_contexts = {}

def get_chat_context(browser_id):
    return chat_contexts.setdefault(browser_id, [])

def initialize_chat(browser, caption):
    """
    Initialise une session de conversation avec GPT en fournissant le contexte de la recette.
    """
    print("#####USING NATIF#####")
    try:
        context_prompt = (
            f"I'm going to ask you questions about this recipe. "
            f"Please use this recipe information as context for all your responses: {caption}"
        )
        browser_id = id(browser)
        chat_context = get_chat_context(browser_id)
        chat_context.append({"role": "system", "content": context_prompt})
        logger.info("Chat initialized successfully with recipe context")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize chat: {e}", exc_info=True)
        return False

def send_raw_prompt(browser, prompt):
    """
    Envoie une requête brute à l'API ChatGPT.
    """
    try:
        browser_id = id(browser)
        chat_context = get_chat_context(browser_id)
        chat_context.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="o4-mini",
            messages=chat_context,
            temperature=0.2,
        )
        reply = response.choices[0].message.content
        chat_context.append({"role": "assistant", "content": reply})
        logger.info("Response received successfully")
        return reply
    except Exception as e:
        logger.error(f"Failed to send prompt: {e}", exc_info=True)
        return None

def extract_json_from_response(response):
    """
    Extrait un JSON depuis une réponse textuelle de ChatGPT.
    """
    try:
        code_blocks = re.findall(r"```json(.*?)```", response, re.DOTALL)
        if code_blocks:
            return json.loads(code_blocks[-1].strip())
        else:
            logger.warning("No JSON code block found in the response")
            return None
    except Exception as e:
        logger.error(f"Failed to extract JSON: {e}", exc_info=True)
        return None

def send_json_prompt(browser, prompt):
    """
    Envoie un prompt et tente d’extraire une réponse JSON.
    """
    response = send_raw_prompt(browser, prompt)
    return extract_json_from_response(response)

def get_number_of_steps(browser, caption=None):
    """
    Récupère le nombre d'étapes d'une recette.
    """
    try:
        prompt = "How many steps are in this recipe? Please respond with only a number."
        response = send_raw_prompt(browser, prompt)
        if response:
            numbers = re.findall(r"\d+", response)
            if numbers:
                count = int(numbers[0])
                logger.info(f"Found {count} steps in the recipe")
                return count
        logger.warning("Could not determine number of steps")
        return None
    except Exception as e:
        logger.error(f"Error in get_number_of_steps: {e}", exc_info=True)
        return None

def process_recipe_part(browser, part, mode="", step_number=None):
    """
    Envoie un prompt formaté à GPT et extrait la réponse structurée.
    """
    try:
        lang = os.getenv("LANGUAGE_CODE", "en")

        if mode == "step" or step_number is not None:
            prompt = f"Write your Response in {lang}. Please fill out this JSON document {part}. Only complete step {step_number} of the recipe. Only include up to 3 ingredients. Use decimals for amounts. Do not repeat ingredients. Step name should be '{step_number}.'. Wrap your response in ```json code block."
        elif mode == "info":
            prompt = f"Write your Response in {lang}. Please fill out this JSON document {part}. Only fill out author, description, recipeYield, prepTime and cooktime. Format times as PT15M or PT1H."
        elif mode == "ingredients":
            prompt = f"Write your Response in {lang}. Please fill out this JSON document {part}. Append ingredients to 'recipeIngredient'. One per line."
        elif mode == "name":
            prompt = f"Write your Response in {lang}. Please fill out this JSON document {part}. Keep the name short."
        elif mode == "nutrition":
            prompt = f"Write your Response in {lang}. Please fill out this JSON document {part}. Only include calories and fatContent."
        elif mode == "instructions":
            prompt = f"Write your Response in {lang}. Please fill out this JSON document {part}. Write the instructions as one long string. Don't include ingredients."
        else:
            prompt = f"Write your Response in {lang}. Please fill out this JSON document {part}. Only complete the specified sections. Wrap your response in ```json code block."

        return send_json_prompt(browser, prompt)
    except Exception as e:
        logger.error(f"Error processing {mode if mode else 'recipe part'}: {e}", exc_info=True)
        return None