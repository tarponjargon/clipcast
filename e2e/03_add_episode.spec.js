import { expect, test } from "@playwright/test";
import {
  deleteTestAccount,
  createTestAccount,
  updateTestAccountPlan,
  getPlanByVoiceCode,
} from "./utils/db";
import { logInTestAccount } from "./utils/login";
import c from "config";

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
  await logInTestAccount(page);
});

test("User Can Add Podcast Episode", async () => {
  // make sure plan is base so I don't get charged
  await updateTestAccountPlan("base");

  // update voice
  await page.getByTestId("voices-link").click();
  // set listener for response
  let statusCode;
  page.on("response", (response) => {
    if (response.url().includes("/partials/app/update-voice")) {
      statusCode = response.status();
    }
  });
  const voiceEl = await page.locator('[for="voice-us"]');
  await voiceEl.click();
  expect(statusCode).toBe(200);

  // add a podcast episode via form at top
  await page.getByTestId("add-url-input").click();
  await page.getByTestId("add-url-input").fill("https://htmlforpeople.com/");
  await page.getByTestId("add-url-input").press("Enter");

  // check that the episode is in the list and play it
  const dataSel = "a[data-content-id][data-hostname='htmlforpeople.com']";
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

  // make sure play is visible, then close it
  const player = await page.locator("#podcast-player [data-name='shikwasa']");
  expect(player).toBeVisible();
  await page.locator("#podcast-player-close").click();
  expect(player).not.toBeVisible();

  // make sure the episoide voice is part of base plan
  const voiceCode = await page.locator(dataSel).getAttribute("data-voice");
  expect(voiceCode).toBe("us");
  const voicePlan = await getPlanByVoiceCode(voiceCode);
  expect(voicePlan.plan).toBe("base");

  // delete the episode
  const dataEl = await page.locator(dataSel);
  const contentId = await dataEl.getAttribute("data-content-id");
  await page.locator(`a[data-delete="${contentId}"]`).click();
  expect(dataEl).not.toBeVisible();
});
