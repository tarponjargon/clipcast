import { test, expect } from "@playwright/test";
const { deleteTestAccount, createTestAccount } = require("./utils/db");

// Annotate entire file as serial.
test.describe.configure({ mode: "serial" });

test.use({
  httpCredentials: {
    username: "misc",
    password: "misc",
  },
});

test.beforeEach(async () => {
  await deleteTestAccount(process.env.TEST_ACCOUNT_EMAIL);
});

test.afterEach(async () => {
  await deleteTestAccount(process.env.TEST_ACCOUNT_EMAIL);
});

test("User Can Sign Up", async ({ page }) => {
  // Intercept and listen to responses
  let statusCode;
  page.on("response", (response) => {
    if (response.url().includes("/partials/signup")) {
      statusCode = response.status();
    }
  });
  await page.goto(process.env.BASE_URL + "/signup");
  await page.locator("#email-entry-field").click();
  await page.locator("#email-entry-field").fill(process.env.TEST_ACCOUNT_EMAIL);
  await page.locator("#password-field").click();
  await page.locator("#password-field").fill(process.env.TEST_ACCOUNT_PASSWORD);
  await page.locator("#password-confirm-field").click();
  await page.locator("#password-confirm-field").fill("testemail2");
  await page.locator("#signup-submit-button").click();
  await expect(page).toHaveURL(/signup/);
  await page.getByTestId("terms-checkbox").check();
  await page.locator("#signup-submit-button").click();
  await page.waitForResponse(
    (response) => response.url().includes("/partials/signup") && response.status() === 400
  );
  expect(statusCode).toBe(400);
  await expect(page.locator("#response-card")).toContainText(
    "Confirmation password does not match password"
  );
  await page.locator("#password-confirm-field").click();
  await page.locator("#password-confirm-field").fill("");
  await page.locator("#password-confirm-field").fill(process.env.TEST_ACCOUNT_PASSWORD);
  await page.locator("#signup-submit-button").click();
  await expect(page).toHaveURL(/app/);
});

test("User Can Log In", async ({ page }) => {
  console.log("Running login test");
  await createTestAccount();
  await page.goto(process.env.BASE_URL + "/login");
  await page.locator("#email-entry-field").click();
  await page.locator("#email-entry-field").fill(process.env.TEST_ACCOUNT_EMAIL);
  await page.locator("#email-entry-field").press("Tab");
  await page.locator("#password-field").fill(process.env.TEST_ACCOUNT_PASSWORD);
  await page.locator("#login-submit-button").click();
  await expect(page).toHaveURL(/app/);
  await expect(page).toHaveTitle(/Dashboard/);
});
