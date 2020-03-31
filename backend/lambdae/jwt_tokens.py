from http import cookies
import datetime
import time

import jwt

import lambdae.models as models
import lambdae.shared as shared


JWT_ALGO = "HS256"
JWT_SECRET = shared.get_env_var("JWT_SECRET")

# 1 day?
TOKEN_EXPIRY = datetime.timedelta(days=1)


class TokenValidationError(Exception):
    pass


def jwt_issue(*, group_id: str, user_id: str, t: float = None) -> str:
    return jwt_encode({
        "group_id": group_id,
        "user_id": user_id,
        "time": time.time() if t is None else t
    })


def jwt_validate(token: str) -> dict:
    try:
        result = jwt_decode(token)
    except jwt.exceptions.PyJWTError as e:
        raise shared.AuthException(e)

    if result["time"] < time.time() - TOKEN_EXPIRY.total_seconds():
        raise shared.AuthException("Token is expired")

    return result


def jwt_encode(to_encode: dict) -> str:
    """
    Encode a jwt token using our token and algo. Return a string
    """
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO).decode()


def jwt_decode(token: str) -> dict:
    """
    Decode a jwt token using our token and algo. Return the encoded object

    This does not perform any validation/structural checks
    """
    return jwt.decode(token.encode(), JWT_SECRET, algorithms=[JWT_ALGO])


def issue_token(user: models.UsersModel) -> str:
    """
    Given a user instance compute the jwt token for it.
    """
    return jwt_issue(group_id=user.group_id, user_id=user.user_id)


def get_jwt_cookie(user: models.UsersModel = None) -> str:
    """
    Get the string which when used with `set-cookie` in headers to set the cookie
    to "token=blah.blah.blah; etc"
    """
    body = issue_token(user)
    expiry = datetime.datetime.utcnow() + TOKEN_EXPIRY

    return shared.cookie_format(body, expiry)


def require_authorization(event) -> models.UsersModel:
    """
    Take a lambda http event then:
     - pull out the jwt token
     - validate it
     - look up the user
     - return the user instance

    If any of that fails, throw an `AuthException`
    """

    try:
        raw_cookie = event["headers"]["Cookie"]
    except KeyError:
        raise shared.AuthException("No cookie found in headers")

    try:
        auth_cookie = cookies.SimpleCookie()
        auth_cookie.load(raw_cookie)
        cookie_value = auth_cookie[shared.COOKIE_ATTR_NAME].value
    except (cookies.CookieError, KeyError) as e:
        raise shared.AuthException("Malformed cookie") from e

    # Already raises AuthException if failure
    validated = jwt_validate(cookie_value)

    try:
        return models.UsersModel.get(validated["group_id"], validated["user_id"])
    except models.UsersModel.DoesNotExist:
        raise shared.AuthException("No such user.")
