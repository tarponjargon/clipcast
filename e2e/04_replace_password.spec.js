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
  // launchOptions: {
  //   slowMo: 500, // Add slowMo option
  // },
});

test.beforeAll(async ({ browser }) => {
  page = await browser.newPage();
  await deleteTestAccount();
  await createTestAccount();
});

test.afterAll(async () => {
  await deleteTestAccount();
});

test("User Can Replace Password", async () => {
  // fill out forgotpassword form
  await page.goto(process.env.BASE_URL + "/forgotpassword");
  await page.locator("#email-entry-field").fill(process.env.TEST_ACCOUNT_EMAIL);
  await page.locator("#email-entry-field").press("Enter");
  const successEl = await page.locator("#success-target h1");
  expect(successEl).toHaveText("Submitted");

  // wait for email to arrive and parse reset link out of it
  await page.waitForTimeout(10000);
  const resetLink = await getForgotPasswordLink();
  await page.goto(resetLink);

  // fill out resetpassword form, testing when pw's don't match
  await page.locator("#password-field").fill("newpassword1");
  await page.locator("#password-confirm-field").fill("newpassword2");
  await page.locator("#password-confirm-field").press("Enter");
  await expect(page.locator("#response-card")).toContainText(
    "Confirmation password does not match"
  );

  // fill out resetpassword form, testing when pw's do match
  await page.locator("#password-field").fill("newpassword1");
  await page.locator("#password-confirm-field").fill("newpassword1");
  await page.locator("#password-confirm-field").press("Enter");
  const responseEl = await page.locator("#response-card");
  expect(responseEl).toContainText("password is updated");
  await expect(page).toHaveURL(/app/);

  // reset password back to original
  await page.getByTestId("account-link").click();
  await page.getByTestId("edit-password").click();
  await page.locator("#password-field").fill(process.env.TEST_ACCOUNT_PASSWORD);
  await page.locator("#password-confirm-field").fill(process.env.TEST_ACCOUNT_PASSWORD);
  await page.locator("#password-submit-button").click();

  // log out and back in with original password
  await page.getByTestId("logout-link").click();
  await logInTestAccount(page);
});
