import { expect, test } from "@playwright/test";
import { deleteTestAccount, createTestAccount, getTestAccountPlan } from "./utils/db";
import { logInTestAccount } from "./utils/login";

let page; // I'm going to re-use this for tests behind a login

test.describe.configure({ mode: "serial" });
test.use({
  httpCredentials: {
    username: "misc",
    password: "misc",
  },
});

test.beforeEach(async ({ browser }) => {
  page = await browser.newPage();
  await deleteTestAccount();
  await createTestAccount();
  await logInTestAccount(page);
});

test("User Can Select Base Plan", async () => {
  await page.getByTestId("account-link").click();
  await expect(page).toHaveURL(/app\/profile/);
  const planEl = page.locator('[for="plan-basic"]');
  await planEl.click();
  expect(page.locator("#toast-2-body")).toHaveText("Plan updated");
  const planObj = await getTestAccountPlan();
  expect(planObj.plan).toBe("base");
});

test("User Can Add Podcast Episode", async () => {
  await page.getByTestId("add-url-input").click();
  await page.getByTestId("add-url-input").fill("https://htmlforpeople.com/");
  await page.getByTestId("add-url-input").press("Enter");
  const episodeEl = await page.locator("a[data-content-id][data-title='HTML for People']");
  episodeEl.click();
});
