# MODULES
# Using my own proxy given that proxy rotation is not working
import re
import urllib.request
import dateparser, copy
from bs4 import BeautifulSoup as Soup
from dateutil.parser import parse
import random
import datetime
from dateutil.relativedelta import relativedelta
import logging
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
import http.client as http_client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium_stealth import stealth
import json
import requests
import asyncio
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV2ProxylessRequest
from datetime import timedelta
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    WebDriverException,
    InvalidArgumentException,
)

# METHODS


def lexical_date_parser(date_to_check):
    if date_to_check == "":
        return ("", None)
    datetime_tmp = None
    date_tmp = copy.copy(date_to_check)
    try:
        date_tmp = date_tmp[date_tmp.rfind("..") + 2 :]
        datetime_tmp = dateparser.parse(date_tmp)
    except:
        date_tmp = None
        datetime_tmp = None

    if datetime_tmp is None:
        date_tmp = date_to_check
    else:
        datetime_tmp = datetime_tmp.replace(tzinfo=None)

    if date_tmp[0] == " ":
        date_tmp = date_tmp[1:]
    return date_tmp, datetime_tmp


def define_date(date):
    months = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Sept": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
        "01": 1,
        "02": 2,
        "03": 3,
        "04": 4,
        "05": 5,
        "06": 6,
        "07": 7,
        "08": 8,
        "09": 9,
        "10": 10,
        "11": 11,
        "12": 12,
    }
    try:
        if " ago" in date.lower():
            q = int(date.split()[-3])
            if "minutes" in date.lower() or "mins" in date.lower():
                return datetime.datetime.now() + relativedelta(minutes=-q)
            elif "hour" in date.lower():
                return datetime.datetime.now() + relativedelta(hours=-q)
            elif "day" in date.lower():
                return datetime.datetime.now() + relativedelta(days=-q)
            elif "week" in date.lower():
                return datetime.datetime.now() + relativedelta(days=-7 * q)
            elif "month" in date.lower():
                return datetime.datetime.now() + relativedelta(months=-q)
        elif "yesterday" in date.lower():
            return datetime.datetime.now() + relativedelta(days=-1)
        else:
            date_list = date.replace("/", " ").split(" ")
            if len(date_list) == 2:
                date_list.append(datetime.datetime.now().year)
            elif len(date_list) == 3:
                if date_list[0] == "":
                    date_list[0] = "1"
            return datetime.datetime(
                day=int(date_list[0]),
                month=months[date_list[1]],
                year=int(date_list[2]),
            )
    except:
        return float("nan")


def element_to_dict(element):
    """Convert a BeautifulSoup element to a JSON Dictionary"""
    # If it's a NavigableString (plain text), just return the string
    if isinstance(element, str):
        return element

    # If it's a tag, return a dictionary with tag name, attributes, and children
    result = {
        "tag": element.name,
        "attributes": element.attrs,  # Tag attributes
        "children": [],  # To hold any child elements
    }

    # Recursively convert children (contents) into the dictionary
    for child in element.contents:
        if isinstance(child, str):
            result["children"].append(child.strip())  # Add text nodes directly
        else:
            result["children"].append(
                element_to_dict(child)
            )  # Recursively process elements

    return result


# CLASSES


