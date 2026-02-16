# Stripe Integration & Payment Setup Guide

**PZDetector™** by Chair-to-Keyboard™

This guide explains how to set up Stripe payments for PZDetector™ licensing.

---

## Overview

The PZDetector™ payment system consists of:

1. **Static Website** (`web/`) - Pricing page with Stripe Checkout
2. **License API** (`api/license_api.py`) - Flask backend for webhooks
3. **Desktop App** - License validation client

---

## 1. Stripe Account Setup

### Create Stripe Account

1. Go to https://stripe.com and create an account
2. Complete business verification (required for live payments)
3. Navigate to **Dashboard → Developers → API keys**

### Get API Keys

You'll need three keys:

```bash
# Publishable Key (public, goes in frontend)
pk_test_xxxxxxxxxxxxxxxx  # Test mode
pk_live_xxxxxxxxxxxxxxxx  # Live mode

# Secret Key (private, goes in backend)
sk_test_xxxxxxxxxxxxxxxx  # Test mode
sk_live_xxxxxxxxxxxxxxxx  # Live mode

# Webhook Secret (generated when you create webhook)
whsec_xxxxxxxxxxxxxxxx
```

---

## 2. Create Products in Stripe

### Dashboard → Products → Add Product

**Personal Plan:**
- Name: `PZDetector™ Personal`
- Description: `Lifetime license for 1 device`
- Pricing: `$49.00` (one-time payment)
- Copy the **Price ID**: `price_xxxxxxxxxxxxx`

**Professional Plan:**
- Name: `PZDetector™ Professional`
- Description: `Lifetime license for 3 devices with enterprise features`
- Pricing: `$99.00` (one-time payment)
- Copy the **Price ID**: `price_yyyyyyyyyyyyy`

---

## 3. Configure Environment Variables

### Create `.env` file in project root:

```bash
cp .env.example .env
nano .env  # or use your editor
```

### Add your Stripe credentials:

```bash
# Stripe Keys
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET

# Stripe Price IDs
STRIPE_PRICE_PERSONAL=price_1234567890abcdef
STRIPE_PRICE_PROFESSIONAL=price_0987654321fedcba

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
```

**⚠️ IMPORTANT:** Never commit `.env` to Git! It's already in `.gitignore`.

---

## 4. Update Frontend with Publishable Key

### Edit `web/pricing.html`:

Find this line:
```javascript
const stripe = Stripe('pk_test_YOUR_PUBLISHABLE_KEY_HERE');
```

Replace with your actual publishable key:
```javascript
const stripe = Stripe('pk_test_51N1a2b3c4d5e6f7g8h9i0j');
```

---

## 5. Deploy License API

### Option A: Local Development

```bash
# Install dependencies
cd api
pip install -r requirements.txt

# Run the API
python license_api.py
```

API will be available at `http://localhost:5000`

### Option B: Production Deployment (Railway/Heroku/DigitalOcean)

**Railway.app (Recommended):**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Add environment variables in Railway dashboard
railway variables set STRIPE_SECRET_KEY=sk_live_xxx
railway variables set STRIPE_WEBHOOK_SECRET=whsec_xxx

# Deploy
railway up
```

Your API URL: `https://your-app.railway.app`

### Option C: Netlify Functions (Serverless)

Create `netlify/functions/webhook.js`:
```javascript
// Convert license_api.py to serverless function
// See Netlify Functions documentation
```

---

## 6. Configure Stripe Webhooks

### Dashboard → Developers → Webhooks → Add Endpoint

**Endpoint URL:**
```
https://your-api-domain.com/api/webhook
```

**Events to listen for:**
- `checkout.session.completed` ✓

**Webhook Secret:**
Copy the signing secret (`whsec_xxx`) and add to `.env`

---

## 7. Test the Integration

### Test Mode Checkout

