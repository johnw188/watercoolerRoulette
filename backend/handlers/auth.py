import json
import urllib.request
import urllib.parse
import os

import boto3

CLIENT_ID = os.environ["OAUTH_ID"]
CLIENT_SECRET = os.environ["OAUTH_SECRET"]

AUTH_URL = "https://slack.com/api/oauth.access"
EXPECTED_REDIRECT = "https://watercooler.express/chat"

AUTH_TEST = "https://api.slack.com/methods/auth.test"


# TODO: make me a helper generally
def get_dynamo_table(table_name: str):
    dynamodb = boto3.resource('dynamodb')
    prefix = os.environ["DYNAMODB_TABLE_PREFIX"]
    return dynamodb.Table(prefix + "-" + table_name)


def url_to_json(url: str, params: dict) -> dict:
    if params:
        url = "{url}?{params}".format(url=url, params=urllib.parse.urlencode(params))

    response = urllib.request.urlopen(url)
    assert response.status == 200, response.status

    return json.loads(response.read())


def get_or_create_user(*, user_id: str, team_id: str, slack_username: str, slack_team: str, slack_url: str):
    # Hard overwrite the todo to the database, YOLO
    table = get_dynamo_table("users")
    table.put_item(Item={
        'user_id': user_id,
        'team_id': team_id,
        'slack_username': slack_username,
        'slack_team': slack_team,
        'slack_url': slack_url
    })


def endpoint(event, context):
    # This is the redirect behavior when slack fails to auth
    # if "error" in event["pathParameters"]:
    #     return {"statusCode": 403, "body": "Oauth Error Redirect by Slack to here"}

    # Ask slack if user is legit
    auth_params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": event["pathParameters"]["code"]
    }

    try:
        auth_result = url_to_json(AUTH_URL, auth_params)
    except urllib.error.URLError:
        return {"statusCode": 403, "body": "OAuth seems invald"}

    assert auth_result["ok"], auth_result
    token = auth_result["access_token"]

    # Slack said ok, find out their team identity
    try:
        team_result = url_to_json(AUTH_TEST, {"token": token})
    except urllib.error.URLError:
        return {"statusCode": 403, "body": "OAuth seems invald"}

    assert team_result["ok"], team_result

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
