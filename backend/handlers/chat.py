import json


BASE_URL = "https://slack.com/api/oauth.access"


def endpoint(event, context):
    # TODO: Check auth
    body = "You are awesome."

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
