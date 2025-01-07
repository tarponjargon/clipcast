const mysql = require("mysql2/promise");

async function runQuery(query, params) {
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

module.exports = { runQuery };
