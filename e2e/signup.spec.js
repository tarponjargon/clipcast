import { test, expect } from "@playwright/test";
const { runQuery } = require("./utils/db");

const deleteQuery = `DELETE FROM user WHERE email = ?`;

test.use({
  // Configure the context to use basic authentication
  httpCredentials: {
    username: "misc",
    password: "misc",
  },
});

test.beforeEach(async () => {
  await runQuery(deleteQuery, [process.env.TEST_ACCOUNT_EMAIL]);
});

test.afterEach(async () => {
  await runQuery(deleteQuery, [process.env.TEST_ACCOUNT_EMAIL]);
});

test("Test Sign Up", async ({ page }) => {
  // Intercept and listen to responses
  let statusCode;
  page.on("response", (response) => {
    if (response.url().includes("/partials/signup")) {
      statusCode = response.status();
    }
  });

  await page.goto(process.env.BASE_URL + "/signup");

  // Fill the email field
  await page.getByLabel("Your E-Mail *").click();
  await page.getByLabel("Your E-Mail *").fill(process.env.TEST_ACCOUNT_EMAIL);

  // Fill the password field
  await page.getByLabel("Password *", { exact: true }).click();
  await page.getByLabel("Password *", { exact: true }).fill(process.env.TEST_ACCOUNT_PASSWORD);

  // Fill the confirm password field
  await page.getByLabel("Confirm Password *").click();
  await page.getByLabel("Confirm Password *").fill("testemail2");

  // Click the sign-up button
  await page.getByRole("button", { name: "Sign Up", exact: true }).click();

  // Verify that the URL has not changed (because the terms checkbox is not checked)
  await expect(page).toHaveURL(/signup/);

  // Check the terms of use checkbox
  await page.getByTestId("terms-checkbox").check();

  // Click the sign-up button
  await page.getByRole("button", { name: "Sign Up", exact: true }).click();

  await page.waitForResponse(
    (response) => response.url().includes("/partials/signup") && response.status() === 400
  );

  // Assert the status code
  expect(statusCode).toBe(400);

  // Check that the response card contains the error message
  await expect(page.locator("#response-card")).toContainText(
    "Confirmation password does not match password"
  );

  // Fill the confirm password field
  await page.getByLabel("Confirm Password *").click();
  await page.getByLabel("Confirm Password *").fill("");
  await page.getByLabel("Confirm Password *").fill(process.env.TEST_ACCOUNT_PASSWORD);

  await page.getByRole("button", { name: "Sign Up", exact: true }).click();

  await page.waitForNavigation();

  // Assert the URL
  await expect(page).toHaveURL(/app/);
});
