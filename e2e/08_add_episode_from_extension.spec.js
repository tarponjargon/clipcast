import { expect, test } from "@playwright/test";
import { deleteTestAccount, createTestAccount, updateVoice } from "./utils/db";

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
  await updateVoice("us");
});

test("User Can Add Podcast From Extension", async () => {
  // example of a url that would be referred from the chrome extension
  await page.goto(
    process.env.BASE_URL + "/app/add-url?url=https%3A%2F%2Fclipcast.it%2Ftest-article"
  );

  // login should be required
  await page.locator("#email-entry-field").click();
  await page.locator("#email-entry-field").fill(process.env.TEST_ACCOUNT_EMAIL);
  await page.locator("#email-entry-field").press("Tab");
  await page.locator("#password-field").fill(process.env.TEST_ACCOUNT_PASSWORD);
  await page.locator("#login-submit-button").click();
  await expect(page).toHaveURL(/app/);

  // check that the episode is in the list
  const dataSel = "a[data-content-id][data-hostname='clipcast.it']";
  const playEl = await page.locator(dataSel);
  await playEl.waitFor();

  // capture the content id of the episode
  const dataEl = await page.locator(dataSel);
  const contentId = await dataEl.getAttribute("data-content-id");

  // delete the episode
  await page.locator(`a[data-delete="${contentId}"]`).click();
  expect(await page.locator(dataSel)).toBeHidden();
});
