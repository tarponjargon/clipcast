import { expect, test } from "@playwright/test";
import { deleteTestAccount, createTestAccount, getTestAccountPlan } from "./utils/db";
import { logInTestAccount } from "./utils/login";

let page;

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

test("User Can Select Premium Plan", async () => {
  // select basic plan
  await page.goto(process.env.BASE_URL + "/app/profile");
  await page.locator('[href="/app/stripe-checkout"] button').first().click();
  // check that the url contains "stripe.com"
  expect(await page.url()).toContain("stripe.com");
});