class GoogleNews:

    def __init__(
        self, lang="en", period="", start="", end="", encode="utf-8", region=None
    ):
        self.__texts = []
        self.__links = []
        self.__results = []
        self.__totalcount = 0
        self.proxy = []
        self.user_agent = (
            "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0"
        )
        self.__lang = lang
        if region:
            self.accept_language = lang + "-" + region + "," + lang + ";q=0.9"
            self.headers = {
                "User-Agent": self.user_agent,
                "Accept-Language": self.accept_language,
            }
        else:
            self.headers = {"User-Agent": self.user_agent}
        self.__period = period
        self.__start = start
        self.__end = end
        self.__encode = encode
        self.__exception = False
        self.__version = "1.6.14"
        self.chrome_options = Options()
        self.chrome_options.add_argument("--enable-logging")
        self.chrome_options.add_argument("--v=1")  # Set verbosity to 1
        self.cookies = {}
        self.driver = None
        self.api_key = None
        self.cap_monster_client = None
        self.ClientOptions = None
        self.recaptcha_request = None
        self.url = None
        # Use to dump the result from webscrapping into a json file
        self.save_results_formatted = False
        # Use to dump the raw html into a json file
        self.save_raw_html = False
        # Use to return the results from the webscrapping
        self.return_results = False

    # get the version of the package
    def getVersion(self):
        return self.__version

    def getResults(self):
        return self.__results

    def enableException(self, enable=True):
        self.__exception = enable

    # Setters
    def set_return_results(self, return_results):
        """
        Set the return_results to True or False.
        If True, the results will be returned by the get_page() method
        """
        self.return_results = return_results

    def set_save_results_formatted(self, save_results_formatted):
        """
        Set the save_results_formatted to True or False.
        If True, the data will be saved into a json file
        """
        self.save_results_formatted = save_results_formatted

    def set_save_raw_html(self, save_raw_html):
        """
        Set the save_raw_html to True or False.
        If True, the raw html will be saved into a json file
        """
        self.save_raw_html = save_raw_html

    def set_lang(self, lang):
        self.__lang = lang

    def setlang(self, lang):
        """Don't remove this, will affect old version user when upgrade"""
        self.set_lang(lang)

    def set_period(self, period):
        self.__period = period

    def setperiod(self, period):
        """Don't remove this, will affect old version user when upgrade"""
        self.set_period(period)

    def set_time_range(self, start, end):
        self.__start = start
        self.__end = end

    def setTimeRange(self, start, end):
        """Don't remove this, will affect old version user when upgrade"""
        self.set_time_range(start, end)

    def set_encode(self, encode):
        self.__encode = encode

    def setencode(self, encode):
        """Don't remove this, will affect old version user when upgrade"""
        self.set_encode(encode)

    def set_key(self, key):
        """Set the key for the search"""
        self.__key = key

    def search(self, key):
        """
        Searches for a term in google.com in the news section and retrieves
        the first page into __results.
        Parameters:
        key = the search term
        """
        self.__key = key
        if self.__encode != "":
            self.__key = urllib.request.quote(self.__key.encode(self.__encode))
        # In case we want to return the results
        if self.return_results:
            return self.get_page()
        else:
            self.get_page()

    def setproxy(self, proxy):
        self.proxy = proxy

    def set_cookie(self, cookie):
        self.cookies = cookie

    def check_proxy(self, proxy):
        """
        Check if the proxy is working sending a
        request to httpbin.org/ip
        """
        types = ["http", "https", "socks4", "socks5"]
        url = "http://httpbin.org/ip"
        for type in types:
            try:
                proxies = {
                    "http": f"{type}://{proxy}",
                    "https": f"{type}://{proxy}",
                }
                response = requests.get(url, proxies=proxies, timeout=5)
                if response.status_code == 200:
                    return type
            except requests.exceptions.RequestException as e:
                print(f"Proxy {type} not working: {e}")
        return None

    def set_api_key(self, api_key):
        """Set api_key for CapMonster"""
        self.api_key = api_key
        self.ClientOptions = ClientOptions(api_key=api_key)
        self.cap_monster_client = CapMonsterClient(options=ClientOptions)

    async def solve_catpcha_google(self, website_url, CaptchaKey):
        """Uses the CaoMonster API to solve the recaptcha"""
        self.recaptcha_request = RecaptchaV2ProxylessRequest(
            websiteUrl=website_url, websiteKey=CaptchaKey
        )
        result = await self.cap_monster_client.solve_captcha(self.recaptcha_request)
        return result
        # return result['gRecaptchaResponse']

    def setup_chrome_proxy(self, chrome_options, proxy, cookie):
        """Set up the Chrome browser with the proxy and cookie"""
        # chrome_options.add_argument(f'--proxy-server={proxy}')
        ua = UserAgent()
        user_agent = ua.random
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--no-sandbox")  # Add this line
        chrome_options.add_argument(
            "--disable-dev-shm-usage"
        )  # Optionally, reduce memory usage

        # Initialize the WebDriver with the specified options
        # driver_service = Service('../chromedriver')
        driver = webdriver.Chrome(options=chrome_options)

        # Set random or specific monitor sizes
        possible_sizes = [
            (1920, 1080),
            (1366, 768),
            (1280, 720),
            (1440, 900),
            (1536, 864),
        ]
        chosen_size = random.choice(possible_sizes)
        driver.set_window_size(*chosen_size)

        # Navigate to a page that accepts the cookie
        # driver.get('https://www.google.com')

        # Inject the cookie into the browser
        # Stop passing the cookie for now
        # if 'expiry' in cookie:
        #     del cookie['expiry']  # Selenium might not accept expiry,
        # depends on version
        # driver.add_cookie(cookie)

        # Refresh or navigate again to make cookie take effect
        # driver.get('https://www.google.com')
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

    def open_browser(self, proxies, url, max_retries=10):
        """Opens the browser with the proxy, abd cc and retries if it fails"""
        for attempt in range(max_retries):
            proxy = "None"
            try:
                self.driver = self.setup_chrome_proxy(
                    self.chrome_options, proxy, self.cookies
                )
                self.driver.get(url)
                print(f"Connected using proxy: {proxy}")
                return self.driver  # Return the self.driver if successful
            except Exception as e:
                print(
                    f"Failed to connect using proxy: {proxy}, Attempt: {attempt + 1}, Error: {e}"
                )
                self.driver.quit()
                sleep(3)  # Wait before retrying
        print("Failed to connect using all provided proxies.")
        return None

    async def catcha_solver(self):
        """Solve the recaptcha using CapMonster"""
        sleep(5)
        key = self.driver.find_element(By.XPATH, '//*[@id="recaptcha"]').get_attribute(
            "data-sitekey"
        )
        # recaptchaDataSValue=self.driver.find_element(By.XPATH,
        # '//*[@id="recaptcha"]').get_attribute('data-s') if needed
        recaptcha_response = await self.solve_catpcha_google(
            self.driver.current_url, key
        )  # his is the error
        print(f"recatcha respone: {recaptcha_response}")
        print(f"data-sitekey: {key}")
        print(f"url: {self.driver.current_url}")
        self.driver.execute_script(
            f'document.getElementById("g-recaptcha-response").innerHTML="{recaptcha_response}";'
        )
        sleep(2)

    async def build_response2(self, url):
        """Reworkign the webscrapping process and the parsing"""
        # Getting the url and trying a proxy
        full_url = url.replace(
            "search?", "search?hl=" + self.__lang + "&gl=" + self.__lang + "&"
        )
        self.driver = self.open_browser(self.proxy, full_url)

        # Check if you have sent to a "Before you continue to Google" page
        if "consent" in self.driver.current_url:
            agreed_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[@aria-label="Accept all"]')
                )
            )
            agreed_button.click()
            sleep(2)

        # In case we have a recaptcha
        if "sorry" in self.driver.current_url:
            self.catcha_solver(self.driver)

        sleep(2)

        # After the page has loaded, extract the page source
        page_source = self.driver.page_source

        # Parse the page source with BeautifulSoup
        pretty_html = Soup(page_source, "html.parser").prettify()
        if self.save_raw_html:
            with open("raw_html.html", "w", encoding="utf-8") as f:
                f.write(pretty_html)

        # Close the webdriver
        self.driver.close()

        # Perform analysis or extraction from the page
        result = self.result_parse_new(page_source)
        return result

    def remove_after_last_fullstop(self, s):
        """Remove the text after the last '.' in the string.
        If there is no '.', return the string as is."""
        # Find the last occurrence of the full stop
        last_period_index = s.rfind(".")
        # Slice the string up to the last full stop
        return s[: last_period_index + 1] if last_period_index != -1 else s

    def url_search_formatting(self, page=1, key=""):
        """Format the URL for the search a first time"""
        try:
            # Base URL and common parameters
            base_url = "https://www.google.com/search"
            common_params = (
                f"q={self.__key}&lr=lang_{self.__lang}&"
                "biw=1920&bih=976&source=lnt&&tbm=nws&sbd=1"
            )  # Note the double &&

            # Pagination parameter
            pagination_param = f"&start={10 * (page - 1)}"

            # Handle the different cases for date or period filters
            if self.__start and self.__end:
                # Date range filter
                date_params = (
                    f"&tbs=lr:lang_1{self.__lang},cdr:1,cd_min:{self.__start},"
                    f"cd_max:{self.__end}"
                )
                self.url = f"{base_url}?{common_params}{date_params}{pagination_param}"
            elif self.__period:
                # Pre-defined period filter
                period_params = f"&tbs=lr:lang_1{self.__lang},qdr:{self.__period}"
                self.url = (
                    f"{base_url}?{common_params}{period_params}{pagination_param}"
                )
            else:
                # No date or period filter, just language and pagination
                self.url = f"{base_url}?{common_params}{pagination_param}"

            return self.url
        except AttributeError:
            raise AttributeError("You need to run a search() before using get_page().")

    def result_parse_new(self, html_content):
        """Potential replacement of the result_parse2. Using beautiful soup"""
        # Initialize BeautifulSoup parser
        soup = Soup(html_content, "html.parser")

        # Find all div elements with class 'SoAPf'
        articles = soup.find_all("div", class_="SoAPf")

        for article in articles:
            # Extract title from the div with role="heading"
            title_tag = article.find("div", role="heading")
            title = title_tag.get_text(strip=True) if title_tag else "No title"

            # Extract description from the div with class 'GI74Re'
            desc_tag = article.find("div", class_="GI74Re")
            desc = desc_tag.get_text(strip=True) if desc_tag else "No description"

            # Extract date from the span element within the div with class 'OSrXXb'
            date_tag = article.find("div", class_="OSrXXb").find("span")
            date = date_tag.get_text(strip=True) if date_tag else "No date"

            # Extract link if present (optional, depending on your HTML structure)
            link_tag = article.find_parent("a")  # Assuming <a> wraps around <div>
            link = (
                link_tag["href"]
                if link_tag and link_tag.has_attr("href")
                else "No link"
            )

            # Add title and link to separate lists
            self.__texts.append(title)
            self.__links.append(link)

            # Append extracted information into the results list
            self.__results.append(
                {
                    "title": title,
                    "date": date,
                    "desc": desc,
                    "link": link,
                }
            )
        return self.__results

    def page_at(self, page=1):
        """
        Retrieves a specific page from google.com in the news
        sections into results.
        Parameter:
        page = number of the page to be retrieved
        """
        # Getting the formatted URL
        formated_url = self.url_search_formatting(page, self.__key)
        # Executing and the webscrap and potential exceptions
        try:
            results = asyncio.run(self.build_response2(formated_url))
        except NoSuchElementException as e_no_element:
            print(f"Element not found: {e_no_element}")
        except TimeoutException as e_timeout:
            print(f"Timeout occurred: {e_timeout}")
        except ElementNotInteractableException as e_not_interactable:
            print(f"Element not interactable: {e_not_interactable}")
        except StaleElementReferenceException as e_stale:
            print(f"Stale element reference: {e_stale}")
        except InvalidArgumentException as e_invalid_arg:
            print(f"Invalid argument: {e_invalid_arg}")
        except WebDriverException as e_webdriver:
            print(f"WebDriver error: {e_webdriver}")
        return results

    def get_page(self, page=1):
        # this is the one that runs when we do search()
        """
        Retrieves a specific page from google.com in
        the news sections into __results.
        Parameter:
        page = number of the page to be retrieved
        """
        formatted_url = self.url_search_formatting(page, self.__key)
        # formatted_url = self.url_search_old(page)
        # Executing and the webscrap and potential exceptions
        try:
            content = asyncio.run(self.build_response2(formatted_url))
        except NoSuchElementException as e_no_element:
            print(f"Element not found: {e_no_element}")
        except TimeoutException as e_timeout:
            print(f"Timeout occurred: {e_timeout}")
        except ElementNotInteractableException as e_not_interactable:
            print(f"Element not interactable: {e_not_interactable}")
        except StaleElementReferenceException as e_stale:
            print(f"Stale element reference: {e_stale}")
        except InvalidArgumentException as e_invalid_arg:
            print(f"Invalid argument: {e_invalid_arg}")
        except WebDriverException as e_webdriver:
            print(f"WebDriver error: {e_webdriver}")

        # Save the results into a json file
        if self.save_results_formatted:
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=4)

        return content

    def getpage(self, page=1):
        """Don't remove this, will affect old version user when upgrade"""
        self.get_page(page)

    def get_news(self, key="", deamplify=False):
        if key != "":
            if self.__period != "":
                key += f" when:{self.__period}"
        else:
            if self.__period != "":
                key += f"when:{self.__period}"
        key = urllib.request.quote(key.encode(self.__encode))
        start = f"{self.__start[-4:]}-{self.__start[:2]}-{self.__start[3:5]}"
        end = f"{self.__end[-4:]}-{self.__end[:2]}-{self.__end[3:5]}"

        if self.__start == "" or self.__end == "":
            self.url = "https://news.google.com/search?q={}&hl={}".format(
                key, self.__period, self.__lang.lower()
            )
        else:
            self.url = (
                "https://news.google.com/search?q={}+before:{}+after:{}&hl={}".format(
                    key, end, start, self.__lang.lower()
                )
            )

        try:
            self.req = urllib.request.Request(self.url, headers=self.headers)
            self.response = urllib.request.urlopen(self.req)
            self.page = self.response.read()
            self.content = Soup(self.page, "html.parser")
            articles = self.content.select("article")
            for article in articles:
                try:
                    # title
                    try:
                        title = article.findAll("div")[2].findAll("a")[0].text
                    except:
                        title = None
                    # description
                    try:
                        desc = None
                    except:
                        desc = None
                    # date
                    try:
                        date = article.find("time").text
                        # date,datetime_tmp = lexial_date_parser(date)
                    except:
                        date = None
                    # datetime
                    try:
                        datetime_chars = article.find("time").get("datetime")
                        datetime_obj = parse(datetime_chars).replace(tzinfo=None)
                    except:
                        datetime_obj = None
                    # link
                    if deamplify:
                        try:
                            link = (
                                "news.google.com/"
                                + article.find("div").find("a").get("href")[2:]
                            )
                        except Exception as deamp_e:
                            print(deamp_e)
                            link = (
                                article.find("article")
                                .get("jslog")
                                .split("2:")[1]
                                .split(";")[0]
                            )
                    else:
                        try:
                            link = (
                                "news.google.com/"
                                + article.find("div").find("a").get("href")[2:]
                            )
                        except Exception as deamp_e:
                            print(deamp_e)
                            link = None
                    self.__texts.append(title)
                    self.__links.append(link)
                    if link.startswith("https://www.youtube.com/watch?v="):
                        desc = "video"
                    # image
                    try:
                        img = "news.google.com" + article.find("figure").find(
                            "img"
                        ).get("src")
                    except:
                        img = None
                    # site
                    try:
                        site = article.find("time").parent.find("a").text
                    except:
                        site = None
                    try:
                        media = (
                            article.find("div")
                            .findAll("div")[1]
                            .find("div")
                            .find("div")
                            .find("div")
                            .text
                        )
                    except:
                        media = None
                    # reporter
                    try:
                        reporter = article.findAll("span")[2].text
                    except:
                        reporter = None
                    # collection
                    self.__results.append(
                        {
                            "title": title,
                            "desc": desc,
                            "date": date,
                            "datetime": define_date(date),
                            "link": link,
                            "img": img,
                            "media": media,
                            "site": site,
                            "reporter": reporter,
                        }
                    )
                except Exception as e_article:
                    print(e_article)
        except Exception as e_parser:
            print(e_parser)
            if self.__exception:
                raise Exception(e_parser)
            else:
                pass

    def total_count(self):
        return self.__totalcount

    def result(self, sort=False):
        """Don't remove this, will affect old version user when upgrade"""
        return self.results(sort)

    def results(self, sort=False):
        """Returns the __results.
        New feature: include datatime and sort the
        articles in decreasing order"""
        results = self.__results
        if sort:
            try:
                results.sort(key=lambda x: x["datetime"], reverse=True)
            except Exception as e_sort:
                print(e_sort)
                if self.__exception:
                    raise Exception(e_sort)
                else:
                    pass
                results = self.__results
        return results

    def get_texts(self):
        """Returns only the __texts of the __results."""
        return self.__texts

    def gettext(self):
        """Don't remove this, will affect old version user when upgrade"""
        return self.get_texts()

    def get_links(self):
        """Returns only the __links of the __results."""
        return self.__links

    def clear(self):
        self.__texts = []
        self.__links = []
        self.__results = []
        self.__totalcount = 0
