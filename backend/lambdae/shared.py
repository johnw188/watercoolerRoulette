import datetime

import jwt


def get_token_for_user():
    exp_dt = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    exipry = exp_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return {"Set-Cookie": "foo=bar; Domain=watercooler.express; expires"}
