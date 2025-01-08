async function signup(page, email, password) {
  await page.goto(process.env.BASE_URL + "/signup");
  await page.locator("#email-entry-field").click();
  await page.locator("#email-entry-field").fill(email);
  await page.locator("#password-field").click();
  await page.locator("#password-field").fill(password);
  await page.locator("#password-confirm-field").click();
  await page.locator("#password-confirm-field").fill(password);
  await page.getByTestId("terms-checkbox").check();
  await page.locator("#signup-submit-button").click();
  await page.waitForNavigation();
}
export default signup;
