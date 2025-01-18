import { expect, test } from "@playwright/test";
import { deleteTestAccount, createTestAccount, getSubscriptionStatus } from "./utils/db";
import { logInTestAccount } from "./utils/login";

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
  await logInTestAccount(page);
});

// test.afterEach(async () => {
//   await deleteTestAccount();
// });

test("User Can Subscribe and Unsubscribe", async () => {
  // select basic plan
  await page.goto(process.env.BASE_URL + "/app/profile");

  // subscribe
  const response = await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes("/partials/update-profile-subscription") &&
        response.status() === 200
    ),
    page.locator("#customSwitch2").click(),
  ]);

  expect(response[0].status()).toBe(200);

  const toast = await page.locator("#toast-2-body");
  expect(toast).toHaveText("Subscription updated");

  const subscriptionObj = await getSubscriptionStatus();
  expect(subscriptionObj.subscribed).toBe(1);

  // unsubscribe
  const response2 = await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes("/partials/update-profile-subscription") &&
        response.status() === 200
    ),
    page.locator("#customSwitch2").click(),
  ]);

  expect(response2[0].status()).toBe(200);

  const toast2 = await page.locator("#toast-2-body");
  expect(toast2).toHaveText("Subscription updated");

  const subscriptionObj2 = await getSubscriptionStatus();
  expect(subscriptionObj2.subscribed).toBe(0);
});
