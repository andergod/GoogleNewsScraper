# Import packages
import sys
from MyGoogleNews3 import GoogleNews
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
import datetime
import numpy as np
import urllib.request
import logging
import threading
import requests
import queue
import http.client as http_client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import random
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium_stealth import stealth
import json
import importlib
import cred


# Load nltk model and download the necessary information
def load_nltk_information():
    nltk.download("vader_lexicon")
    nltk.download("vader_lexicon")
    nltk.download("stopwords")
    nltk.download("punkt")
    # Load the spaCy English model
    nlp = spacy.load("en_core_web_sm")
    return nlp


# Define functions used on this script
def getNews(stock, startdate, enddate, proxies, cookies) -> str:
    googlenews = GoogleNews()
    googlenews = GoogleNews(lang="en", region="US")
    googlenews = GoogleNews(start=startdate, end=enddate)
    googlenews.set_APIKEY(cred.APIKEY)
    googlenews.setproxy(proxies)
    # googlenews.set_cookie(cookies)
    # googlenews.get_news(stock)
    googlenews.search(stock)
    result = [googlenews.page_at(i) for i in range(1, 3)]  # get the news from 10 pages
    result = [item for sublist in result for item in sublist]  # flatten the list
    titles = [element["title"] for element in result]
    descriptions = [element["desc"] for element in result]
    total_text = "".join(titles + descriptions)
    return total_text


def clean_text(text) -> str:
    # Tokenize the text
    words = word_tokenize(text)
    # Remove stop words
    stop_words = set(stopwords.words("english"))
    filtered_words = [
        word.lower()
        for word in words
        if word.isalnum() and word.lower() not in stop_words
    ]
    return " ".join(filtered_words)


def analyze_sentiment(text) -> str:
    # Analyze sentiment of the text and return a trading recommendation.
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(text)["compound"]
    # Assume a simple threshold for sentiment
    if sentiment_score >= 0.1:
        return "Buy"
    elif sentiment_score <= -0.1:
        return "Sell"
    else:
        return "Hold"


def get_main_currency(text, stock_dict) -> str:
    nlk = load_nltk_information()
    doc = nlk(text)
    # Extract entities recognized as cryptocurrencies
    recognized_currencies = [
        ent.text.lower() for ent in doc.ents if ent.text.lower() in stock_dict
    ]
    # If there are recognized cryptocurrencies, return the first one, otherwise return None
    if recognized_currencies:
        return stock_dict[recognized_currencies[0]].upper()
    else:
        return None


def get_week_pairs(start_year, end_year):
    # Start date at the beginning of the start year
    start_date = datetime.date(start_year, 1, 1)
    # Adjust start date if January 1 is not a Monday
    start_date += datetime.timedelta(days=(7 - start_date.weekday()) % 7)
    # End date at the end of the end year
    end_date = datetime.date(end_year, 12, 31)
    # List for storing the week pairs
    week_pairs = []
    # Current date initially set to the first Monday of the start year
    current_date = start_date
    while current_date <= end_date:
        # The Sunday following the Monday
        following_sunday = current_date + datetime.timedelta(days=6)
        # Append the Monday and its corresponding Sunday to the list
        week_pairs.append((current_date, following_sunday))
        # Move to the next Monday (one week ahead)
        current_date += datetime.timedelta(days=7)

    # Convert list of tuples to numpy array with dtype datetime64
    week_pairs_np = np.array(week_pairs, dtype="datetime64[D]")

    return week_pairs_np


