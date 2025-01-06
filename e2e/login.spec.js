import { test, expect } from "@playwright/test";
import login from "./utils/login";

test.use({
  // Configure the context to use basic authentication
  httpCredentials: {
    username: "misc",
    password: "misc",
  },
});

test("user can access dashboard after login", async ({ page }) => {
  await page.goto(process.env.BASE_URL);
  await page.getByRole("link", { name: "Log In" }).click();
  await page.getByLabel("Your E-Mail *").click();
  await page.getByLabel("Your E-Mail *").fill(username);
  await page.getByLabel("Your E-Mail *").press("Tab");
  await page.getByLabel("Password *").fill(password);
  await page.getByRole("button", { name: "Log In", exact: true }).click();
  await page.waitForNavigation();
  await expect(page).toHaveURL(/app/);
  await expect(page).toHaveTitle(/Dashboard/);
});
