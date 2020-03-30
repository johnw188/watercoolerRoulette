from http import cookies
import time

import pytest

import lambdae.shared as shared
import lambdae.models as models
import lambdae.jwt_tokens as tokens


def test_jwt_encoding():
    to_encode = {"bar": "baz"}
    encoded = tokens.jwt_encode(to_encode)

    decoded = tokens.jwt_decode(encoded)
    assert decoded == to_encode


def test_get_jwt_cookie():
    group_id, user_id = "fakegroup-cookie", "fakegroup-user"
    user = models.UsersModel(group_id, user_id)
    cookie = tokens.get_jwt_cookie(user)
    assert cookie.startswith("token="), cookie

    auth_cookie = cookies.SimpleCookie()
    auth_cookie.load(cookie)
    value = auth_cookie[shared.COOKIE_ATTR_NAME].value

    decoded = tokens.jwt_decode(value)
    assert decoded["group_id"] == group_id
    assert decoded["user_id"] == user_id


def test_require_authorization():
    group_id, user_id = "fakegroup-cookie", "fakegroup-user"
    user = models.UsersModel(group_id, user_id)
    user.username = "usernameeeeee"
    user.teamname = "bar"
    user.avatar = "foo"
    user.url = "baz"
    user.email = "noone@nowhere.com"
    user.delete()

    cookie = tokens.get_jwt_cookie(user)
    fake_aws_events = {"headers": {"Cookie": cookie}}

    # User not saved yet, so should fail to get
    with pytest.raises(shared.AuthException):
        tokens.require_authorization(fake_aws_events)

    user.save()
    tokens.require_authorization(fake_aws_events)


def test_require_authorization_fail1():
    # Non-existant
    fake_aws_events = {"headers": {}}
    with pytest.raises(shared.AuthException):
        tokens.require_authorization(fake_aws_events)


def test_require_authorization_fail2():
    # Malformed
    fake_aws_events = {"headers": {"Cookie": "hella-malformed"}}
    with pytest.raises(shared.AuthException):
        tokens.require_authorization(fake_aws_events)


def test_require_authorization_fail3():
    # invalid
    fake_aws_events = {"headers": {"Cookie": "token=def_invalid"}}
    with pytest.raises(shared.AuthException):
        tokens.require_authorization(fake_aws_events)


def test_require_authorization_expired():
    token = tokens.jwt_issue(group_id="group", user_id="user", t=time.time() - tokens.TOKEN_EXPIRY.total_seconds() - 1)
    fake_aws_events = {"headers": {"Cookie": "token=" + token}}

    with pytest.raises(shared.AuthException) as e:
        tokens.require_authorization(fake_aws_events)
    assert "Token is expired" in str(e)
