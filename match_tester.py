import requests
import concurrent.futures

import backend.lambdae.shared as shared

import jwt

import simplejson


headers= {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "pN=5; s_pers=%20s_vnum%3D1587315935986%2526vn%253D6%7C1587315935986%3B%20s_invisit%3Dtrue%7C1584827519809%3B%20s_nr%3D1584825719810-Repeat%7C1592601719810%3B; s_sess=%20s_cc%3Dtrue%3B%20s_sq%3Dawsamazonprod1%252Cawsamazonallprod1%253D%252526pid%25253Dv1%2525252Fdocumentation%2525252Fapi%2525252Flatest%2525252Freference%2525252Fservices%2525252Fdynamodb%252526pidt%25253D1%252526oid%25253Dhttps%2525253A%2525252F%2525252Fboto3.amazonaws.com%2525252Fv1%2525252Fdocumentation%2525252Fapi%2525252Flatest%2525252Freference%2525252Fservices%2525252Fdynamodb.html%25252523dynamodb%252526ot%25253DA%3B",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
}


def request_match(group_id: str, user_id: str):
    # Forge myself a JWT token
    token = shared.jwt_encode({"group_id": group_id, "user_id": user_id})
    response = requests.post("https://watercooler.express/match_new", json={"token": token, "blob": {}}, headers=headers)

    try:
        print(response.json())
    except simplejson.errors.JSONDecodeError:
        print(response.text)


request_match("pirates", "yourmom")
