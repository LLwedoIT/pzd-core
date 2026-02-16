# PZDetector™ Production Go-Live Checklist

**Chair-to-Keyboard™** | *The Human Centric Software Development Company*

Complete pre-launch verification checklist with copy-paste commands. Follow in order.

---

## 📋 Pre-Launch Requirements

- [ ] Stripe account created and verified
- [ ] Domain registered (pzdetector.com or custom)
- [ ] SSL certificate (automatic with Netlify)
- [ ] Email service configured (SendGrid/AWS SES - optional but recommended)
- [ ] GitHub account with repository access
- [ ] Netlify account created

---

## 🚀 PHASE 1: Stripe Setup (Day 1)

### 1.1 Create Stripe Account

```
https://stripe.com/register
```

- Go to Stripe.com
- Sign up with business email
- Complete verification (ID check, business details)
- Allow 24-48 hours for verification

### 1.2 Get API Keys

Once verified, get your keys:

```
Stripe Dashboard → Developers → API Keys
```

**Copy these values:**

```
STRIPE_PUBLIC_KEY=pk_live_xxxxxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxx
```

> ⚠️ Keep these SECRET_KEY values private! Never commit to GitHub.

### 1.3 Create Products & Prices

In Stripe Dashboard → Products:

**Product 1: Personal**
```
Name: PZDetector™ Personal
Price: $49.00 (one-time)
```

After creating, copy the **Price ID**:
```
STRIPE_PRICE_PERSONAL=price_xxxxxxxxxxxx
```

**Product 2: Professional**
```
Name: PZDetector™ Professional
Price: $99.00 (one-time)
```

After creating, copy the **Price ID**:
```
STRIPE_PRICE_PROFESSIONAL=price_xxxxxxxxxxxx
```

> 💡 **Tip:** Use exactly these amounts unless you have pricing research supporting changes.

### 1.4 Create Webhook Endpoint

In Stripe Dashboard → Developers → Webhooks:

```
1. Click → Add Endpoint
2. Endpoint URL: https://YOUR_SITE.netlify.app/.netlify/functions/webhook
3. Events to send:
   - ✅ checkout.session.completed
4. Click → Create Endpoint
5. Copy the Signing Secret:
```

```
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxx
```

---

## 🌐 PHASE 2: Netlify Setup (Day 1-2)

### 2.1 Connect GitHub Repository

```
1. Go to https://app.netlify.com
2. Click → Connect a Git provider → GitHub
3. Authorize Netlify to access GitHub
4. Select repository: pzd-core
5. Click → Deploy
```

### 2.2 Configure Build Settings

Once site created, go to:

```
Netlify Dashboard → Site Settings → Build & Deploy → Build Settings
```

**Verify settings:**

```
Build command: (none - using netlify.toml)
Publish directory: web/
Functions directory: netlify/functions
```

### 2.3 Set Environment Variables

In Netlify Dashboard → Site Settings → Environment Variables:

**Add these variables:**

```
STRIPE_SECRET_KEY = sk_live_xxxxxxxxxxxxxxxxxxxx
STRIPE_PUBLIC_KEY = pk_live_xxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET = whsec_xxxxxxxxxxxxxxxxxxxx
STRIPE_PRICE_PERSONAL = price_xxxxxxxxxxxx
STRIPE_PRICE_PROFESSIONAL = price_xxxxxxxxxxxx
SUPABASE_URL = https://your-project.supabase.co (optional)
SUPABASE_KEY = your-anon-key (optional)
SENDGRID_API_KEY = SG.xxxxxxxxxxxxxxxxxxxx (optional)
EMAIL_FROM = licenses@pzdetector.com (optional)
```

> **Leave SUPABASE_* blank if not using database yet (functions will log to console)**

### 2.4 Fix Stripe Public Key in Frontend

After getting your public key, update the pricing page:

Edit `web/pricing.html` line ~223:

**Find:**
```javascript
const stripe = Stripe(window.STRIPE_PUBLISHABLE_KEY || 'pk_test_YOUR_PUBLISHABLE_KEY_HERE');
```

**Netlify automatically injects via environment variables** - no manual edit needed if set in Step 2.3!

### 2.5 Deploy Site

```
git push origin master
```

Netlify auto-deploys when you push to master. Wait for green checkmark.

Go to: `https://your-site.netlify.app`

---

## ✅ PHASE 3: Testing (Day 2)

### 3.1 Test Checkout Flow

```
1. Go to https://your-site.netlify.app/pricing.html
2. Click "Start 7-Day Trial" on Personal plan
3. Use TEST CARD:
   Card: 4242 4242 4242 4242
   Expiry: 12/34
   CVC: 123
4. Complete payment
5. Check Netlify Functions logs for webhook success
```

