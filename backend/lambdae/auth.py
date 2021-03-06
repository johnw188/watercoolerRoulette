import hashlib

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


def make_redirect_for_user(user: models.UsersModel):
    # Shoot the user a cookie with their JWT token, and redirect
    headers = {
        "Location": AFTER_AUTH_REDIRECT,
        "Set-Cookie": tokens.get_jwt_cookie(user)
    }
    return {"statusCode": 302, "headers": headers}

# NB: This call is not unit tested
def _do_slack_oauth(code: str):
    # Ask slack if user is legit
    auth_params = {
        "client_id": OAUTH_ID,
        "client_secret": OAUTH_SECRET,
        "code": code,
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

    # Expected `team_result` format
    # {
    #     "ok": true,
    #     "url": "https://subarachnoid.slack.com/",
    #     "team": "Subarachnoid Workspace",
    #     "user": "grace",
    #     "team_id": "T12345678",
    #     "user_id": "W12345678"
    # }

    # Also pull down their avatar
    profile_resp = requests.get(USER_INFO_API, headers=headers).json()
    assert profile_resp["ok"], profile_resp

    return dict(
        group_id=team_result["team_id"],
        user_id=team_result["user_id"],
        username=team_result["user"],
        teamname=team_result["team"],
        url=team_result["url"],
        avatar=profile_resp["profile"]["image_192"],
        email=profile_resp["profile"]["email"]
    )


@shared.json_request
def slack_oauth(event, context, slack_oauth_call=_do_slack_oauth):
    # This is the redirect behavior when slack fails to auth
    query_params = event["queryStringParameters"]
    if "error" in query_params:
        return shared.json_error_response(message="Oauth Error Redirect by Slack to here", code=403)

    user_kwargs = slack_oauth_call(query_params["code"])
    user = models.UsersModel(**user_kwargs)
    user.save()

    return make_redirect_for_user(user)


def _do_google_oauth(code: str):
    GOOGLE_OAUTH_ID = ""
    GOOGLE_OAUTH_SECRET = ""

    requests.post("https://accounts.google.com/o/oauth2/token")
    auth_params = {
        "client_id": GOOGLE_OAUTH_ID,
        "client_secret": GOOGLE_OAUTH_SECRET,
        "code": code,
        "redirect_uri": "https://api.watercooler.express/auth"
    }

    auth_result = requests.post(AUTH_CB_API, data=auth_params).json()
    token = auth_result["access_token"]

    headers = {"Authorization": "Bearer " + token}
    userinfo = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)

    group_hash = hashlib.sha1()
    group_hash.update(userinfo["hd"].encode())
    group_digest = group_hash.hexdigest()[::3]

    assert userinfo["email_verified"]
    return dict(
        group_id=group_digest,
        user_id=userinfo["sub"],
        username=userinfo["name"],
        teamname=userinfo["hd"],
        url=userinfo["hd"],
        avatar=userinfo["picture"],
        email=userinfo["email"]
    )


@shared.json_request
def google_oauth(event, context, google_oauth_call=_do_google_oauth):
    user_kwargs = google_oauth_call(event["queryStringParameters"]["code"])
    user = models.UsersModel(**user_kwargs)
    user.save()

    return make_redirect_for_user(user)
