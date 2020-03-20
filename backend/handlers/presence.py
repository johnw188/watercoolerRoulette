import time
import json


def endpoint(event, context):
    # TODO: Update presense time here

    response = {
        "statusCode": 200,
        "body": json.dumps({"message": str(time.time())})
    }

    return response
