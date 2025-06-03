def test_signup_success(client):
    resp = client.post("/signup", data={
        "type": "user",
        "name": "Test User",
        "email": "tuser@example.com",
        "password": "secret123",
        "confirm_password": "secret123"
    }, follow_redirects=True)

    assert b"Signup successful!" in resp.data
