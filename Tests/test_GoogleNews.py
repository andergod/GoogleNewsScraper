# from app.MyGoogleNews3 import *
import asyncio
import app.cred as cred
import pytest

from selenium.webdriver.common.by import By
from app.MyGoogleNews3 import GoogleNews


def test_search():
    """Test get Search from Google News"""
    # Start , end date and search
    startdate, enddate, search = "02/01/2020", "02/28/2020", "covid-19"
    # Set up the GoogleNews object
    googlenews = GoogleNews(start=startdate, end=enddate, lang="en", region="US")
    googlenews.set_return_results(True)
    webscrap = googlenews.search(search)
    # Assert that there are at least 2 result with non-empty title and description
    non_empty_count = 0

    for result in webscrap:
        # Check if both title and desc are non-empty
        if result["title"].strip() and result["desc"].strip():
            non_empty_count += 1

    # Assert that at least 2 results have non-empty title and description
    assert (
        non_empty_count >= 2
    ), "At least 2 results should have non-empty title and description"


def test_get_page():
    """Test get page from Google News"""
    # Start , end date and search
    startdate, enddate, search = "02/01/2020", "02/28/2020", "covid-19"
    # Set up the GoogleNews object
    googlenews = GoogleNews(start=startdate, end=enddate, lang="en", region="US")
    googlenews.set_key(search)
    webscrap = [googlenews.page_at(i) for i in range(1, 3)]
    webscrap = [item for sublist in webscrap for item in sublist]  # flatten the list

    # Assert that there are at least 8 result with non-empty title and description
    non_empty_count = 0
    for result in webscrap:
        # Check if both title and desc are non-empty
        if result["title"].strip() and result["desc"].strip():
            non_empty_count += 1

    # Assert that at least 8 results have non-empty title and description
    assert (
        non_empty_count >= 8
    ), "At least 8 results should have non-empty title and description"


@pytest.mark.asyncio
async def test_solving_catpcha():
    """Test solving captcha"""
    googlenews = GoogleNews()
    catpcha_url = "https://google.com/recaptcha/api2/demo"
    googlenews.set_api_key(cred.APIKEY)
    googlenews.open_browser(" ", catpcha_url, max_retries=1)
    # The catcha is still not solving, need to solve that
    await googlenews.catcha_solver()
    # Getting a confinrmation message
    pass_sign = googlenews.driver.find_element(By.XPATH, "/html/body/div").text
    googlenews.driver.quit()
    assert "Success" in pass_sign


# if __name__ == "__main__":
#     asyncio.run(test_solving_catpcha())


# def test_url_formatting():
#     """Test url formatting old version vs new version"""
#     # Start , end date and search
#     startdate, enddate, search = "02/01/2020", "02/28/2020", "covid-19"
#     # Set up the GoogleNews object
#     googlenews = GoogleNews(start=startdate, end=enddate, lang="en", region="US")
#     googlenews.set_key(search)
#     # Assert that the url is formatted correctly
#     print(f"Old weorking URL: \n{googlenews.url_search_old(1)}")
#     print(f"New not working URL: \n{googlenews.url_search_formatting(1, search)}")
