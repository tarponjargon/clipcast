const mysql = require("mysql2/promise");

/* these functions are for test support only */

export async function deleteTestAccount() {
  const deleteQuery = `DELETE FROM user WHERE email = ?`;
  await runQuery(deleteQuery, [process.env.TEST_ACCOUNT_EMAIL]);
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
  console.log("Running query: ", query, params);
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
