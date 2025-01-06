import re
import os
from playwright.sync_api import sync_playwright, Page, expect


def test_has_title():
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False, slow_mo=1000, devtools=True)

        # Create a browser context with basic authentication
        context = browser.new_context(
            http_credentials={"username": "misc", "password": "misc"}
        )

        # Open a new page in the authenticated context
        page = context.new_page()

        # Navigate to the URL requiring basic auth
        page.goto(os.environ["BASE_URL"])

        store_name = os.environ["STORE_NAME"]
        expect(page).to_have_title(re.compile(store_name))
