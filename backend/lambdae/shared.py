import functools
import os
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


# TODO DISABLE/Remove in prod? Idk
def debug_wrapper(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return {
                "statusCode": 500,
                "body": str(e) + "\n" + traceback.format_exc()}
    return wrapper
