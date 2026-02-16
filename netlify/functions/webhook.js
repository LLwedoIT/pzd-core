/**
 * Netlify Function: Stripe Webhook Handler
 * 
 * POST /.netlify/functions/webhook
 * Handles: checkout.session.completed
 */

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { createClient } = require('@supabase/supabase-js');
const crypto = require('crypto');

// Initialize Supabase client (or use your preferred database)
const supabase = process.env.SUPABASE_URL && process.env.SUPABASE_KEY
  ? createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY)
  : null;

/**
 * Generate a cryptographically secure license key
 */
function generateLicenseKey() {
  const parts = [];
  for (let i = 0; i < 4; i++) {
    const part = crypto.randomBytes(2).toString('hex').toUpperCase();
    parts.push(part);
  }
  return `PZDT-${parts.join('-')}`;
}

/**
 * Create license record in database
 */
async function createLicense(customerEmail, plan, devices = 1) {
  const licenseKey = generateLicenseKey();
  
  const licenseData = {
    key: licenseKey,
    email: customerEmail,
    plan: plan,
    devices: devices,
    created: new Date().toISOString(),
    active: true,
    activations: []
  };

  if (supabase) {
    // Store in Supabase
    const { error } = await supabase
      .from('licenses')
      .insert([licenseData]);
    
    if (error) {
      console.error('Supabase insert error:', error);
      throw error;
    }
  } else {
    // Fallback: Log to console (not recommended for production)
    console.log('[LICENSE CREATED]', JSON.stringify(licenseData, null, 2));
    console.warn('Warning: No database configured. License only logged to console.');
  }

  return licenseData;
}

/**
 * Send license key via email
 */
async function sendLicenseEmail(email, licenseKey, plan) {
  // Using Netlify Forms or external email service
  // For production, integrate SendGrid, AWS SES, or Mailgun
  
  const emailBody = `
    Your PZDetector™ License Key
    
    Thank you for your purchase!
    
    License Key: ${licenseKey}
    Plan: ${plan}
    
    To activate:
    1. Open PZDetector™
    2. Go to License & Trial section
    3. Click "Activate License"
    4. Enter your license key
    
    Need help? Email support@pzdetector.com
    
    --
    Chair-to-Keyboard™
    The Human Centric Software Development Company
  `;

  // TODO: Implement actual email sending
  // For now, just log it
  console.log('[EMAIL]', {
    to: email,
    subject: 'Your PZDetector™ License Key',
    licenseKey,
    plan
  });

  // If using SendGrid:
  /*
  const sgMail = require('@sendgrid/mail');
  sgMail.setApiKey(process.env.SENDGRID_API_KEY);
  
  await sgMail.send({
    to: email,
    from: 'licenses@pzdetector.com',
    subject: 'Your PZDetector™ License Key',
    text: emailBody,
  });
  */
}

exports.handler = async (event, context) => {
  // Only allow POST
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  const sig = event.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  let stripeEvent;

  try {
    // Verify webhook signature
    stripeEvent = stripe.webhooks.constructEvent(
      event.body,
      sig,
      webhookSecret
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Invalid signature' })
    };
  }

  // Handle the event
  try {
    if (stripeEvent.type === 'checkout.session.completed') {
      const session = stripeEvent.data.object;
      
      // Extract customer info
      const customerEmail = session.customer_details?.email;
      const plan = session.metadata?.plan || 'unknown';
      
      // Determine device count based on plan
      const devices = plan === 'price_personal' ? 1 : 3;
      
      // Generate and save license
      const license = await createLicense(customerEmail, plan, devices);
      
      // Send license key to customer
      await sendLicenseEmail(customerEmail, license.key, plan);
      
      console.log('[SUCCESS] License created:', license.key, 'for', customerEmail);
    }

    return {
      statusCode: 200,
      body: JSON.stringify({ received: true })
    };

  } catch (error) {
    console.error('Webhook handler error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
