import { expect } from "@playwright/test";

export async function logInTestAccount(page) {
  await page.goto(process.env.BASE_URL + "/login");
  await page.locator("#email-entry-field").click();
  await page.locator("#email-entry-field").fill(process.env.TEST_ACCOUNT_EMAIL);
  await page.locator("#email-entry-field").press("Tab");
  await page.locator("#password-field").fill(process.env.TEST_ACCOUNT_PASSWORD);
  await page.locator("#login-submit-button").click();
  await page.waitForNavigation();
  await expect(page).toHaveURL(/app/);
  await expect(page).toHaveTitle(/Dashboard/);
}
