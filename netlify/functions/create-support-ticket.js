const client = require('node-zendesk').createClient({
  username: process.env.ZENDESK_EMAIL,
  token: process.env.ZENDESK_API_TOKEN,
  subdomain: process.env.ZENDESK_SUBDOMAIN
});

exports.handler = async (event) => {
  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const { email, subject, description, licenseKey, osVersion } = JSON.parse(event.body);

    // Validate required fields
    if (!email || !subject || !description) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Missing required fields: email, subject, description' })
      };
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Invalid email format' })
      };
    }

    // Build ticket body with system info
    const ticketBody = `Customer Email: ${email}
OS Version: ${osVersion || 'Not provided'}
License Key: ${licenseKey ? licenseKey.substring(0, 5) + '...' : 'Not activated'}

---

${description}`;

    // Create Zendesk ticket
    const ticket = {
      ticket: {
        subject: `[PZDetector™] ${subject}`,
        description: ticketBody,
        requester: {
          email: email,
          name: email.split('@')[0]
        },
        type: 'problem',
        tags: ['pzdetector', 'desktop-app'],
        custom_fields: [
          {
            id: process.env.ZENDESK_LICENSE_FIELD_ID || null,
            value: licenseKey ? 'licensed' : 'trial'
          }
        ]
      }
    };

    // Remove null custom fields
    ticket.ticket.custom_fields = ticket.ticket.custom_fields.filter(f => f.id);

    const result = await client.tickets.create(ticket);

    console.log(`[SUCCESS] Zendesk ticket created: #${result.ticket.id}`);

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        success: true,
        ticketId: result.ticket.id,
        message: `Support ticket #${result.ticket.id} created. We'll respond within 24 hours.`
      })
    };

  } catch (error) {
    console.error('[ERROR] Failed to create Zendesk ticket:', error.message);

    // Don't expose internal errors to client
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Failed to create support ticket. Please try again later or email support@pzdetector.com'
      })
    };
  }
};
