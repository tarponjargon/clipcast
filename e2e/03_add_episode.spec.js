import { expect, test } from "@playwright/test";
import {
  deleteTestAccount,
  createTestAccount,
  updateTestAccountPlan,
  getPlanByVoiceCode,
} from "./utils/db";
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

test("User Can Add Podcast Episode", async () => {
  // make sure plan is base so I don't get charged
  await updateTestAccountPlan("base");

  // update voice
  await page.getByTestId("voices-link").click();
  const voiceEl = await page.locator('[for="voice-us"]');
  // listen for updatevoice AJAX request
  const response = await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes("/partials/app/update-voice") && response.status() === 200
    ),
    await voiceEl.click(),
  ]);
  expect(response[0].status()).toBe(200);

  // add a podcast episode via form at top
  await page.getByTestId("add-url-input").fill("https://clipcast.it/test-article");
  await page.getByTestId("add-url-input").press("Enter");

  // check that the episode is in the list
  const dataSel = "a[data-content-id][data-hostname='clipcast.it']";
  const playSel = " .fa-play-circle";
  const pauseSel = " .fa-pause-circle";
  const playEl = await page.locator(dataSel);
  await playEl.waitFor();

  // capture the content id of the episode
  const dataEl = await page.locator(dataSel);
  const contentId = await dataEl.getAttribute("data-content-id");

  // check notification exists
  const badgeEl = await page.locator("#notifications-badge");
  await badgeEl.waitFor();
  expect(badgeEl).toBeVisible();
  await page.locator("#notifications-link").click();
  const notificationSel = `[data-notification='${contentId}']`;
  expect(await page.locator(notificationSel + " .bi-bell-fill")).toBeVisible();
  expect(badgeEl).toBeHidden();

  // play episode
  await page.locator(dataSel).click();
  await page.waitForTimeout(2000);
  const pauseBtn = await page.locator(dataSel + pauseSel);
  expect(pauseBtn).toBeVisible();

  // make sure there's a duration value in the player.
  const durationElement = await page.locator("#podcast-player .shk-time_duration");
  const durationText = await durationElement.textContent();
  const durationRegex = /^(\d{2}:)?\d{2}:\d{2}$/;
  expect(durationText).toMatch(durationRegex);

  // pause the episode
  await pauseBtn.click();
  const playBtn = await page.locator(dataSel + playSel);
  expect(playBtn).toBeVisible();

  // make sure play is visible, then close it
  const player = await page.locator("#podcast-player [data-name='shikwasa']");
  expect(player).toBeVisible();
  await page.locator("#podcast-player-close").click();
  expect(await page.locator("#podcast-player [data-name='shikwasa']")).toBeHidden();

  // make sure the episoide voice is part of base plan
  const voiceCode = await page.locator(dataSel).getAttribute("data-voice");
  expect(voiceCode).toBe("us");
  const voicePlan = await getPlanByVoiceCode(voiceCode);
  expect(voicePlan.plan).toBe("base");

  // delete the episode
  await page.locator(`a[data-delete="${contentId}"]`).click();
  expect(await page.locator(dataSel)).toBeHidden();
});
