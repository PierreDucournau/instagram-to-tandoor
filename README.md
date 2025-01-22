# Instagram -> Tandoor / Mealie

Since I often browse Instagram for recipes, I wanted a way to save them to my own recipe collection on [Tandoor](https://github.com/TandoorRecipes/recipes). Getting an Instagram API took me too long, so I decided to use [Selenium](https://github.com/SeleniumHQ/selenium) to scrape the recipe from a provided Instagram post. Since everyone writes their recipes differently and it's almost impossible to parse them all into the required JSON format, I decided to use an LLM. My notebook is not powerful enough to use [Ollama](https://ollama.com/) for this, so I decided to use [DuckAi](https://duck.ai). To automate the query process, I also used Selenium to interact with the website.
When I get all the necessary JSON parts, I combine them and send them to Tandoor using the implemented API.

The problem with LLM's is that they are not deterministic, so the output can be variable in quality. Sometimes you have to adjust the output manually, but in most cases it's good enough to use as is.

## Installation:

Make sure you have python 3.x installed on your system.

Without venv:

```
git clone https://github.com/doen1el/instagram-to-tandoor.git instagram-to-tandoor
cd instagram-to-tandoor
pip install -r requirements.txt
```

With venv:

```
git clone https://github.com/doen1el/instagram-to-tandoor.git instagram-to-tandoor
cd instagram-to-tandoor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Preparation:

Create an `.env` file in the root directory of the project and add the following

### Tandoor

```
BASE_URL_TANDOOR=https://YOUR_TANDOOR_URL
TOKEN_TANDOOR=YOUR_TANDOOR_TOKEN
LANGUAGE_CODE=de (or en, etc.)
```

You can retrieve your tandoor token by

1. Visiting `https://YOUR_TANDOOR_URL/settings/#api`.
2. Creating a new token using the `write read bookmarklet` and a name of your choice
3. Copy the token and add it to the `.env` file

---

### Mealie

```
BASE_URL_MEALIE=https://YOUR_MEALIE_URL
TOKEN_MEALIE=YOUR_TANDOOR_TOKEN
LANGUAGE_CODE=de (or en, etc.)
```

You can retrieve your tandoor token by

1. Visiting `https://YOUR_TANDOOR_URL/user/profile`.
2. Creating a new api token with a name of your choice
3. Copy the token and add it to the `.env` file

Since Selenium uses the installed web browser, you need to adapt the `instagram.py` and `duckai.py` files to your browser of choice. The default is `Firefox`.

## Usage:

```
python3 main.py -url [https://www.instagram.com/...] -mode [mealie (m) | tandoor (t)]
```

or use

```
python3 main.py -help
```

for more information.

## Contributing:

Feel free to open an issue, pull request, or simply fork the project.

## Disclaimer:

By using this application you accept [DuckDuckGo AI Chat ToS](https://duckduckgo.com/aichat/privacy-terms)

## Todo's:

- [ ] Dockerize the project
- [ ] Create a GUI
- [ ] Optimize prompting
- [ ] Add more error handling

## Special thanks to the following projects:

- [Tandoor](https://github.com/TandoorRecipes/recipes)
- [Selenium](https://github.com/SeleniumHQ/selenium)
- [BeautfiulSoup4](https://github.com/wention/BeautifulSoup4?tab=readme-ov-file)
