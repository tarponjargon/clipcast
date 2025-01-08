async function login(page, username, password) {
  await page.goto(process.env.BASE_URL + "/login");
  await page.locator("#email-entry-field").click();
  await page.locator("#email-entry-field").fill(username);
  await page.locator("#email-entry-field").press("Tab");
  await page.locator("#password-field").fill(password);
  await page.locator("#login-submit-button").click();
  await page.waitForNavigation();
}
export default login;
