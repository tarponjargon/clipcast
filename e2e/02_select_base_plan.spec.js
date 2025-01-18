import { expect, test } from "@playwright/test";
import { deleteTestAccount, createTestAccount, getTestAccountPlan } from "./utils/db";
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

test("User Can Select Base Plan", async () => {
  // set listener for response
  let statusCode;
  page.on("response", (response) => {
    if (response.url().includes("/partials/app/update-plan")) {
      statusCode = response.status();
    }
  });

  // select basic plan
  await page.goto(process.env.BASE_URL + "/app/profile");
  const planEl = await page.locator('[for="plan-basic"]');
  await planEl.click();

  // make sure it's selected in the db and success indicator appears
  await page.waitForResponse(
    (response) => response.url().includes("/partials/app/update-plan") && response.status() === 200
  );
  expect(statusCode).toBe(200);
  const toast = await page.locator("#toast-2-body");
  expect(toast).toHaveText("Plan updated");
  const planObj = await getTestAccountPlan();
  expect(planObj.plan).toBe("base");
});
