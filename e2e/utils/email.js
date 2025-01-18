import imap from "imap-simple";
import nodemailer from "nodemailer";

const imapConfig = {
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

export async function getForgotPasswordLink() {
  const connection = await imap.connect({ imap: imapConfig.imap });
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

export async function sendEmail(to, subject, text) {
  console.log("Sending email to", to, "with subject", subject, "and text", text);
  const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
      user: process.env.TEST_ACCOUNT_EMAIL,
      pass: process.env.TEST_ACCOUNT_GOOGLE_APP_PASSWORD,
    },
  });

  const mailOptions = {
    from: process.env.TEST_ACCOUNT_EMAIL,
    to,
    subject,
    text,
  };

  await transporter.sendMail(mailOptions);
}
