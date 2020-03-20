import time
import json


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

    body = {
         "ok": True,
         "access_token": "fooplaceholder",
         "scope": "identity.basic",
         "team_id": "FooTeamID"
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
