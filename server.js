const fs = require('fs');
const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

function decodeBase64(str) {
  return Buffer.from(str.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8');
}

function cleanHtml(html) {
  return html
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '') 
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '') 
    .replace(/<\/?[^>]+(>|$)/g, '') 
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/\s+/g, ' ')
    .trim();
}

app.post('/fetch-emails', async (req, res) => {
  try {
    const { accessToken } = req.body;
    const messagesRes = await axios.get(
      'https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=50',
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );

    const messages = messagesRes.data.messages || [];
    const seenIds = new Set();
    const emailData = [];

    for (const msg of messages) {
      if (seenIds.has(msg.id)) continue;
      seenIds.add(msg.id);

      const messageRes = await axios.get(
        `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}?format=full`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );

      const payload = messageRes.data.payload;
      const headers = payload.headers.reduce((acc, h) => {
        acc[h.name.toLowerCase()] = h.value;
        return acc;
      }, {});

      let body = '';

      if (payload.parts) {
        const plainPart = payload.parts.find(p => p.mimeType === 'text/plain' && p.body?.data);
        if (plainPart) {
          body = decodeBase64(plainPart.body.data);
        } else {

          const htmlPart = payload.parts.find(p => p.mimeType === 'text/html' && p.body?.data);
          if (htmlPart) body = cleanHtml(decodeBase64(htmlPart.body.data));
        }
      } else if (payload.body?.data) {
        
        body = payload.mimeType === 'text/html' ? cleanHtml(decodeBase64(payload.body.data)) : decodeBase64(payload.body.data);
      }

      emailData.push(
        `From: ${headers.from || ''}\n` +
        `To: ${headers.to || ''}\n` +
        `Date: ${headers.date || ''}\n` +
        `Subject: ${headers.subject || ''}\n` +
        `Body:\n${body}\n` +
        `------------------------\n`
      );
    }

    fs.writeFileSync('gmail_emails.txt', emailData.join('\n'), 'utf-8');
    res.json({ message: '✅ Last 100 distinct emails saved to gmail_emails.txt (clean text)' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch emails' });
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));
