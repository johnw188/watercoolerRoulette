import lambdae.shared as shared


def test_jwt_encoding():
    to_encode = {"bar": "baz"}
    encoded = shared.jwt_encode(to_encode)

    decoded = shared.jwt_decode(encoded)
    assert decoded == to_encode
