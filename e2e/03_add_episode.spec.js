import { expect, test } from "@playwright/test";
import { deleteTestAccount, createTestAccount, updateVoice } from "./utils/db";
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
  test.slow();
  // make sure voice is us so I don't get charged
  await updateVoice("us");

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

  // delete the episode
  await page.locator(`a[data-delete="${contentId}"]`).click();
  expect(await page.locator(dataSel)).toBeHidden();
});
