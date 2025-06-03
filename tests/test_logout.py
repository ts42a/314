from werkzeug.security import generate_password_hash
from app import db, User

def test_logout(client):
    # log in first
    with client.application.app_context():
        db.session.add(User(
            name="Log",
            email="log@example.com",
            password=generate_password_hash("p4ss"),
            role="user"
        ))
        db.session.commit()

    client.post("/login", data={
        "type": "user",
        "email": "log@example.com",
        "password": "p4ss"
    }, follow_redirects=True)

    # now log out
    resp = client.get("/logout", follow_redirects=True)
    assert b"Logged out." in resp.data
