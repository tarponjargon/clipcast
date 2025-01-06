import os
import re
import pytest
from playwright.sync_api import sync_playwright, expect


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100, devtools=True)
        yield browser
        # browser.close()


@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context(
        http_credentials={"username": "misc", "password": "misc"}
    )
    page = context.new_page()
    yield page
    context.close()


def test_user_can_access_dashboard_after_login(page):
    base_url = os.environ.get("BASE_URL")
    page.goto(f"{base_url}/login")
    page.locator("#email-entry-field").fill(os.environ.get("TEST_ACCOUNT_EMAIL"))
    page.locator("#email-entry-field").press("Tab")
    page.locator("#password-field").fill(os.environ.get("TEST_ACCOUNT_PASSWORD"))
    page.locator("#login-submit-button").click()
    page.wait_for_url("**/app")
    expect(page).to_have_url(re.compile(r"/app"))
    expect(page).to_have_title(re.compile(r"Dashboard"))
