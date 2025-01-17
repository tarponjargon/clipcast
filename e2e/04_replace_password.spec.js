import { expect, test } from "@playwright/test";
import { deleteTestAccount, createTestAccount, getTestAccountPlan } from "./utils/db";
import { logInTestAccount } from "./utils/login";
import { getForgotPasswordLink } from "./utils/email";

let page;

test.describe.configure({ mode: "serial" });
test.use({
  httpCredentials: {
    username: "misc",
    password: "misc",
  },
  launchOptions: {
    slowMo: 500, // Add slowMo option
  },
});

test.beforeAll(async ({ browser }) => {
  page = await browser.newPage();
  await deleteTestAccount();
  await createTestAccount();
});

test("User Can Replace Password", async () => {
  await page.goto(process.env.BASE_URL + "/forgotpassword");
  await page.locator("#email-entry-field").click();
  await page.locator("#email-entry-field").fill(process.env.TEST_ACCOUNT_EMAIL);
  await page.locator("#email-entry-field").press("Enter");
  const successEl = await page.locator("#success-target h1");
  expect(successEl).toHaveText("Submitted");
  await page.waitForTimeout(5000);
  const resetLink = await getForgotPasswordLink();
  await page.goto(resetLink);
  await page.locator("#password-field").fill("newpassword1");
  await page.locator("#password-confirm-field").fill("newpassword2");
  await page.locator("#password-confirm-field").press("Enter");
  await expect(page.locator("#response-card")).toContainText(
    "Confirmation password does not match"
  );
  await page.locator("#password-field").fill(process.env.TEST_ACCOUNT_PASSWORD);
  await page.locator("#password-confirm-field").fill(process.env.TEST_ACCOUNT_PASSWORD);
  await page.locator("#password-confirm-field").press("Enter");
  const responseEl = await page.locator("#response-card");
  expect(responseEl).toContainText("Password updated successfully");
  await expect(page).toHaveURL(/app/);
});
