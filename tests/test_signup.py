from flask_app.modules.extensions import DB


def test_signup(app, client):
    """Test the signup route"""
    with app.test_request_context():

        fake_email = "testemail@testemail.com"

        response = client.post(
            "/partials/signup",
            data={
                "email": fake_email,
                "password": "sdlks9IusOpiUse",
                "password_confirm": "sdlks9IusOpiUse",
                "accepted_terms": "1",
                "marketing_subscribed": None,
            },
        )

        print(response.text)
        assert response.status_code == 200

        # clean up
        deleted = DB.delete_query(
            "DELETE FROM user WHERE email = %(email)s", {"email": fake_email}
        )
        assert deleted == 1
