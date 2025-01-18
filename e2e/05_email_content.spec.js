import { expect, test } from "@playwright/test";
import { deleteTestAccount, createTestAccount, updateTestAccountPlan } from "./utils/db";
import { logInTestAccount } from "./utils/login";
import { sendEmail } from "./utils/email";

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

// test.afterAll(async () => {
//   await deleteTestAccount();
// });

test("User Can E-Mail Content", async () => {
  test.setTimeout(240000);
  await updateTestAccountPlan("base");
  await page.getByTestId("add-content-link").click();
  const extractedText = await page.locator("#email-field").textContent();
  const myEmail = extractedText.trim();
  const content = `
    HTML is for people
    I feel strongly that anyone should be able to make a website with HTML if they want.
    This book will teach you how to do just that. It doesn't require
    any previous experience making websites or coding.
  `;
  await sendEmail(myEmail, "HTML is for people", content);

  // wait for email to arrive and be processed
  await page.waitForTimeout(120000);

  await page.goto(process.env.BASE_URL + "/app");

  // check that the episode is in the list and play it
  const dataSel = "a[data-content-id]";
  const playSel = " .fa-play-circle";
  const pauseSel = " .fa-pause-circle";
  await page.locator(dataSel).click();
  await page.waitForSelector(dataSel + pauseSel);
  const pauseBtn = await page.locator(dataSel + pauseSel);
  expect(pauseBtn).toBeVisible();
  await page.waitForTimeout(1000);

  // pause the episode
  await pauseBtn.click();
  const playBtn = await page.locator(dataSel + playSel);
  expect(playBtn).toBeVisible();
});
