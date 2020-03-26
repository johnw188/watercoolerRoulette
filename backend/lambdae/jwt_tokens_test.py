from http import cookies

import lambdae.models as models
import lambdae.jwt_tokens as tokens


def test_jwt_encoding():
    to_encode = {"bar": "baz"}
    encoded = tokens.jwt_encode(to_encode)

    decoded = tokens.jwt_decode(encoded)
    assert decoded == to_encode


def test_get_jwt_cookie():
    group, user = "fakegroup-cookie", "fakegroup-user"
    user = models.UsersModel(group, user)
    cookie = tokens.get_jwt_cookie(user)
    assert cookie.startswith("token="), cookie

    auth_cookie = cookies.SimpleCookie()
    auth_cookie.load(cookie)
    value = auth_cookie[tokens.COOKIE_ATTR_NAME].value
    
    tokens.jwt_decode(value)
