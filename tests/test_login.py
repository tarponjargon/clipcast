from flask_app.modules.extensions import DB


def test_login(app, client):
    """Test the login route"""
    with app.test_request_context():
        response = client.post(
            "/partials/login",
            data={
                "email": app.config.get("TEST_ACCOUNT_EMAIL"),
                "password": app.config.get("TEST_ACCOUNT_PASSWORD"),
            },
        )

        print(response.text)
        assert response.status_code == 200
