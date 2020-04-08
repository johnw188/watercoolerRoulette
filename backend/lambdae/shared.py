import datetime
import functools
import os
import json
import traceback


COOKIE_ATTR_NAME = "token"


def cookie_format(body: str, expiry: datetime.datetime):
    cookie_parts = (
        COOKIE_ATTR_NAME + "=" + body,
        "Domain=.watercooler.express",
        expiry.strftime("expires=%a, %d %b %Y %H:%M:%S GMT"),
        "SameSite=None",
        "Secure")
    return "; ".join(cookie_parts)


def get_expired_cookie() -> str:
    return cookie_format("", datetime.datetime(1970, 1, 1))


def get_env_var(name: str) -> str:
    value = os.environ.get(name, None)
    assert value is not None, "Expected the environment variable \"{}\" to be set.".format(name)
    return value


def _fmt_exception(e: Exception) -> str:
    return str(e) + "\n" + traceback.format_exc()


class AuthException(Exception):
    pass


def get_header(headers: dict, keyname: str, default: str) -> str:
    """
    This function deals with the inconsistent casing of http headers :(

    A fine example of why we can't have nice things
    """
    for k, v in headers.items():
        if k.lower() == keyname.lower():
            return v
    return default


def json_request(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        event, context = args
        print("Request to " + str(f.__name__) + ":\n" + json.dumps(event, indent=2))
        request_headers = event.get("headers", {})

        try:
            response = f(*args, **kwargs)
        except AuthException:
            response = {
                "statusCode": 401,
                "headers": {"Set-Cookie": get_expired_cookie()},
                "body": json.dumps({"ok": False, "message": "User is not logged in"})}
        except Exception as e:
            print("Unhandled Exception!!!")
            print(_fmt_exception(e))
            response = {
                "statusCode": 500,
                "body": json.dumps({
                    "ok": False,
                    # TODO DISABLE/Remove in prod? Idk
                    "message": _fmt_exception(e)
                })}

        # Remember to encode your bodies kids
        if "body" in response:
            assert type(response["body"]) == str

        # Patch any headers added with the appropriate stuffs
        headers = response.get("headers", {})
        headers.update({
            # Look at this filthy hack
            "Access-Control-Allow-Origin": get_header(request_headers, "Origin", "*"),
            "Access-Control-Allow-Credentials": True,
            "Content-Type": "application/json"
        })
        response["headers"] = headers

        print("Response:\n" + json.dumps(response, indent=2))
        return response

    return wrapper


def json_response(j: dict, code: int, ok: bool):
    to_send = {"ok": ok}
    to_send.update(j)
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(to_send)}


def json_success_response(j: dict) -> dict:
    return json_response(j, 200, True)


def json_error_response(*, message: str, code: int, j: dict = {}) -> dict:
    to_send = {"message": message}
    to_send.update(j)
    return json_response(to_send, code, False)


def json_response_from_exception(e: Exception, code: int = 500):
    json_error_response(_fmt_exception(e), code)
