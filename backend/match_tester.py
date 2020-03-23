import json
import requests
import simplejson

import lambdae.shared as shared


headers = {
    "Host": "watercooler.express",
    "Content-Type": "application/json",
    "User-Agent": "curl/7.58.0"
}


def request_match(group_id: str, user_id: str):
    # Forge myself a JWT token
    token = shared.jwt_encode({"group_id": group_id, "user_id": user_id})
    response = requests.post(
        "http://watercooler.express/match",
        json={"token": token, "blob": {}},
        headers=headers)

    print("RESPONSE:")
    try:
        print(response.json())
    except simplejson.errors.JSONDecodeError:
        print(response.text)


request_match("faketeam", "fake38")
