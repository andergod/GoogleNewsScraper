# from app.MyGoogleNews3 import *
from app.MyGoogleNews3 import GoogleNews


def test_get_news():
    """Test get Search from Google News"""
    # Start , end date and search
    startdate, enddate, search = "2021-01-01", "2021-05-02", "covid-19"
    # Set up the GoogleNews object
    googlenews = GoogleNews(start=startdate, end=enddate, lang="en", region="US")
    googlenews.search(search)
    return googlenews.getResults()


if __name__ == "__main__":
    test_get_news()
