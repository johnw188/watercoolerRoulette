import functools
import urllib.request
import urllib.parse
import os
import traceback

import lambdae.shared as shared
import lambdae.models as models

import requests
import boto3

EXPECTED_REDIRECT = "https://watercooler.express/chat"

AUTH_CB_API = "https://slack.com/api/oauth.access"
AUTH_TEST_API = "https://api.slack.com/api/auth.test"
USER_INFO_API = "https://slack.com/api/users.profile.get"


@shared.debug_wrapper
def endpoint(event, context):
    # This is the redirect behavior when slack fails to auth
    query_params = event["queryStringParameters"]
    if "error" in query_params:
        return {
            "statusCode": 403,
            "body": "Oauth Error Redirect by Slack to here"}

    # Ask slack if user is legit
    auth_params = {
        "client_id": os.environ["OAUTH_ID"],
        "client_secret": os.environ["OAUTH_SECRET"],
        "code": query_params["code"],
        "redirect_uri": "https://watercooler.express/auth"
    }

    try:
        auth_result = requests.post(AUTH_CB_API, data=auth_params).json()
    except urllib.error.URLError:
        return {"statusCode": 403, "body": "OAuth seems invald"}

    assert auth_result["ok"], auth_result
    token = auth_result["access_token"]

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    # Slack said ok, find out their team identity
    try:
        team_result = requests.post(AUTH_TEST_API, headers=headers).json()
    except urllib.error.URLError:
        return {"statusCode": 403, "body": "Unable to get identity!"}

    assert team_result["ok"], (token, team_result)

    # Also pull down their avatar
    try:
        profile_resp = requests.get(USER_INFO_API, headers=headers).json()
    except urllib.error.URLError:
        return {"statusCode": 403, "body": "Unable to get avatar!"}

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
        team_id=team_result["team_id"],
        slack_username=team_result["user"],
        slack_team=team_result["team"],
        slack_url=team_result["url"],
        slack_avatar=profile_resp["profile"]["image_192"]
    )
    user.save()

    # Shoot the user a cookie with their JWT token, and redirect    
    response_headers = {"Location": "https://watercooler.express/win"}
    response_headers.update(user.get_jwt_token_header())
    return {"statusCode": 302, "headers": response_headers}


@shared.debug_wrapper
def win(event, context):
    return {"statusCode": 200, "body": "You win at oauth."}
