import urllib.request
import urllib.parse
import os
import traceback

import requests
import boto3

TABLE_PREFIX = os.environ["DYNAMO_TABLE_PREFIX"]
CLIENT_ID = os.environ["OAUTH_ID"]
CLIENT_SECRET = os.environ["OAUTH_SECRET"]

AUTH_CB = "https://slack.com/api/oauth.access"
EXPECTED_REDIRECT = "https://watercooler.express/chat"

AUTH_TEST = "https://api.slack.com/api/auth.test"


# TODO: make me a helper generally
def get_dynamo_table(table_name: str):
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(TABLE_PREFIX + "-" + table_name)


def get_or_create_user(
        *,
        user_id: str,
        team_id: str,
        slack_username: str,
        slack_team: str,
        slack_url: str):
    # Hard overwrite, YOLO
    table = get_dynamo_table(USERS_TABLE)
    table.put_item(Item={
        'user_id': user_id,
        'team_id': team_id,
        'slack_username': slack_username,
        'slack_team': slack_team,
        'slack_url': slack_url
    })


def endpoint(event, context):
    try:
        return _endpoint(event, context)
    except Exception as e:
        return {
            "statusCode": 200,
            "body": str(e) + "\n" + traceback.format_exc()}


def _endpoint(event, context):
    # This is the redirect behavior when slack fails to auth
    query_params = event["queryStringParameters"]
    if "error" in query_params:
        return {
            "statusCode": 403,
            "body": "Oauth Error Redirect by Slack to here"}

    # Ask slack if user is legit
    auth_params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": query_params["code"],
        "redirect_uri": "https://watercooler.express/auth"
    }

    try:
        auth_result = requests.post(AUTH_CB, data=auth_params).json()
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
        res = requests.post(AUTH_TEST, headers=headers)
    except urllib.error.URLError:
        return {"statusCode": 403, "body": "OAuth seems invald"}

    team_result = res.json()
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

    get_or_create_user(
        user_id=team_result["user_id"],
        team_id=team_result["team_id"],
        slack_username=team_result["user"],
        slack_team=team_result["team"],
        slack_url=team_result["url"]
    )
    # TODO: Issue JWT token here
    return {
        "statusCode": 302,
        "headers": {"Location": "https://watercooler.express/chat"}
    }