**Check Function Logs:**

```
Netlify Dashboard → Functions → webhook → Logs
```

Should see: `[SUCCESS] License created: PZDT-xxxx-xxxx-xxxx-xxxx`

### 3.2 Verify Stripe Webhook Delivery

```
Stripe Dashboard → Developers → Webhooks → [Your Endpoint] → Attempts
```

Should show **successful** delivery for checkout.session.completed

### 3.3 Test License Validation API

From your terminal:

```powershell
# Get a test license key from the logs above
$licenseKey = "PZDT-xxxx-xxxx-xxxx-xxxx"
$deviceId = "test-device-12345"

Invoke-WebRequest -Uri "https://your-site.netlify.app/.netlify/functions/validate-license" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body (@{
    licenseKey = $licenseKey
    deviceId = $deviceId
  } | ConvertTo-Json)
```

Expected response:
```json
{
  "valid": true,
  "plan": "price_personal",
  "devices": 1,
  "email": "customer@example.com"
}
```

### 3.4 Test Desktop App License Activation

```powershell
# On your test machine
cd C:\Users\YourUsername\pzd-core

# Edit app/config.json
# Change: "licenseApiUrl": "https://your-site.netlify.app"

# Run app
python -u app/main.py
```

In app → License & Trial section:
- Click "Activate License"
- Paste test license key
- Should activate successfully

### 3.5 Test Desktop App Support Submission

In app → License & Trial section:
- Click "Contact Support"
- Fill form:
  - Email: your@email.com
  - Subject: "Test support ticket"
  - Description: "This is a test support request"
- Click "Submit"
- Should show: "Ticket #12345 created!"

Check Zendesk Dashboard → Should see new ticket within 2 seconds

### 3.6 Test Support Email Routing

Send email to `support@pzdetector.com`:

```
To: support@pzdetector.com
Subject: Test Email Support
Body: This is a test support email
```

Check Zendesk → New ticket should auto-create within 5 seconds

---

## 🔐 PHASE 4: Security Check (Day 2)

### 4.1 Verify No Secrets in Git

```powershell
# Check if any secrets leaked
git log -p | Select-String "sk_" -Context 5

# Check environment files
git ls-files | grep .env
git ls-files | grep secret
git ls-files | grep key
```

Should return nothing. If it does:

```powershell
# Immediately revoke compromised keys in Stripe
# Then rotate all keys
```

### 4.2 Check .gitignore Coverage

```powershell
# Verify sensitive files ignored
cat .gitignore | findstr "license"
cat .gitignore | findstr ".env"
```

Should include:
```
licenses.json
license.json
device_id
.env
.env.local
```

### 4.3 Verify HTTPS

```powershell
# Your Netlify site automatically gets SSL
curl -I https://your-site.netlify.app
```

Look for:
```
Strict-Transport-Security: max-age=31536000
```

### 4.4 Test Webhook Signature Verification

The webhook handler MUST verify Stripe signatures. Verify in logs:

```
Netlify Dashboard → Functions → webhook → Logs
```

Should NOT see "Webhook signature verification failed" errors

---

## 📧 PHASE 5: Email & Support Setup (Day 2-3)

### 5.1 Set up SendGrid (Optional)

```
1. Go to https://sendgrid.com
2. Sign up free account
3. Go to Settings → API Keys
4. Create API key
5. Copy value: SG.xxxxxxxxxxxxxxxxxxxx
```

Add to Netlify environment variables (see Phase 2.3)

### 5.2 Set Up Zendesk Support (Recommended)

See [ZENDESK_SETUP.md](ZENDESK_SETUP.md) for complete setup guide.

**Quick Setup:**

1. Create Zendesk account: `https://zendesk.com/signup` (Professional plan)
2. Get API credentials from Admin Center → Apps & Extensions → APIs & Extensions → Tokens
3. Add to Netlify environment variables:
   ```
   ZENDESK_SUBDOMAIN = your-subdomain
   ZENDESK_EMAIL = your-email@zendesk.com
   ZENDESK_API_TOKEN = your-api-token
   ZENDESK_LICENSE_FIELD_ID = 123456789 (create custom field first)
   ```
4. Create support email: `support@pzdetector.com` → Forward to Zendesk
5. Enable Help Center: Admin Center → Channels → Help Center
6. Test: Click "Contact Support" in desktop app → Verify ticket in Zendesk

**Features:**
- Auto-ticket creation from desktop app "Contact Support" button
- Email support: support@pzdetector.com → auto-creates tickets
- Help Center portal: `pzdetector.zendesk.com/hc`
- Auto-reply to customers
- Ticket dashboard with SLA tracking

