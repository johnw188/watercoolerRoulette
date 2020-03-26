from http import cookies
import datetime
import time

import jwt

import lambdae.models as models
import lambdae.shared as shared


JWT_ALGO = "HS256"
JWT_SECRET = shared.get_env_var("JWT_SECRET")
COOKIE_ATTR_NAME = "token"

# 1 day?
TOKEN_EXPIRY = datetime.timedelta(days=1)


class TokenValidationError(Exception):
    pass


def jwt_issue(*, group_id: str, user_id: str) -> str:
    return jwt_encode({
        "group_id": group_id,
        "user_id": user_id,
        "time": time.time()
    })


def jwt_validate(token: str) -> dict:
    try:
        result = jwt_decode(token)
    except jwt.exceptions.PyJWTError as e:
        raise TokenValidationError(e)

    if result["time"] < time.time() - TOKEN_EXPIRY.total_seconds():
        raise TokenValidationError("Token is expired")

    return result


def jwt_encode(to_encode: dict) -> str:
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO).decode()


def jwt_decode(token: str) -> dict:
    return jwt.decode(token.encode(), JWT_SECRET, algorithms=[JWT_ALGO])


class AuthException(Exception):
    pass


def issue_token(user: models.UsersModel) -> str:
    """
    Given a user instance compute the jwt token for it.
    """
    return jwt_issue(group_id=user.group_id, user_id=user.user_id)


def get_jwt_cookie(user: models.UsersModel) -> str:
    """
    Get the string which when used with `set-cookie` in headers to set the cookie
    to "token=blah.blah.blah; etc"
    """
    encoded = issue_token(user)
    expiry = (datetime.datetime.utcnow() + TOKEN_EXPIRY).strftime("expires=%a, %d %b %Y %H:%M:%S GMT")
    cookie_parts = (COOKIE_ATTR_NAME + "=" + encoded, "Domain=watercooler.express", expiry)
    return "; ".join(cookie_parts)


def require_authorization(event) -> models.UsersModel:
    """
    Take a lambda http event then:
     - pull out the jwt token
     - validate it
     - look up the user
     - return the user instance

    If any of that fails, throw an auth exception
    """

    try:
        auth_cookie = cookies.SimpleCookie()
        auth_cookie.load(event["headers"]["Cookie"])
        validated = jwt_validate(auth_cookie[COOKIE_ATTR_NAME].value)
        return models.UsersModel.get(validated["group_id"], validated["user_id"])
    except Exception as e:
        raise AuthException("Failure during auth") from e
