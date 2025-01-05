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
  await page.goto("/");

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/ClipCast/);
});

test("get started link", async ({ page }) => {
  await page.goto("/");

  // Click the get started link.
  await page.getByRole("link", { name: "Get started" }).click();

  // Expects page to have a heading with the name of Installation.
  await expect(page.getByRole("heading", { name: "Installation" })).toBeVisible();
});

test("signup button", async ({ page }) => {
  await page.goto("/");

  // Click the signup button using data attribute
  await page.getByRole("button", { name: "Sign up" }).click();

  // Expects page to have a heading with the name of Sign up.
  await expect(page.getByRole("heading", { name: "Sign up" })).toBeVisible();
});
