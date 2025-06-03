from werkzeug.security import generate_password_hash
from app import db, User             # same caveat: adjust import

def test_login_success(client):
    # seed a user directly
    with client.application.app_context():
        db.session.add(User(
            name="Dev",
            email="dev@example.com",
            password=generate_password_hash("pass123"),
            role="user"
        ))
        db.session.commit()

    resp = client.post("/login", data={
        "type": "user",
        "email": "dev@example.com",
        "password": "pass123"
    }, follow_redirects=True)

    assert b"Logged in successfully!" in resp.data
