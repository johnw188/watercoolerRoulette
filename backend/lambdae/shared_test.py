import json

import lambdae.shared as shared


def test_wrapper_error_handle():
    fail_message = "Abject failure"

    @shared.json_request
    def failing_function(event, context):
        raise RuntimeError(fail_message)

    result = failing_function({}, {})
    json_body = json.loads(result["body"])

    assert not json_body["ok"]
    assert fail_message in json_body["message"]


def test_wrapper_cookie_clearance():
    @shared.json_request
    def failing_function(event, context):
        raise shared.AuthException

    result = failing_function({}, {})
    json_body = json.loads(result["body"])

    assert not json_body["ok"]
    assert "Set-Cookie" in result["headers"]
    assert result["headers"]["Set-Cookie"].startswith("token=;")


def test_wrapper_origin_forward():
    # Make sure the request origin gets forwarded to the 'access-control-allow-origin' header
    @shared.json_request
    def failing_function(event, context):
        return shared.json_success_response({})

    origin = "foo.com"
    result = failing_function({"headers": {"origin": origin}}, {})
    json_body = json.loads(result["body"])

    assert json_body["ok"]
    assert result["headers"]["Access-Control-Allow-Origin"] == origin
