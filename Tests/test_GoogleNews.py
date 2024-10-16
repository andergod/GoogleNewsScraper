# from app.MyGoogleNews3 import *
from app.MyGoogleNews3 import GoogleNews


def test_search():
    """Test get Search from Google News"""
    # Start , end date and search
    startdate, enddate, search = "02/01/2020", "02/28/2020", "covid-19"
    # Set up the GoogleNews object
    googlenews = GoogleNews(start=startdate, end=enddate, lang="en", region="US")
    googlenews.set_save_results_formatted(True)
    googlenews.set_save_raw_html(True)
    googlenews.search(search)


if __name__ == "__main__":
    test_search()
    # with open("saved_page.html", "w") as f:
    #    f.write(response.text)  # Save the page
