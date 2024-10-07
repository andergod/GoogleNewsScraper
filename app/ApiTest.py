import os
import time
import asyncio
from MyGoogleNews3 import GoogleNews

from capmonstercloudclient.requests import RecaptchaV2ProxylessRequest
from capmonstercloudclient import ClientOptions, CapMonsterClient

#Globals
WEBPAGE_URL = 'https://www.google.com/recaptcha/api2/demo'
WEBPAGE_KEY = '6LcMmR8UAAAAAGGv5Tg2ZMnJ9y1Zzv1J4X4JY6Yt'

async def get_response(current_url, key, googlenews):
    return  [await googlenews.solve_catpcha_google(current_url, key)    for _ in range(3)]

def test_using_googlenews():
    with open('APIKEY.txt', 'r') as file:
        APIKEY = file.read().strip()

    with open('http_proxies.txt', 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]

    googlenews = GoogleNews()
    googlenews = GoogleNews()
    googlenews = GoogleNews(lang='en', region='US')
    googlenews = GoogleNews(start='02/01/2020',end='02/28/2020')
    googlenews.set_APIKEY(APIKEY)
    googlenews.setproxy(proxies)    
    nums = 3

    # Async test
    async_start = time.time()
    print(googlenews.APIKEY)
    async_responses = asyncio.run(get_response(WEBPAGE_URL, WEBPAGE_KEYB, googlenews))
    print(f'average execution time async {1/((time.time()-async_start)/nums):0.2f} ' \
          f'resp/sec\nsolution: {async_responses[0]}')

async def solve_captcha_sync(num_requests, cap_monster_client, recaptcha2request):
    return [await cap_monster_client.solve_captcha(recaptcha2request) for _ in range(num_requests)]

def test_using_package():
    with open('APIKEY.txt', 'r') as file:
        APIKEY = file.read().strip()
        
    client_options = ClientOptions(api_key=APIKEY)
    cap_monster_client = CapMonsterClient(options=client_options)

    recaptcha2request = RecaptchaV2ProxylessRequest(websiteUrl=WEBPAGE_URL,
                                                    websiteKey=WEBPAGE_KEY)
    
    nums = 3

    # Async test
    sync_start = time.time()
    sync_responses = asyncio.run(solve_captcha_sync(nums, cap_monster_client, recaptcha2request))
    print(f'average execution time sync {1/((time.time()-sync_start)/nums):0.2f} ' \
          f'resp/sec\nsolution: {sync_responses[0]}')

if __name__ == '__main__':
    test_using_package()
    
    
    