import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"


def get_live_matches():
    url = f"{BASE_URL}/fixtures?live=all"

    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    return response.json()


def get_today_fixtures():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/fixtures?date={today}"

    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    return response.json()