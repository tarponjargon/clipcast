import { expect } from "@playwright/test";

export async function logInTestUser() {
  const response = await fetch(`${process.env.BASE_URL}/partials/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: process.env.TEST_ACCOUNT_EMAIL,
      password: process.env.TEST_ACCOUNT_PASSWORD,
    }),
  });

  const responseBody = await response.text();

  expect(statusCode).toBe(200);
  expect(responseBody).toContain("You are now logged in");
}
