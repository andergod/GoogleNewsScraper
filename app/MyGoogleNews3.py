### MODULES
#Using my own proxy given that proxy rotation is not working
import re
import urllib.request
import dateparser, copy
from bs4 import BeautifulSoup as Soup, ResultSet
from dateutil.parser import parse
import random
import datetime
from dateutil.relativedelta import relativedelta
import logging
import sys
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
import random
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

### METHODS

def lexical_date_parser(date_to_check):
    if date_to_check=='':
        return ('',None)
    datetime_tmp=None
    date_tmp=copy.copy(date_to_check)
    try:
        date_tmp = date_tmp[date_tmp.rfind('..')+2:]
        datetime_tmp=dateparser.parse(date_tmp)
    except:
        date_tmp = None
        datetime_tmp = None

    if datetime_tmp==None:
        date_tmp=date_to_check
    else:
        datetime_tmp=datetime_tmp.replace(tzinfo=None)

    if date_tmp[0]==' ':
        date_tmp=date_tmp[1:]
    return date_tmp,datetime_tmp


def define_date(date):
    months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Sept':9,'Oct':10,'Nov':11,'Dec':12, '01':1, '02':2, '03':3, '04':4, '05':5, '06':6, '07':7, '08':8, '09':9, '10':10, '11':11, '12':12}
    try:
        if ' ago' in date.lower():
            q = int(date.split()[-3])
            if 'minutes' in date.lower() or 'mins' in date.lower():
                return datetime.datetime.now() + relativedelta(minutes=-q)
            elif 'hour' in date.lower():
                return datetime.datetime.now() + relativedelta(hours=-q)
            elif 'day' in date.lower():
                return datetime.datetime.now() + relativedelta(days=-q)
            elif 'week' in date.lower():
                return datetime.datetime.now() + relativedelta(days=-7*q)
            elif 'month' in date.lower():
                return datetime.datetime.now() + relativedelta(months=-q)
        elif 'yesterday' in date.lower():
            return datetime.datetime.now() + relativedelta(days=-1)
        else:
            date_list = date.replace('/',' ').split(' ')
            if len(date_list) == 2:
                date_list.append(datetime.datetime.now().year)
            elif len(date_list) == 3:
                if date_list[0] == '':
                    date_list[0] = '1'
            return datetime.datetime(day=int(date_list[0]), month=months[date_list[1]], year=int(date_list[2]))
    except:
        return float('nan')


### CLASSEs

