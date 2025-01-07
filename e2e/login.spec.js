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
  await login(page, process.env.TEST_ACCOUNT_EMAIL, process.env.TEST_ACCOUNT_PASSWORD);
  await expect(page).toHaveURL(/app/);
  await expect(page).toHaveTitle(/Dashboard/);
});
