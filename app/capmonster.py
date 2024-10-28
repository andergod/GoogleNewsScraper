""" This module contains the Capmonster functions used
to reach out the Capmonster API and solve the recaptcha"""

import asyncio
from capmonstercloudclient.requests import RecaptchaV2ProxylessRequest
from capmonstercloudclient import CapMonsterClient, ClientOptions


def set_api_key(api_key: str) -> CapMonsterClient:
    """Set api_key for CapMonster"""
    client = ClientOptions(api_key=api_key)
    cap_monster_client = CapMonsterClient(options=client)
    return cap_monster_client


async def capmonster_catpcha_response(
    website_url: str, captcha_key: str, cap_monster_client: CapMonsterClient
) -> list:
    """Uses the CapMonster API to solve the recaptcha"""
    recaptcha_request = RecaptchaV2ProxylessRequest(
        websiteUrl=website_url, websiteKey=captcha_key
    )
    result = await cap_monster_client.solve_captcha(recaptcha_request)
    return result
