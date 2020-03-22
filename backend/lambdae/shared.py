import functools
import traceback


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
