import json


BASE_URL = "https://slack.com/api/oauth.access"


def endpoint(event, context):


    # Add self to the available matches table
try:
    table.put_item(
        Item={
            'foo':1,
            'bar':2,
        },
        ConditionExpression='attribute_not_exists(foo) AND attribute_not_exists(bar)'
    )
except botocore.exceptions.ClientError as e:
    # Ignore the ConditionalCheckFailedException
    # Attempt to acquire matchmaker token
    # If acquired
    #    make matches
    #    Release token
    #    poll for match result
    # else
    #    for each 1/2 second:
    #        poll for match result
    #
    # if matched
    #     return shared room id, and delete match record for self
    # else 
    #     return suggested timeout?



    # TODO: Check auth
    body = "You are awesome."

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
