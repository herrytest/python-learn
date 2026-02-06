from app.core.security import create_access_token, decode_access_token


def test_create_and_decode_token_roundtrip():
    token = create_access_token("demo-user")
    assert decode_access_token(token) == "demo-user"
