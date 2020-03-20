import time
import json
import urllib


CLIENT_ID = "TODO"
CLIENT_SECRET = "TODO"

BASE_URL = "https://slack.com/api/oauth.access"
EXPECTED_REDIRECT = "https://watercooler.express/chat"


def endpoint(event, context):
    # TODO: From John
    # we need to make an /auth endpoint for slack to redirect to,
    # which will basically be a lambda that makes a 
    # GET https://slack.com/api/oauth.access?client_id=CLIENT_ID&client_secret=CLIENT_SECRET&code=XXYYZZ
    # and then responds with a HTTP redirect to whatever we call /video

    # which returns {
    #     "ok": true,
    #     "access_token": "xoxp-1111827399-16111519414-20367011469-5f89a31i07",
    #     "scope": "identity.basic",
    #     "team_id": "T0G9PQBBK"
    # }
    if event["pathParameters"].get("error") is not None:
        return {"statusCode": 403, "body": "Oauth Error Reported by slack"}

    params = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": "TODO3"
    })

    full_url = "{BASE_URL}?{PARAMS}".format(BASE_URL=BASE_URL, params=params)
    # TODO failed auth here.
    try:
        result = json.dumps(urllib.urlopen(full_url).data)
    except urllib.error.URLError:
        return {"statusCode": 403, "body": "Oauth Error !?!?!?"}

    body = {
         "ok": True,
         "access_token": result["access_token"],
         "scope": "identity.basic",
         "team_id": "FooTeamID"
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