1. Visit `http://localhost:8000/pricing.html`
2. Click "Start 7-Day Trial" on any plan
3. Use Stripe test card:
   ```
   Card: 4242 4242 4242 4242
   Expiry: Any future date
   CVC: Any 3 digits
   ZIP: Any 5 digits
   ```
4. Complete checkout
5. Check `api/licenses.json` - license key should be generated
6. Check Stripe Dashboard → Payments - should see test payment

### Verify Webhook Delivery

1. Stripe Dashboard → Developers → Webhooks
2. Click your webhook endpoint
3. Check "Attempts" tab - should see successful delivery

---

## 8. Update Desktop App

### Edit `app/config.json`:

```json
{
  "purchaseUrl": "https://pzdetector.com/pricing",
  "enableLicenseCheck": true,
  "trialDays": 7
}
```

### Integrate new license service:

Replace `app/license_service.py` with `app/license_service_v2.py`:

```bash
mv app/license_service.py app/license_service_v1_backup.py
mv app/license_service_v2.py app/license_service.py
```

Add to `app/requirements.txt`:
```
requests>=2.31.0
```

---

## 9. Go Live

### Switch to Live Mode

1. Set environment variables to live keys:
   ```bash
   STRIPE_SECRET_KEY=sk_live_xxxxx
   STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
   ```

2. Update `web/pricing.html` with live publishable key

3. Update webhook URL to production domain

4. Test with real card (charge yourself $1 to verify)

5. Refund test transaction in Stripe Dashboard

---

## 10. Email Delivery (Optional but Recommended)

### Option A: SendGrid

```bash
pip install sendgrid

# Add to .env
SENDGRID_API_KEY=SG.xxxxxxxxxx
EMAIL_FROM=licenses@pzdetector.com
```

Update `license_api.py`:
```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_license_email(email, license_key, plan):
    message = Mail(
        from_email='licenses@pzdetector.com',
        to_emails=email,
        subject='Your PZDetector™ License Key',
        html_content=f'''
            <h2>Welcome to PZDetector™!</h2>
            <p>Your license key: <strong>{license_key}</strong></p>
        '''
    )
    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    response = sg.send(message)
```

### Option B: AWS SES

```bash
pip install boto3

# Add to .env
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
EMAIL_FROM=licenses@pzdetector.com
```

---

## Pricing Tiers Summary

| Plan | Price | Devices | Features |
|------|-------|---------|----------|
| **Personal** | $49 | 1 | Core PZ detection, Glazed Vision, Process Guardian |
| **Professional** | $99 | 3 | + Network Control, Biometric, Advanced Logging |
| **Enterprise** | Custom | Unlimited | + SSO, AD Deployment, Custom Branding, SLA |

---

## Security Checklist

- [ ] API keys stored in environment variables (not in code)
- [ ] Webhook signature verification enabled
- [ ] HTTPS enabled on API endpoint
- [ ] `.env` file added to `.gitignore`
- [ ] Rate limiting enabled on API endpoints
- [ ] License database backed up regularly
- [ ] Error messages don't expose sensitive data

---

## Support & Troubleshooting

### Common Issues

**"Invalid API Key"**
- Check `.env` file has correct keys
- Verify you're using test/live keys consistently

**"Webhook not receiving events"**
- Check webhook URL is publicly accessible
- Verify webhook secret matches
- Check Stripe Dashboard → Webhooks → Attempts

**"License validation fails"**
- Ensure API is running and accessible
- Check network connectivity from desktop app
- Verify API URL in config.json

---

## Next Steps

1. Set up monitoring (e.g., Sentry for error tracking)
2. Configure email delivery (SendGrid/AWS SES)
3. Add analytics (Stripe Dashboard has built-in reports)
4. Create referral/discount program
5. Set up automated invoicing for Enterprise

---

**Questions?** Email: support@pzdetector.com

**PZDetector™** by Chair-to-Keyboard™  
*The Human Centric Software Development Company*
