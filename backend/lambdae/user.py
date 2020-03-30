import lambdae.jwt_tokens as tokens
import lambdae.shared as shared
import lambdae.models as models


@shared.json_request
def get_user_info(event, context):
    user = tokens.require_authorization(event)
    user_id_to_get = event['pathParameters'].get('id', user.user_id)
    models.UsersModel.get(user.group_id, user_id_to_get)
    return shared.json_success_response({"username": user.username, "avatar": user.avatar})