class GoogleNews:

    def __init__(self,lang="en",period="",start="",end="",encode="utf-8",region=None):
        self.__texts = []
        self.__links = []
        self.__results = []
        self.__totalcount = 0
        self.proxy = []
        self.user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'
        self.__lang = lang
        if region:
            self.accept_language= lang + '-' + region + ',' + lang + ';q=0.9'
            self.headers = {'User-Agent': self.user_agent, 'Accept-Language': self.accept_language}
        else:
            self.headers = {'User-Agent': self.user_agent}
        self.__period = period
        self.__start = start
        self.__end = end
        self.__encode = encode
        self.__exception = False
        self.__version = '1.6.14'
        self.chrome_options = Options()
        self.chrome_options.add_argument("--enable-logging")
        self.chrome_options.add_argument("--v=1")  # Set verbosity to 1
        self.cookies = {}
        self.driver = None
        self.APIKEY=None
        self.cap_monster_client=None
        self.ClientOptions=None
        self.recaptcha_request=None

    def getVersion(self):
        return self.__version
    
    def enableException(self, enable=True):
        self.__exception = enable

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

    def search(self, key):
        """
        Searches for a term in google.com in the news section and retrieves the first page into __results.
        Parameters:
        key = the search term
        """
        self.__key = key
        if self.__encode != "":
            self.__key = urllib.request.quote(self.__key.encode(self.__encode))
        self.get_page()
        
    def setproxy(self, proxy):
        self.proxy = proxy
        
    def set_cookie(self, cookie):
        self.cookies = cookie
        
    def check_proxy(self, proxy):
        types = ['http', 'https', 'socks4', 'socks5']
        url = 'http://httpbin.org/ip'
        for type in types:
            try:
                proxies = { 'http': f'{type}://{proxy}', 'https': f'{type}://{proxy}' }
                response = requests.get(url, proxies=proxies, timeout=5)
                if response.status_code == 200:
                    return type
            except requests.exceptions.RequestException as e:
                continue
        return None
    
    def set_APIKEY(self, APIKEY):
        self.APIKEY = APIKEY
        self.ClientOptions=ClientOptions(api_key=APIKEY)
        self.cap_monster_client=CapMonsterClient(options=ClientOptions)
        
    async def solve_catpcha_google(self, website_url, CaptchaKey):
        self.recaptcha_request = RecaptchaV2ProxylessRequest(websiteUrl=website_url, websiteKey=CaptchaKey)
        result = await self.cap_monster_client.solve_captcha(self.recaptcha_request)
        return result 
        #return result['gRecaptchaResponse']      
            
    def setup_chrome_proxy(self, chrome_options, proxy, cookie):
        #chrome_options.add_argument(f'--proxy-server={proxy}') 
        ua = UserAgent()
        user_agent = ua.random
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        
        # Initialize the WebDriver with the specified options
        driver = webdriver.Chrome(options=chrome_options)
        
        # Set random or specific monitor sizes
        possible_sizes = [(1920, 1080), (1366, 768), (1280, 720), (1440, 900), (1536, 864)]
        chosen_size = random.choice(possible_sizes)
        driver.set_window_size(*chosen_size)
        
        # Navigate to a page that accepts the cookie
        #driver.get('https://www.google.com')
        
        # Inject the cookie into the browser
        # Stop passing the cookie for now
        # if 'expiry' in cookie:
        #     del cookie['expiry']  # Selenium might not accept expiry, depends on version
        # driver.add_cookie(cookie)

        # Refresh or navigate again to make cookie take effect
        #driver.get('https://www.google.com')
        # Use selenium-stealth to avoid being detected as a bot
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        return driver
    
    def try_proxies(self, proxies, url, max_retries=10):
        for attempt in range(max_retries):
            proxy=  random.choice(proxies)
            try:
                self.driver = self.setup_chrome_proxy(self.chrome_options, proxy, self.cookies)
                self.driver.get(url)
                print(f"Connected using proxy: {proxy}")
                return self.driver  # Return the self.driver if successful
            except Exception as e:
                print(f"Failed to connect using proxy: {proxy}, Attempt: {attempt + 1}, Error: {e}")
                self.driver.quit()
                sleep(2)  # Wait before retrying
        print("Failed to connect using all provided proxies.")
        return None
        
    async def build_response(self):
        #Getting the url and trying a proxy
        full_url = self.url.replace("search?", "search?hl=" + self.__lang + "&gl=" + self.__lang + "&")
        self.driver = self.try_proxies(self.proxy, full_url)
        
        #Check if you have sent to a "Before you continue to Google" page
        current_url = self.driver.current_url
        if "consent" in current_url:
            agreed_button=WebDriverWait(self.driver,30).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Accept all"]')))
            agreed_button.click()
            sleep(2)
        
        current_url = self.driver.current_url
        #In case we have a recaptcha
        if "sorry" in current_url:
            sleep(5)
            key=self.driver.find_element(By.XPATH, '//*[@id="recaptcha"]').get_attribute('data-sitekey')
            #recaptchaDataSValue=self.driver.find_element(By.XPATH, '//*[@id="recaptcha"]').get_attribute('data-s') if needed
            recaptcha_response = await self.solve_catpcha_google(current_url, key) #his is the error
            print('recatcha respone: {lol}'.format(recaptcha_response))
            print('data-sitekey: {lol}'.format(key))
            print('url: {lol}'.format(current_url))
            self.driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{recaptcha_response}";')
            sleep(2)
        
        # After the page has loaded, extract the page source
        page_source = self.driver.page_source
        self.driver.close()
        # Parse the page source with BeautifulSoup
        content = Soup(page_source, "html.parser")
        
        # Perform analysis or extraction from the page
        results = self.initial_html_parse(content)
        return results
        
    def initial_html_parse(self, content):
        try:
            stats = content.find_all("div", id="result-stats")
            if stats:
                stats_text = stats[0].text
                match = re.search(r'[\d,]+', stats_text)
                self.__totalcount = int(match.group().replace(',', '')) if match else None
            else:
                self.__totalcount = None
                logging.debug('Total count is not available when sort by date')
            
            results = content.find_all("a", attrs={'data-ved': True})
            return results
        except Exception as e:
            logging.error(f"Failed to parse content: {e}")
            return None
        
    def remove_after_last_fullstop(self, s):
        # Find the last occurrence of the full stop
        last_period_index = s.rfind('.')
        # Slice the string up to the last full stop
        return s[:last_period_index+1] if last_period_index != -1 else s
    
    def page_at(self, page=1):
        """
        Retrieves a specific page from google.com in the news sections into __results.
        Parameter:
        page = number of the page to be retrieved
        """
        results = []
        try:
            if self.__start != "" and self.__end != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{},sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,self.__start,self.__end,(10 * (page - 1)))
            elif self.__period != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},qdr:{},,sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,self.__period,(10 * (page - 1))) 
            else:
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,(10 * (page - 1))) 
        except AttributeError:
            raise AttributeError("You need to run a search() before using get_page().")
        try:
            result = asyncio.run(self.build_response())
            for item in result:
                try:
                    tmp_text = item.find("h3").text.replace("\n","")
                except Exception:
                    tmp_text = ''
                try:
                    tmp_link = item.get("href").replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
                except Exception:
                    tmp_link = ''
                try:
                    tmp_media = item.find('div').find('div').find('div').find_next_sibling('div').text
                except Exception:
                    tmp_media = ''
                try:
                    tmp_date = item.find('div').find_next_sibling('div').find('span').text
                    tmp_date,tmp_datetime=lexical_date_parser(tmp_date)
                except Exception:
                    tmp_date = ''
                    tmp_datetime=None
                try:
                    tmp_desc = self.remove_after_last_fullstop(item.find('div').find_next_sibling('div').find('div').find_next_sibling('div').find('div').find('div').find('div').text).replace('\n','')
                except Exception:
                    tmp_desc = ''
                try:
                    tmp_img = item.find("img").get("src")
                except Exception:
                    tmp_img = ''
                self.__texts.append(tmp_text)
                self.__links.append(tmp_link)
                results.append({'title': tmp_text, 'media': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date),'desc': tmp_desc, 'link': tmp_link,'img': tmp_img})
        except Exception as e_parser:
            print(e_parser)
            if self.__exception:
                raise Exception(e_parser)
            else:
                pass
        return results

    def get_page(self, page=1):
        #this is the one that runs when we do search()
        """
        Retrieves a specific page from google.com in the news sections into __results.
        Parameter:
        page = number of the page to be retrieved 
        """
        try:
            if self.__start != "" and self.__end != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{},sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,self.__start,self.__end,(10 * (page - 1)))
            elif self.__period != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},qdr:{},,sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,self.__period,(10 * (page - 1))) 
            else:
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,(10 * (page - 1))) 
        except AttributeError:
            raise AttributeError("You need to run a search() before using get_page().")
        
        try:
            result = asyncio.run(self.build_response())
            for item in result:
                try:
                    tmp_text = item.find("h3").text.replace("\n","")
                except Exception:
                    tmp_text = ''
                try:
                    tmp_link = item.get("href").replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
                except Exception:
                    tmp_link = ''
                try:
                    tmp_media = item.find('div').find('div').find('div').find_next_sibling('div').text
                except Exception:
                    tmp_media = ''
                try:
                    tmp_date = item.find('div').find_next_sibling('div').find('span').text
                    tmp_date,tmp_datetime=lexical_date_parser(tmp_date)
                except Exception:
                    tmp_date = ''
                    tmp_datetime=None
                try:
                    tmp_desc = self.remove_after_last_fullstop(item.find('div').find_next_sibling('div').find('div').find_next_sibling('div').find('div').find('div').find('div').text).replace('\n','')
                except Exception:
                    tmp_desc = ''
                try:
                    tmp_img = item.find("img").get("src")
                except Exception:
                    tmp_img = ''
                self.__texts.append(tmp_text)
                self.__links.append(tmp_link)
                self.__results.append({'title': tmp_text, 'media': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date),'desc': tmp_desc, 'link': tmp_link,'img': tmp_img})
        except Exception as e_parser:
            print(e_parser)
            if self.__exception:
                raise Exception(e_parser)
            else:
                pass

    def getpage(self, page=1):
        """Don't remove this, will affect old version user when upgrade"""
        self.get_page(page)

    def get_news(self, key="",deamplify=False):
        if key != '':
            if self.__period != "":
                key += f" when:{self.__period}"
        else:
            if self.__period != "":
                key += f"when:{self.__period}"
        key = urllib.request.quote(key.encode(self.__encode))
        start = f'{self.__start[-4:]}-{self.__start[:2]}-{self.__start[3:5]}'
        end = f'{self.__end[-4:]}-{self.__end[:2]}-{self.__end[3:5]}'
        
        if self.__start == '' or self.__end == '':
            self.url = 'https://news.google.com/search?q={}&hl={}'.format(
                key, self.__period, self.__lang.lower())
        else:
            self.url = 'https://news.google.com/search?q={}+before:{}+after:{}&hl={}'.format(
                key, end, start, self.__lang.lower())

        try:
            self.req = urllib.request.Request(self.url, headers=self.headers)
            self.response = urllib.request.urlopen(self.req)
            self.page = self.response.read()
            self.content = Soup(self.page, "html.parser")
            articles = self.content.select('article')
            for article in articles:
                try:
                    # title
                    try:
                        title=article.findAll('div')[2].findAll('a')[0].text
                    except:
                        title=None
                    # description
                    try:
                        desc=None
                    except:
                        desc=None
                    # date
                    try:
                        date = article.find("time").text
                        # date,datetime_tmp = lexial_date_parser(date)
                    except:
                        date = None
                    # datetime
                    try:
                        datetime_chars=article.find('time').get('datetime')
                        datetime_obj = parse(datetime_chars).replace(tzinfo=None)
                    except:
                        datetime_obj=None
                    # link
                    if deamplify:
                        try:
                            link = 'news.google.com/' + article.find('div').find("a").get("href")[2:]
                        except Exception as deamp_e:
                            print(deamp_e)
                            link = article.find("article").get("jslog").split('2:')[1].split(';')[0]
                    else:
                        try:
                            link = 'news.google.com/' + article.find('div').find("a").get("href")[2:]
                        except Exception as deamp_e:
                            print(deamp_e)
                            link = None
                    self.__texts.append(title)
                    self.__links.append(link)
                    if link.startswith('https://www.youtube.com/watch?v='):
                        desc = 'video'
                    # image
                    try:
                        img = 'news.google.com'+article.find("figure").find("img").get("src")
                    except:
                        img = None
                    # site
                    try:
                        site=article.find("time").parent.find("a").text
                    except:
                        site=None
                    try:
                        media=article.find("div").findAll("div")[1].find("div").find("div").find("div").text
                    except:
                        media=None
                    # reporter
                    try:
                        reporter = article.findAll('span')[2].text
                    except:
                        reporter = None
                    # collection
                    self.__results.append({'title':title,
                                           'desc':desc,
                                           'date':date,
                                           'datetime':define_date(date),
                                           'link':link,
                                           'img':img,
                                           'media':media,
                                           'site':site,
                                           'reporter':reporter})
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

    def result(self,sort=False):
        """Don't remove this, will affect old version user when upgrade"""
        return self.results(sort)

    def results(self,sort=False):
        """Returns the __results.
        New feature: include datatime and sort the articles in decreasing order"""
        results=self.__results
        if sort:
            try:
                results.sort(key = lambda x:x['datetime'],reverse=True)
            except Exception as e_sort:
                print(e_sort)
                if self.__exception:
                    raise Exception(e_sort)
                else:
                    pass
                results=self.__results
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