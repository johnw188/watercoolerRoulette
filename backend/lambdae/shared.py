import functools
import os
import json
import traceback


def get_env_var(name: str) -> str:
    value = os.environ.get(name, None)
    assert value is not None, "Expected the environment variable \"{}\" to be set."
    return value


def _fmt_exception(e: Exception) -> str:
    return str(e) + "\n" + traceback.format_exc()


# TODO DISABLE/Remove in prod? Idk
def debug_wrapper(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        event, context = args
        print("Request to " + str(f.__name__) + ":\n" + json.dumps(event, indent=2))

        try:
            response = f(*args, **kwargs)
        except Exception as e:
            response = {
                "statusCode": 500,
                "body": json.dumps({
                    "ok": False,
                    "message": _fmt_exception(e)
                })}

        headers = response.get("headers", {})
        headers.update({
            # Look at this filthy hack
            "Access-Control-Allow-Origin": event["headers"].get("Origin", event["headers"].get("origin", "*")),
            "Access-Control-Allow-Credentials": True
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
