import { expect, test } from "@playwright/test";
import { deleteTestAccount, createTestAccount, updateVoice } from "./utils/db";
import { logInTestAccount } from "./utils/login";

let page;

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
  await logInTestAccount(page);
});

// test.afterAll(async () => {
//   await deleteTestAccount();
// });

test("User Can Submit Text content", async () => {
  test.slow();
  await updateVoice("us");
  await page.getByTestId("add-content-link").click();
  const content = `
    HTML is for people
    I feel strongly that anyone should be able to make a website with HTML if they want.
    This book will teach you how to do just that. It doesn't require
    any previous experience making websites or coding.
  `;
  await page.locator("#add-content-textarea").fill(content);
  await page.locator("#add-content-submit-button").click();

  // check that the episode is in the list and play it
  await page.goto(process.env.BASE_URL + "/app");
  const dataSel = "a[data-content-id]";
  const playSel = " .fa-play-circle";
  const pauseSel = " .fa-pause-circle";
  await page.locator(dataSel).click();
  await page.waitForSelector(dataSel + pauseSel);
  const pauseBtn = await page.locator(dataSel + pauseSel);
  expect(pauseBtn).toBeVisible();

  // pause the episode
  await pauseBtn.click();
  const playBtn = await page.locator(dataSel + playSel);
  expect(playBtn).toBeVisible();
});
