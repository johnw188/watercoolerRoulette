import datetime
import json

import lambdae.shared as shared
import lambdae.models as models

import requests
from http import cookies


AUTH_CB_API = "https://slack.com/api/oauth.access"
AUTH_TEST_API = "https://api.slack.com/api/auth.test"
USER_INFO_API = "https://slack.com/api/users.profile.get"

OAUTH_ID = shared.get_env_var("OAUTH_ID")
OAUTH_SECRET = shared.get_env_var("OAUTH_SECRET")

AFTER_AUTH_REDIRECT = "https://watercooler.express"


COOKIE_ATTR_NAME = "token"


class AuthException(Exception):
    pass


def require_authorization(event):
    """
    Take a lambda http event then:
     - pull out the jwt token
     - validate it
     - look up the user
     - return the user instance

    If any of that fails, throw an auth exception
    """

    try:
        auth_cookie = cookies.SimpleCookie()
        auth_cookie.load(event["headers"]["Cookie"])
        return models.UsersModel.from_token(auth_cookie[COOKIE_ATTR_NAME].value)
    except Exception as e:
        raise AuthException("Failure during auth") from e


@shared.debug_wrapper
def slack_oauth(event, context):
    # This is the redirect behavior when slack fails to auth
    query_params = event["queryStringParameters"]
    if "error" in query_params:
        return shared.json_error_response("Oauth Error Redirect by Slack to here", 403)

    print(query_params)

    # Ask slack if user is legit
    auth_params = {
        "client_id": OAUTH_ID,
        "client_secret": OAUTH_SECRET,
        "code": query_params["code"],
        "redirect_uri": "https://api.watercooler.express/auth"
    }
    auth_result = requests.post(AUTH_CB_API, data=auth_params).json()
    assert auth_result["ok"], auth_result
    token = auth_result["access_token"]

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    # Slack said ok, find out their team identity
    team_result = requests.post(AUTH_TEST_API, headers=headers).json()
    assert team_result["ok"], (token, team_result)

    # Also pull down their avatar
    profile_resp = requests.get(USER_INFO_API, headers=headers).json()
    assert profile_resp["ok"], profile_resp

    # Expected `team_result` format
    # {
    #     "ok": true,
    #     "url": "https://subarachnoid.slack.com/",
    #     "team": "Subarachnoid Workspace",
    #     "user": "grace",
    #     "team_id": "T12345678",
    #     "user_id": "W12345678"
    # }

    user = models.UsersModel(
        user_id=team_result["user_id"],
        group_id=team_result["team_id"],
        slack_username=team_result["user"],
        slack_team=team_result["team"],
        slack_url=team_result["url"],
        slack_avatar=profile_resp["profile"]["image_192"]
    )
    user.save()

    # Figure out how to format/set the cookie
    encoded = user.get_token()
    expiry = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("expires=%a, %d %b %Y %H:%M:%S GMT")
    cookie_parts = (COOKIE_ATTR_NAME + "=" + encoded, "Domain=watercooler.express", expiry)
    cookie = "; ".join(cookie_parts)

    # Shoot the user a cookie with their JWT token, and redirect
    headers = {
        "Location": AFTER_AUTH_REDIRECT,
        "Set-Cookie": cookie
    }
    return {"statusCode": 302, "headers": headers}


@shared.debug_wrapper
def auth_test_users(event, context):
    for x in range(100):
        fake_user = models.UsersModel(
            user_id="fake" + str(x),
            group_id="faketeam",
            slack_username="fakeusername" + str(x),
            slack_team="idk",
            slack_url="www.nowhere.slack.com",
            slack_avatar="http://via.placeholder.com/192x192"
        )
        fake_user.save()

    return {"statusCode": 200, "body": "Fake users created"}