### 5.3 Implement Email Sending (Optional)

Update `netlify/functions/webhook.js`:

**Find the `sendLicenseEmail` function and replace with:**

```javascript
async function sendLicenseEmail(email, licenseKey, plan) {
  const sgMail = require('@sendgrid/mail');
  sgMail.setApiKey(process.env.SENDGRID_API_KEY);
  
  const message = {
    to: email,
    from: process.env.EMAIL_FROM || 'licenses@pzdetector.com',
    subject: 'Your PZDetector™ License Key',
    text: `Your PZDetector™ License Key

Thank you for your purchase!

License Key: ${licenseKey}
Plan: ${plan}

To activate:
1. Open PZDetector™
2. Go to License & Trial section
3. Click "Activate License"
4. Enter: ${licenseKey}

Need help? Click "Contact Support" in the app or email support@pzdetector.com

--
Chair-to-Keyboard™
The Human Centric Software Development Company
`
  };
  
  await sgMail.send(message);
}
```

Add SendGrid to dependencies:

```powershell
# In netlify/functions/package.json, add:
# "@sendgrid/mail": "^7.7.0"
```

---

## 💰 PHASE 6: Financial Setup (Day 3)

### 6.1 Set Up Stripe Payouts

```
Stripe Dashboard → Settings → Payout Schedule
```

- **Recommended:** Daily payouts to your bank account
- Verify bank details are correct
- Review payout fees

### 6.2 Configure Invoicing (Optional)

```
Stripe Dashboard → Billing → Settings
```

Enable automatic invoicing if desired

### 6.3 Set Up Accounting

```
Stripe Dashboard → Developers → Events → Export Guide
```

- Export transaction history for accounting
- Set up bookkeeper access if needed
- You'll want records for taxes (7-year retention required)

---

## 📊 PHASE 7: Monitoring & Analytics (Day 3)

### 7.1 Enable Netlify Analytics

```
Netlify Dashboard → Site Settings → Analytics
```

- Enable Build analytics
- Enable Function analytics
- Enable visitor analytics

### 7.2 Monitor Stripe Dashboard

Daily:
```
Stripe Dashboard → Payments
```

Check:
- Payment volume
- Success rate
- Error messages
- Disputed transactions

### 7.3 Set Up Alerts

```
Stripe Dashboard → Developers → Events → Create Webhook
```

Optional webhook for failures:
```
Events: charge.failed, charge.dispute.created
Endpoint: https://your-monitoring-service.com
```

---

## 🌍 PHASE 8: Domain Setup (Day 3-4)

### 8.1 Point Domain to Netlify

**If using pzdetector.com:**

At your domain registrar (GoDaddy, Namecheap, etc.):

```
DNS Records:

Type: CNAME
Name: www
Value: pzd-core.netlify.com

Type: CNAME
Name: (root/@)
Value: pzd-core.netlify.com
```

Wait 24-48 hours for DNS propagation.

Verify:

```powershell
nslookup pzdetector.com
```

Should show Netlify nameservers

### 8.2 Add Domain to Netlify

```
Netlify Dashboard → Domain Management → Add custom domain
```

1. Add primary domain: pzdetector.com
2. Add www subdomain: www.pzdetector.com
3. Netlify auto-provisions SSL certificate

Verify:
```powershell
curl -I https://pzdetector.com
```

Should get 200 OK with SSL

---

## 📱 PHASE 9: Apps & Integration (Day 4)

### 9.1 Update Desktop App Config

In production:

```python
# app/config.json - BEFORE RELEASE:
{
  "purchaseUrl": "https://pzdetector.com/pricing",
  "licenseApiUrl": "https://pzdetector.com",
  "enableLicenseCheck": true,
  "trialDays": 7
}
```

### 9.2 Package Desktop App Release

```powershell
cd app

# Create executable
pyinstaller --name "PZDetector" `
  --onefile `
  --windowed `
  main.py

# Will create: dist/PZDetector.exe
```

### 9.3 Upload to GitHub Releases

```powershell
# Create git tag
git tag -a v1.0.0 -m "Production release"
git push origin v1.0.0

