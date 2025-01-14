import { expect, test } from "@playwright/test";
import {
  deleteTestAccount,
  createTestAccount,
  getTestAccountPlan,
  updateTestAccountPlan,
} from "./utils/db";
import { logInTestAccount } from "./utils/login";

let page; // I'm going to re-use this for tests behind a login

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
  await logInTestAccount(page);
});

test("User Can Select Base Plan", async () => {
  await page.goto(process.env.BASE_URL + "/app/profile");
  const planEl = await page.locator('[for="plan-basic"]');
  await planEl.click();
  const toast = await page.locator("#toast-2-body");
  expect(toast).toHaveText("Plan updated");
  const planObj = await getTestAccountPlan();
  expect(planObj.plan).toBe("base");
});

test("User Can Add Podcast Episode", async () => {
  await updateTestAccountPlan("base");
  await page.getByTestId("add-url-input").click();
  await page.getByTestId("add-url-input").fill("https://htmlforpeople.com/");
  await page.getByTestId("add-url-input").press("Enter");
  const dataSel = "a[data-content-id][data-hostname='htmlforpeople.com']";
  const playSel = " .fa-play-circle";
  const pauseSel = " .fa-pause-circle";
  await page.locator(dataSel).click();
  await page.waitForSelector(dataSel + pauseSel);
  const pauseBtn = await page.locator(dataSel + pauseSel);
  expect(pauseBtn).toBeVisible();
  await page.waitForTimeout(1000);
  await pauseBtn.click();
  const playBtn = await page.locator(dataSel + playSel);
  expect(playBtn).toBeVisible();
  const player = await page.locator("#podcast-player [data-name='shikwasa']");
  // const elementDetails = await player.evaluate((el) => ({
  //   tagName: el.tagName,
  //   text: el.textContent,
  //   html: el.outerHTML,
  // }));
  // console.log("Element details:", elementDetails);
  expect(player).toBeVisible();
  await page.locator("#podcast-player-close").click();
  expect(player).not.toBeVisible();

  const dataEl = await page.locator(dataSel);
  const contentId = await dataEl.getAttribute("data-content-id");
  await page.locator(`a[data-delete="${contentId}"]`).click();
  expect(dataEl).not.toBeVisible();
});
