import functools
import os
import json
import traceback

import jwt


def get_env_var(name: str) -> str:
    value = os.environ.get(name, None) 
    assert value is not None, "Expected the environment variable \"{}\" to be set."
    return value


JWT_ALGO = "HS256"
JWT_SECRET = get_env_var("JWT_SECRET")


def jwt_encode(to_encode: dict) -> str:
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)


def jwt_decode(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])


def _fmt_exception(e: Exception) -> str:
    return str(e) + "\n" + traceback.format_exc()


# TODO DISABLE/Remove in prod? Idk
def debug_wrapper(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return {
                "statusCode": 500,
                "body": _fmt_exception(e)}
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