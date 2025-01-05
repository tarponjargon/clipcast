import { expect } from "@playwright/test";

async function login(page, username, password) {
  await page.goto(process.env.BASE_URL);
  await page.getByRole("link", { name: "Log In" }).click();
  await page.getByLabel("Your E-Mail *").click();
  await page.getByLabel("Your E-Mail *").fill(username);
  await page.getByLabel("Your E-Mail *").press("Tab");
  await page.getByLabel("Password *").fill(password);
  await page.getByRole("button", { name: "Log In", exact: true }).click();
  await page.waitForNavigation();
}

export default login;
