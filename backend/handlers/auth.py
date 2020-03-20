import time
import json
import urllib


BASE_URL = "https://slack.com/api/oauth.access"


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

    params = urllib.parse.urlencode({
        'CLIENT_ID': "TODO1",
        'client_secret': "TODO2",
        'code': "TODO3"
    })

    full_url = "{BASE_URL}?{PARAMS}".format(BASE_URL=BASE_URL, params=params)
    # TODO failed auth here.
    urllib.urlopen(full_url)

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