def setup_chrome_proxy(proxy):
    chrome_options = Options()
    chrome_options.add_argument(f"--proxy-server={proxy}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def worker(proxy_queue, url, lock, good_proxies):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 "
        "Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    while True:
        try:
            proxy = proxy_queue.get_nowait()
        except queue.Empty:
            break

        try:
            response = requests.get(
                url, proxies={"http": proxy, "https": proxy}, headers=headers, timeout=5
            )
            logging.info(f"Proxy {proxy} returned status {response.status_code}")
            if response.status_code == 200:
                with lock:
                    good_proxies.append(proxy)
            else:
                continue
        except requests.RequestException as e:
            continue
        finally:
            proxy_queue.task_done()


def test_proxies(file_path, num_workers=50, url="http://www.google.com"):

    with open(file_path, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]

    proxy_queue = queue.Queue()
    for proxy in proxies:
        proxy_queue.put(proxy)

    good_proxies = []
    lock = threading.Lock()
    threads = []

    for _ in range(num_workers):
        thread = threading.Thread(
            target=worker, args=(proxy_queue, url, lock, good_proxies)
        )
        thread.start()
        threads.append(thread)

    proxy_queue.join()

    for thread in threads:
        thread.join()

    with open("good_proxies.txt", "w") as file:
        for proxy in good_proxies:
            file.write(f"{proxy}\n")

    return good_proxies


# Function to load cookies from JSON file
def load_cookies(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


# Extract the GOOGLE_ABUSE_EXEMPTION cookie
def find_abuse_exemption_cookie(cookies):
    for cookie in cookies:
        if cookie["name"] == "GOOGLE_ABUSE_EXEMPTION":
            return cookie
    return None


def setup_chrome_proxy(chrome_options, proxy, cookie):
    chrome_options.add_argument(f"--proxy-server={proxy}")
    ua = UserAgent()
    user_agent = ua.random
    chrome_options.add_argument(f"user-agent={user_agent}")

    # Initialize the WebDriver with the specified options
    driver = webdriver.Chrome(options=chrome_options)

    # Set random or specific monitor sizes
    possible_sizes = [(1920, 1080), (1366, 768), (1280, 720), (1440, 900), (1536, 864)]
    chosen_size = random.choice(possible_sizes)
    driver.set_window_size(*chosen_size)

    # Navigate to a page that accepts the cookie
    driver.get("https://www.google.com")
    # Inject the cookie into the browser
    if "expiry" in cookie:
        del cookie["expiry"]  # Selenium might not accept expiry, depends on version
    driver.add_cookie(cookie)

    # Refresh or navigate again to make cookie take effect
    driver.get("https://www.google.com")
    # Use selenium-stealth to avoid being detected as a bot
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


def test_proxies_selenium(file_path, url="http://www.google.com"):

    with open(file_path, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]

    good_proxies = []

    for proxy in proxies:
        print(f"Testing proxy: {proxy}")
        chrome_options = Options()
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")  # Set verbosity to 1

        # Set up Chrome with the proxy inside the function
        cookies = load_cookies("cookies.json")[0]["cookies"]
        abuse_exemption_cookie = find_abuse_exemption_cookie(cookies)
        driver = setup_chrome_proxy(chrome_options, proxy, abuse_exemption_cookie)
        driver.get(url)
        try:
            if url == "http://www.google.com":
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[1]/div[2]/div/img")
                    )
                )
                good_proxies.append(proxy)
                print(f"Proxy {proxy} works!")
            else:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="logo"]/img'))
                )
                good_proxies.append(proxy)
                print(f"Proxy {proxy} works!")
        except Exception as e:
            print(f"Proxy {proxy} failed with error: {e}")
        finally:
            driver.close()
    return good_proxies


def getting_cookies(file_path, url="http://www.google.com"):
    with open(file_path, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]
    all_cookies = []
    for proxy in proxies:
        print(f"Testing proxy: {proxy}")
        chrome_options = Options()
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")  # Set verbosity to 1

        # Set up Chrome with the proxy inside the function
        driver = setup_chrome_proxy(chrome_options, proxy)
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="logo"]/img'))
            )
            print(f"Proxy {proxy} works!")
        except Exception as e:
            print(f"Proxy {proxy} failed with error: {e}")
            print(
                "Please solve the CAPTCHA if needed. Waiting 30 seconds for manual CAPTCHA completion."
            )
            sleep(30)  # Delay to allow time for CAPTCHA solving

            # Save cookies after potentially solving CAPTCHA
            cookies = driver.get_cookies()
            all_cookies.append({"proxy": proxy, "cookies": cookies})

            # Optional: save cookies to a file
            with open("cookies.json", "w") as f:
                json.dump(all_cookies, f)
            print(f"Proxy {proxy} failed with error: {e}")
        finally:
            driver.close()
    return all_cookies


def read_and_parse_proxies(file_path):
    protocol, address = [], []
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()  # Remove any leading/trailing whitespace
            if line:
                protocol_val, address_val = line.split("://")
                protocol.append(protocol_val)
                address.append(address_val)
    return protocol, address


# Function to test the test_proxies function inside the GoogleNews class
def test_proxy_GoogleNews():
    proxies = ""
    url = (
        "https://www.google.com/search?hl=en&gl=en&q=merck&lr="
        "lang_en&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1en,"
        "cdr:1,cd_min:02/01/2020,cd_max:02/28/2020,sbd:1&tbm=nws&start=0"
    )
    GoogleNews1 = GoogleNews()
    return GoogleNews1.try_proxies(proxies, url)


if __name__ == "__main__":
    proxies = ""
    cookie = None
    # total_text=getNews('merck', '02/01/2020', '02/28/2020', proxies, cookie)
    print(test_proxy_GoogleNews())
