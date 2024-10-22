""" main module used for doing webscrapping and data analysis of 
 our data and potential trading recommendations"""

# Local imports
import datetime
import logging
import threading
import queue
from pathlib import Path
import json
from time import sleep
import random
import os

# Third-party imports
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium_stealth import stealth

# From other files
import app.cred as cred
from app.google_news_webscrap import GoogleNews


def load_nltk_information():
    """Load nltk model and download the necessary information"""
    nltk.download("vader_lexicon")
    nltk.download("vader_lexicon")
    nltk.download("stopwords")
    nltk.download("punkt")
    # Load the spaCy English model
    nlp = spacy.load("en_core_web_sm")
    return nlp


def getNews(stock, start_date, end_date, proxies, cookies) -> str:
    """Function to get news from Google News"""
    googlenews = GoogleNews()
    googlenews = GoogleNews(lang="en", region="US", start=start_date, end=end_date)
    googlenews.set_api_key(cred.APIKEY)
    googlenews.set_key(stock)
    result = googlenews.new_from_pages([1, 2])
    result = [
        item for sublist in result.values() for item in sublist
    ]  # flatten the list
    titles = [element["title"] for element in result]
    descriptions = [element["desc"] for element in result]
    total_text = "".join(titles + descriptions)
    return total_text


def clean_text(text) -> str:
    """Function to clean the text"""
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
    """Analyze sentiment of the text and return a trading recommendation."""
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(text)["compound"]
    # Assume a simple threshold for sentiment
    if sentiment_score >= 0.1:
        return "Buy"
    elif sentiment_score <= -0.1:
        return "Sell"
    else:
        return "Hold"


def get_stock(text, stock_dict) -> str:
    """Get the main currency from a list of recognized cryptocurrencies."""
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
        week_pairs.append(
            (current_date.strftime("%d/%m/%Y"), following_sunday.strftime("%d/%m/%Y"))
        )
        # Move to the next Monday (one week ahead)
        current_date += datetime.timedelta(days=7)

    return week_pairs


if __name__ == "__main__":
    # Potential improvement:
    # I could double check the news is whithin the range on the class
    weeks = get_week_pairs(2015, 2016)
    PROXIES = ""
    COOKIES = None
    STOCK = "merck"
    files_on_data = os.listdir("data")
    dates_on_data = [
        "/".join(file.split(".")[0].split("_")[1:4]) for file in files_on_data
    ]
    for start_date, end_date in weeks:
        if start_date not in dates_on_data:
            TOTAL_TEXT = getNews(STOCK, start_date, end_date, PROXIES, COOKIES)
            start_date_for_file = start_date.replace("/", "_")
            name_file = f"{STOCK}_{start_date_for_file}.txt"
            FILE_PATH = Path("data") / name_file
            with open(FILE_PATH, "w", encoding="utf-8") as file:
                file.write(TOTAL_TEXT)