# Go to GitHub → Releases → Create Release
# Upload: dist/PZDetector.exe
```

---

## ✨ PHASE 10: Launch Checklist (Day 4-5)

### 10.1 Final Website Check

```
[ ] Homepage loads: https://pzdetector.com
[ ] Pricing page loads: https://pzdetector.com/pricing.html
[ ] Success page loads: https://pzdetector.com/success.html
[ ] Navigation links work
[ ] Mobile responsive (test on phone)
[ ] All images load correctly
[ ] No console errors (F12 → Console)
```

### 10.2 Final Payment Flow Check

```powershell
# Test fresh checkout with test card
1. Visit https://pzdetector.com/pricing.html
2. Click "Start 7-Day Trial" (Professional)
3. Complete checkout
4. Verify success page loads
5. Check email for license key
6. Test activation in desktop app
```

### 10.3 Monitoring Setup

```
[ ] Netlify Functions monitoring enabled
[ ] Stripe webhook monitoring enabled
[ ] Zendesk support configured
[ ] Email delivery confirmed (SendGrid or SMTP)
[ ] Error logs accessible
[ ] SSL certificate valid
```

### 10.4 Documentation Review

```
[ ] README.md updated with live links
[ ] LICENSE_GUIDE.md accurate
[ ] STRIPE_SETUP.md complete
[ ] Support email configured (support@pzdetector.com)
```

### 10.5 Social & Marketing (Optional)

```
[ ] Twitter account created
[ ] Product Hunt submission prepared
[ ] HackerNews profile updated with project link
[ ] Reddit communities notified
[ ] Blog post scheduled
```

---

## 🎯 GO/NO-GO DECISION

### ✅ GO if:

```
[ ] All test purchases complete successfully
[ ] License activation works end-to-end
[ ] Support ticket submission working (Zendesk or email)
[ ] All Zendesk integrations configured
[ ] No payment processing errors
[ ] Webhook delivery confirmed
[ ] SSL certificate active
[ ] Domain resolving correctly
[ ] Support email monitored
[ ] Team trained on Zendesk UI
[ ] Backup & recovery plan in place
```

### 🛑 NO-GO if:

```
[ ] Any payment test fails
[ ] Webhook not delivering
[ ] License validation errors
[ ] SSL certificate missing
[ ] Domain not resolving
[ ] Insufficient support coverage
```

---

## 🚀 LAUNCH DAY SCRIPT

**Recommended time:** Early morning, when you can monitor for errors

```powershell
# 1. Final domain check
nslookup pzdetector.com

# 2. Test pricing page
curl -I https://pzdetector.com/pricing.html

# 3. Check Netlify status
# Netlify Dashboard → Overview

# 4. Monitor webhook
#  Stripe Dashboard → Developers → Webhooks

# 5. Announce!
# Send to: team, newsletter, social media, etc.

# 6. Monitor for 24 hours
#  Check Netlify Functions logs
#  Monitor Stripe Dashboard
#  Monitor support email
```

---

## 📞 SUPPORT SETUP

Before launch, prepare:

### Create Support Email Address

```
support@pzdetector.com
```

Configure:
```
[ ] Email forwarding set up (to your email)
[ ] Auto-responder message created
[ ] Support ticket system (optional: Zendesk, Intercom)
[ ] SLA defined (e.g., 24-hour response)
```

### Support Email Template

**Subject:** "Re: Your PZDetector™ Support Request"

**Body:**
```
Hi [Name],

Thank you for contacting PZDetector™ support!

We typically respond within 24 hours. If your issue is urgent:

License Activation Help:
1. Check LICENSE_GUIDE.md on our website
2. Verify your license key format (PZDT-XXXX-XXXX-XXXX-XXXX)
3. Check your internet connection
4. If still stuck, reply with:
   - License key (first 5 chars only, e.g., PZDT-)
   - Your OS version
   - Error message received

We're here to help!

--
PZDetector™ Support
Chair-to-Keyboard™ Inc.
support@pzdetector.com
```

---

## 🔄 Post-Launch Monitoring (Week 1)

### Daily Checks

```powershell
# 1. Check sales
# Stripe Dashboard → Payments

# 2. Check errors
# Netlify Dashboard → Functions → Logs

# 3. Check support email
# Respond to all inquiries

# 4. Check website uptime
# https://www.uptimerobot.com (free monitoring)
```

### Weekly Report Template

```
Week 1 Post-Launch Report
============================

Sales:
[ ] Total revenue: $_______
[ ] Number of conversions: ____
[ ] Avg conversion value: $_______

Technical:
[ ] Uptime: ______%
[ ] Function errors: ____
[ ] Failed webhooks: ____
[ ] Failed payments: ____

Support:
[ ] Emails received: ____
[ ] Avg response time: ____ minutes
[ ] Unresolved issues: ____

Action items:
- [ ] ...
- [ ] ...
```

---

## 🎉 Congratulations!

You're live! 

**Next steps:**
1. Monitor for 24-48 hours
2. Gather customer feedback
3. Plan v1.1 improvements
4. Consider marketing outreach

**Questions?** Email support@pzdetector.com

---

**PZDetector™** by Chair-to-Keyboard™  
*The Human Centric Software Development Company*
