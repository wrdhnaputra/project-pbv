import requests

API_KEY = "ef09f81785160d1da0ce43fe51ae691a"

BASE_URL = "https://api.themoviedb.org/3"

def search_drakor(judul):
    url = f"{BASE_URL}/search/tv"
    params = {
        "api_key": API_KEY,
        "query": judul,
        "language": "en-US"
    }
    response = requests.get(url, params=params)
    return response.json()

def get_drakor_detail(tv_id):
    url = f"{BASE_URL}/tv/{tv_id}"
    params = {
        "api_key": API_KEY,
        "language": "ko-KR"
    }
    response = requests.get(url, params=params)
    return response.json()

def gettv_detail(tv_id):
    url = f"{BASE_URL}/tv/{tv_id}"
    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }
    return requests.get(url, params=params).json()