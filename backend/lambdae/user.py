import lambdae.jwt_tokens as tokens
import lambdae.shared as shared
import lambdae.models as models


@shared.json_request
def get_user_info(event, context):
    user = tokens.require_authorization(event)

    if event["pathParameters"] is None:
        path_params = {}
    else:
        path_params = event["pathParameters"]

    user_id_to_get = path_params.get('id', user.user_id)

    try:
        user_queried = models.UsersModel.get(user.group_id, user_id_to_get)
    except models.UsersModel.DoesNotExist:
        return shared.json_error_response(message='User "{}" does not exist.'.format(user_id_to_get), code=404)

    return shared.json_success_response({
        "user_id": user_queried.user_id,
        "username": user_queried.username,
        "avatar": user_queried.avatar
    })
