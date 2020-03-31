import json

import lambdae.shared as shared
import lambdae.models as models
import lambdae.jwt_tokens as tokens


def _get_channel(event):
    match_id = event["pathParameters"]["match_id"]
    return models.ChannelModel(match_id).get()


@shared.json_request
def message_post(event, context):
    user = tokens.require_authorization(event)
    message = json.load(event["body"])["message"]

    channel = _get_channel(event)
    channel.add_message(user.user_id, message)

    return shared.json_success_response({})


def message_get(event, context):
    user = tokens.require_authorization(event)

    channel = _get_channel(event)
    messages = channel.get_message(user.user_id)

    return shared.json_success_response({"messages": messages})
