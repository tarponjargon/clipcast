// @ts-check
const { test, expect, chromium } = require("@playwright/test");

test.use({
  // Configure the context to use basic authentication
  httpCredentials: {
    username: "misc",
    password: "misc",
  },
});

test("has title", async ({ page }) => {
  await page.goto(process.env.BASE_URL);

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/ClipCast/);
});

test("get started link", async ({ page }) => {
  await page.goto(process.env.BASE_URL);

  // Click the get started link.
  await page.getByTestId("get-started").click();

  // Expects page to have a heading with the name of Installation.
  await expect(page.getByRole("heading", { name: "Sign Up" })).toBeVisible();
});

test("login link", async ({ page }) => {
  await page.goto(process.env.BASE_URL);

  // Click the signup button using data attribute
  await page.getByTestId("login-link").click();

  // Expects page to have a heading with the name of Sign up.
  await expect(page.getByRole("heading", { name: "Log In" })).toBeVisible();
});
