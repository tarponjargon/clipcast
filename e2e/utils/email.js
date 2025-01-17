import imap from "imap-simple";

export async function getForgotPasswordLink() {
  const config = {
    imap: {
      user: process.env.TEST_ACCOUNT_EMAIL,
      password: process.env.TEST_ACCOUNT_GOOGLE_APP_PASSWORD,
      host: "imap.gmail.com",
      port: 993,
      tls: true,
      authTimeout: 3000,
      tlsOptions: { rejectUnauthorized: false },
    },
  };

  // console.log("Connecting to email server..." + JSON.stringify(config.imap, null, 2));

  const connection = await imap.connect({ imap: config.imap });
  await connection.openBox("INBOX");

  // console.log("Connected to email server " + connection);

  // Fetch unread emails
  const searchCriteria = ["UNSEEN"]; // Change to ['ALL'] to fetch all emails
  const fetchOptions = {
    bodies: ["HEADER.FIELDS (FROM TO SUBJECT DATE)", "TEXT"],
    struct: true,
  };

  const messages = await connection.search(searchCriteria, fetchOptions);

  // Sort messages from newest to oldest
  messages.sort((a, b) => new Date(b.attributes.date) - new Date(a.attributes.date));

  let resetLink;
  for (const message of messages) {
    const header = message.parts.find((part) => part.which.includes("HEADER")).body;
    // console.log("Date:", header.date);
    if (header.subject[0].startsWith("Reset Your ClipCast")) {
      const body = message.parts.find((part) => part.which === "TEXT").body;
      const resetLinkMatch = body.match(/https:\/\/[^\s]*resetpassword[^\s]*/);
      // console.log("Reset link match: ", resetLinkMatch);
      if (resetLinkMatch) {
        resetLink = resetLinkMatch[0].trim();
      }

      // Mark the email as deleted
      await connection.addFlags(message.attributes.uid, "\\Deleted");
      break;
    }
  }

  await connection.closeBox(true);
  connection.end();

  return resetLink;
}
