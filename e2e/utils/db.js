const mysql = require("mysql2/promise");

/* these functions are for test support only */

export async function getTestAccountPlan() {
  const selectQuery = `SELECT plan FROM user WHERE email = ?`;
  const resultArr = await runQuery(selectQuery, [process.env.TEST_ACCOUNT_EMAIL]);
  return resultArr[0];
}

export async function getPlanByVoiceCode(code) {
  const selectQuery = `SELECT plan FROM voices WHERE voice_code = ?`;
  const resultArr = await runQuery(selectQuery, [code]);
  return resultArr[0];
}

export async function updateTestAccountPlan(newPlan) {
  const updQuery = `UPDATE user SET plan = ? WHERE email = ?`;
  const result = await runQuery(updQuery, [newPlan, process.env.TEST_ACCOUNT_EMAIL]);
  // console.log("Result of update:", result);
  return result;
}

export async function updateVoice(voice) {
  const updQuery = `UPDATE user SET premium_voice = ? WHERE email = ?`;
  const result = await runQuery(updQuery, [voice, process.env.TEST_ACCOUNT_EMAIL]);
  // console.log("Result of update:", result);
  return result;
}

export async function getSubscriptionStatus() {
  const selectQuery = `SELECT subscribed FROM contact WHERE email = ?`;
  const resultArr = await runQuery(selectQuery, [process.env.TEST_ACCOUNT_EMAIL]);
  return resultArr[0];
}

export async function deleteTestAccount() {
  const userIdArr = await runQuery(`SELECT user_id FROM user WHERE email = ?`, [
    process.env.TEST_ACCOUNT_EMAIL,
  ]);
  if (userIdArr.length === 0) {
    return;
  }
  const userId = userIdArr[0].user_id;
  await runQuery(`DELETE FROM user WHERE user_id = ?`, [userId]);
  await runQuery(`DELETE FROM notification WHERE user_id = ?`, [userId]);
  await runQuery(`DELETE FROM login WHERE user_id = ?`, [userId]);
  await runQuery(`DELETE FROM podcast_content WHERE user_id = ?`, [userId]);
  await runQuery(`DELETE FROM contact WHERE email = ?`, [process.env.TEST_ACCOUNT_EMAIL]);
}

export async function createTestAccount() {
  const insertQuery = `
      INSERT INTO user (
        user_id,
        email,
        password_hash,
        accepted_terms,
        is_active,
        base_voice,
        premium_voice,
        created_at
      )
      VALUES (
        UUID(),
        ?,
        ?,
        1,
        1,
        ?,
        ?,
        NOW()
      )
  `;
  await runQuery(insertQuery, [
    process.env.TEST_ACCOUNT_EMAIL,
    "pbkdf2_sha256$260000$b5583ace9a6ebfe682524b13f1fa2858$vVWyROW9XsckfmlCUgXd3KeMo5jV4hhGtBd5yhwGFTE=",
    process.env.DEFAULT_BASE_VOICE,
    process.env.DEFAULT_PREMIUM_VOICE,
  ]);
}

async function runQuery(query, params) {
  // console.log("Running query: ", query, params);
  const connection = await mysql.createConnection({
    host: process.env.MYSQL_LOCALHOST,
    port: process.env.MYSQL_HOST_PORT,
    user: process.env.MYSQL_USER,
    password: process.env.MYSQL_PASSWORD,
    database: process.env.MYSQL_DATABASE,
  });

  const [results] = await connection.execute(query, params);
  await connection.end();
  return results;
}
