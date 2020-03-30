import datetime

import lambdae.jwt_tokens as tokens
import lambdae.shared as shared
import lambdae.models as models

import requests

AUTH_CB_API = "https://slack.com/api/oauth.access"
AUTH_TEST_API = "https://api.slack.com/api/auth.test"
USER_INFO_API = "https://slack.com/api/users.profile.get"

OAUTH_ID = shared.get_env_var("OAUTH_ID")
OAUTH_SECRET = shared.get_env_var("OAUTH_SECRET")

AFTER_AUTH_REDIRECT = "https://watercooler.express"


@shared.json_request
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
        username=team_result["user"],
        teamname=team_result["team"],
        url=team_result["url"],
        avatar=profile_resp["profile"]["image_192"],
        email=profile_resp["profile"]["email"]
    )
    user.save()

    # Shoot the user a cookie with their JWT token, and redirect
    headers = {
        "Location": AFTER_AUTH_REDIRECT,
        "Set-Cookie": tokens.get_jwt_cookie(user)
    }
    return {"statusCode": 302, "headers": headers}
