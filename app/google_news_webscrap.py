"""main class used for webscrappinng using 
selenium and capMonster to solve the recaptcha"""

# Standard imports
import urllib.request
import asyncio
from time import sleep
import json

# Third party imports
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    WebDriverException,
    InvalidArgumentException,
    SessionNotCreatedException,
)

# Import from local files
import app.capmonster as capmonster
import app.Webdriver as Webdriver

# METHODS


# CLASSES


class GoogleNews:
    """Main class used for webscrapping using selenium and capMonster to solve the recaptcha"""

    def __init__(
        self, lang="en", period="", start="", end="", encode="utf-8", region=None
    ):
        self.__texts = []
        self.__links = []
        self.__results = []
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
        self.__version = "1.6.14"
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

    # Saving the API key for CapMonster
    def set_api_key(self, api_key: str) -> None:
        """Set api_key for CapMonster"""
        self.cap_monster_client = capmonster.set_api_key(api_key)

    # Functions to solve the recaptcha
    async def catcha_solver(self) -> None:
        """Solve the recaptcha using CapMonster"""
        sleep(2)  # Sleep to allow the page to fully load

        key = None

        # Check if the element with id="recaptcha" exists
        recaptcha_element = self.driver.find_elements(By.XPATH, '//*[@id="recaptcha"]')
        if recaptcha_element:
            # If it exists, extract the 'data-sitekey' from it
            key = recaptcha_element[0].get_attribute("data-sitekey")
        else:
            # Check for the element with class "g-recaptcha"
            grecaptcha_element = self.driver.find_elements(
                By.XPATH, '//div[contains(@class,"g-recaptcha")]'
            )
            if grecaptcha_element:
                # If it exists, extract the 'data-sitekey' from it
                key = grecaptcha_element[0].get_attribute("data-sitekey")

        # If neither element is found, raise an exception
        if key is None:
            raise ValueError("No reCAPTCHA element found on the page.")

        # If we successfully found a sitekey
        recaptcha_response = await capmonster.capmonster_catpcha_response(
            self.driver.current_url, key, self.cap_monster_client
        )
        solve_actions = recaptcha_response["gRecaptchaResponse"]

        # Inject the response into the reCAPTCHA response field
        self.driver.execute_script(
            f'document.getElementById("g-recaptcha-response").innerHTML="{solve_actions}";'
        )
        self.driver.find_element(By.ID, "recaptcha-demo-submit").click()

    # Functions relating to Google news processing
    async def get_response(self):
        """Reworkign the webscrapping process and the parsing"""
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
            self.catcha_solver()

        sleep(2)

        # After the page has loaded, extract the page source
        page_source = self.driver.page_source

        # Parse the page source with BeautifulSoup
        pretty_html = Soup(page_source, "html.parser").prettify()
        if self.save_raw_html:
            with open("raw_html.html", "w", encoding="utf-8") as f:
                f.write(pretty_html)
        return page_source

    def url_search_formatting(self, page=1):
        """Creates the URL for the search depending of the
        start, end, period, page and language"""

        def from_international_to_us_date(date: str) -> str:
            """Converts international date format to US date format"""
            return f"{date[3:5]}/{date[:2]}/{date[-4:]}"

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
                    f"&tbs=lr:lang_1{self.__lang},cdr:1,cd_min"
                    f":{from_international_to_us_date(self.__start)},"
                    f"cd_max:{from_international_to_us_date(self.__end)}"
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

    def result_parse(self, html_content):
        """Parse html results using beautiful soup"""
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

    # Main functions to get the webscrapping and results
    def page_at(self, page=1):
        """
        Retrieves a specific page from google.com in the news
        sections into results.
        Parameter:
        page = number of the page to be retrieved
        """
        # Getting the formatted URL
        formatted_url = self.url_search_formatting(page)
        # Opening the browser
        self.driver = Webdriver.open_browser(formatted_url)
        # Executing and the webscrap and potential exceptions
        try:
            page_source = asyncio.run(self.get_response())
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

        # Close the webdriver
        self.driver.close()

        # Perform parse and save info within the class
        result = self.result_parse(page_source)

        # Save the results into a json file
        if self.save_results_formatted:
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
        return result

    def new_from_pages(self, pages: list = None):
        """
        Retrives the news from multiples pages in one go
        reusing the same  webscrapping session.
        Argument:
        pages = number of pages to be retrieved, expects a list
        """
        # Ammending default value
        if pages is None:
            pages = [1]
        # Initialize the dictionary to store the results
        page_info = {}
        # Open first page just to check whats the max number of pages
        formatted_url = self.url_search_formatting(1)
        self.driver = Webdriver.open_browser(formatted_url)
        asyncio.run(self.get_response())
        # Get the max number of pages
        page_elements = self.driver.find_elements(By.CLASS_NAME, "NKTSme")
        if not page_elements:
            max_page = len(page_elements)
            # Cap the search to the max number of pages
            if max(pages) > max_page and max_page != 0:
                pages = [i for i in pages if i <= max_page]
        else:
            print("Max page not found")

        for page in pages:
            formatted_url = self.url_search_formatting(page)
            # Reusing the same session
            self.driver.get(formatted_url)

            # Executing and the webscrap and potential exceptions
            try:
                page_source = asyncio.run(self.get_response())
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

            # Perform parse and save info within the class
            result = self.result_parse(page_source)
            page_name = f"page_{page}"
            page_info[page_name] = result

        # Close the webdriver
        self.driver.close()
        return page_info

    def get_page(self, page=1):
        # this is the one that runs when we do search()
        """
        Retrieves a specific page from google.com in
        the news sections into __results.
        Parameter:
        page = number of the page to be retrieved
        """
        formatted_url = self.url_search_formatting(page)
        # Opening the browser
        self.driver = Webdriver.open_browser(formatted_url)
        # Executing and the webscrap and potential exceptions
        try:
            page_source = asyncio.run(self.get_response())
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

        # Close the webdriver
        self.driver.close()

        # Perform parse and save info within the class
        result = self.result_parse(page_source)

        # Save the results into a json file
        if self.save_results_formatted:
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
        return result

    def clear(self):
        self.__texts = []
        self.__links = []
        self.__results = []
