""" this file contains the tests for the googlenews class. 
The test mainly use selenium webscrapping methods and test our connection 
to our catcha API solver."""

import pytest
from selenium.webdriver.common.by import By
import app.cred as cred
from app.google_news_webscrap import GoogleNews
import app.Webdriver as Webdriver


def test_search():
    """Test get Search from Google News"""
    # Start , end date and search
    startdate, enddate, search = "01/01/2020", "31/01/2020", "covid-19"
    # Set up the GoogleNews object
    googlenews = GoogleNews(start=startdate, end=enddate, lang="en", region="US")
    googlenews.set_return_results(True)
    googlenews.set_save_results_formatted(True)
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


# If you see any wierd behavior on the dates on the webscraper may be
# because we're using get_page instead of search. May be worth pocking around
# if the issue continues
def test_page_at():
    """Test get page from Google News"""
    # Start , end date and search
    startdate, enddate, search = "01/03/2020", "31/03/2020", "covid-19"
    # Set up the GoogleNews object
    googlenews = GoogleNews(start=startdate, end=enddate, lang="en", region="US")
    googlenews.set_key(search)
    webscrap_list = []
    for i in range(1, 4):
        webscrap = googlenews.page_at(i)
        print(googlenews.url_search_formatting(i))
        webscrap_list.append(webscrap)
    webscrap_list = [
        item for sublist in webscrap for item in sublist
    ]  # flatten the list

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


def test_news_from_pages():
    """Test get a list of pages reusing the same webscrap object"""
    # Start , end date and search
    startdate, enddate, search = "01/02/2020", "28/01/2020", "covid-19"
    # Set up the GoogleNews object
    googlenews = GoogleNews(start=startdate, end=enddate, lang="en", region="US")
    googlenews.set_key(search)
    webscrap = googlenews.new_from_pages([1, 2, 3])
    assert any(len(content_per_page) > 0 for content_per_page in webscrap.values())


@pytest.mark.asyncio
async def test_solving_catpcha():
    """Test solving captcha. It works on the recaptcha demo passing
    the g-recaptcha script into the browser"""
    googlenews = GoogleNews()
    catpcha_url = "https://google.com/recaptcha/api2/demo"
    googlenews.set_api_key(cred.APIKEY)
    googlenews.driver = Webdriver.open_browser(catpcha_url)
    # The catcha is still not solving, need to solve that
    await googlenews.catcha_solver()
    # Getting a confinrmation message
    pass_sign = googlenews.driver.find_element(By.XPATH, "/html/body/div").text
    googlenews.driver.quit()
    assert "Success" in pass_sign


# if __name__ == "__main__":
#     test_search()
