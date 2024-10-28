"""This module contains the webdriver functions  that is used to set
up the Chrome browser with the necessary options"""

import random
from fake_useragent import UserAgent
from selenium_stealth import stealth
from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException,
    SessionNotCreatedException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options


def setup_chrome_proxy() -> None:
    """Set up the Chrome browser"""
    ua = UserAgent()
    user_agent = ua.random
    chrome_options = Options()
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")  # Set verbosity to 1
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


def open_browser(url: str, max_retries=3) -> webdriver:
    """Opens the browser and retries if it fails"""
    for _ in range(max_retries):
        try:
            driver = setup_chrome_proxy()
            driver.get(url)
            return driver  # Return the self.driver if successful
        except (
            WebDriverException,
            SessionNotCreatedException,
            TimeoutException,
        ) as e:
            print(f"Error opening browser: {e}")
