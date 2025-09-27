
const axios = require('axios');
const fs = require('fs');

const ACCESS_TOKEN = 'PASTE_YOUR_TOKEN_HERE'; 

async function fetchEmails() {
  try {

    const listRes = await axios.get('https://gmail.googleapis.com/gmail/v1/users/me/messages', {
      headers: { Authorization: `Bearer ${ACCESS_TOKEN}` },
    });

    const messages = listRes.data.messages || [];
    console.log(`Fetched ${messages.length} messages`);

    let fileContent = '';

    for (const msg of messages) {
      const emailRes = await axios.get(`https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}`, {
        headers: { Authorization: `Bearer ${ACCESS_TOKEN}` },
      });
      fileContent += JSON.stringify(emailRes.data, null, 2) + '\n\n';
    }

    fs.writeFileSync('gmail_emails.txt', fileContent, 'utf8');
    console.log('✅ All emails saved to gmail_emails.txt in your project folder!');
  } catch (err) {
    console.error('❌ Error fetching emails:', err.response?.data || err.message);
  }
}

fetchEmails();
