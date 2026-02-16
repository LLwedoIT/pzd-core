# Zendesk Support Integration Setup

**PZDetector™** | *Chair-to-Keyboard™*

Complete guide to configuring Zendesk for customer support with auto-ticket creation from desktop app.

---

## 📋 Overview

This integration enables:
- **Auto-ticket creation** from desktop app support requests
- **Automatic customer tracking** with email & system info
- **Unified support dashboard** in Zendesk
- **24-hour response SLA** tracking
- **Knowledge base** for self-service

---

## 🚀 Part 1: Zendesk Account Setup

### 1.1 Create Zendesk Account

```
https://zendesk.com/signup
```

**Choose:**
- Plan: **Professional** ($55/month, required for webhooks & API)
- Support type: **Email + Chat**

### 1.2 Get API Credentials

Once account created, go to:

```
Zendesk Admin Center → Apps & Integrations → APIs & Extensions → Tokens
```

**Create new token:**

```
Token name: PZDetector Netlify Integration
```

Copy these values:

```
ZENDESK_SUBDOMAIN = your-subdomain (from zendesk URL)
ZENDESK_EMAIL = your-email@company.com (your Zendesk login email)
ZENDESK_API_TOKEN = xxxxxxxxxxxxxxxxxxx
```

**Example:**
```
# If your Zendesk URL is: https://pzdetector.zendesk.com
ZENDESK_SUBDOMAIN = pzdetector
```

### 1.3 Verify API Access

Test connection:

```powershell
$headers = @{
    'Authorization' = 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$env:ZENDESK_EMAIL/token:$env:ZENDESK_API_TOKEN"))
    'Content-Type' = 'application/json'
}

$url = "https://$env:ZENDESK_SUBDOMAIN.zendesk.com/api/v2/users/me.json"

Invoke-WebRequest -Uri $url -Headers $headers
```

Should return your account info (200 OK).

---

## 🎯 Part 2: Zendesk Configuration

### 2.1 Create Support Group

```
Zendesk Admin Center → People → Groups
```

- Group name: **PZDetector Support**
- Description: Customer support for PZDetector™
- Members: Add yourself (and any support team members)

### 2.2 Create Standard Fields

```
Zendesk Admin Center → Objects & Rules → Fields → Tickets
```

Add custom field for license status:

```
Field type: Dropdown
Field name: License Status
Design ID: license_status (auto-filled)
Values:
  - Trial
  - Licensed
  - Premium
```

**Copy the Field ID** (shown after creation):
```
ZENDESK_LICENSE_FIELD_ID = 123456789
```

### 2.3 Create Ticket Form

```
Zendesk Admin Center → Objects & Rules → Ticket Forms
```

Create new form: **PZDetector Support Request**

Include fields:
- Subject (required)
- Description (required)
- License Status (custom field)
- OS Version (custom field - create new)

### 2.4 Create Views

```
Zendesk Admin Center → Account → Views
```

Create view: **Incoming Support Requests**

```
Conditions:
- Status is Open
- Tags contains pzdetector
- Created >= Today

Display: All columns in custom order
```

---

## 🔗 Part 3: Netlify Integration

### 3.1 Add Zendesk Env Vars to Netlify

```
Netlify Dashboard → Site Settings → Environment Variables
```

Add:
```
ZENDESK_SUBDOMAIN = your-zendesk-subdomain
ZENDESK_EMAIL = your-email@zendesk.com
ZENDESK_API_TOKEN = your-api-token
ZENDESK_LICENSE_FIELD_ID = 123456789 (from Part 2.2)
```

### 3.2 Deploy Function

The `create-support-ticket.js` function is ready. Just push to GitHub:

```powershell
git add .
git commit -m "feat: Add Zendesk support integration"
git push origin master
```

Netlify auto-deploys. Verify:

```
Netlify Dashboard → Functions → create-support-ticket → Logs
```

Should show: "Function deployed successfully"

### 3.3 Test Function

```powershell
# Test creating a support ticket via API
$body = @{
    email = "test@example.com"
    subject = "Can't activate license"
    description = "Getting error when trying to activate my license key"
    licenseKey = "PZDT-xxxx-xxxx-xxxx-xxxx"
    osVersion = "Windows 10 Home"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://your-site.netlify.app/.netlify/functions/create-support-ticket" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

Response should include:
```json
{
  "success": true,
  "ticketId": 12345,
  "message": "Support ticket #12345 created. We'll respond within 24 hours."
}
```

Check Zendesk - new ticket should appear immediately.

---

## 💻 Part 4: Desktop App Integration

The desktop app includes a **Support** button that sends requests to the Netlify function.

### 4.1 Configure Desktop App

Edit `app/config.json`:

```json
{
  "purchaseUrl": "https://pzdetector.com/pricing",
  "licenseApiUrl": "https://your-site.netlify.app",
  "supportApiUrl": "https://your-site.netlify.app",
  "enableLicenseCheck": true,
  "trialDays": 7
}
```

### 4.2 Support UI Flow

When user clicks "Contact Support" in app:

1. Dialog opens with fields:
   - Subject (dropdown menu)
   - Description (text area)
2. Auto-fills:
   - User email (from license or asks)
   - OS version (auto-detected)
   - License key status
3. Submits to `create-support-ticket` function
4. Returns ticket number to user

User sees:
```
✓ Support ticket #12345 created!
Your issue has been logged. We'll respond within 24 hours.
```

---

## 📧 Part 5: Support Channel Setup

### 5.1 Create Support Email Address

```
support@pzdetector.com → Zendesk Email Address
```

**In Zendesk:**

```
Admin Center → Channels → Email
```

Add support email:
```
Address: support@pzdetector.com
```

All incoming emails automatically create tickets.

### 5.2 Create Support Portal

```
Zendesk Admin Center → Channels → Help Center
```

Enable Help Center:
```
Portal name: PZDetector Support
```

Customers can:
- Create account
- View ticket status
- Search knowledge base
- Submit feedback

Portal URL: `https://pzdetector.zendesk.com/hc`

### 5.3 Create Knowledge Base Articles

```
Zendesk Help Center → Categories
```

Create category: **Getting Started**

Articles:
- License activation guide
- System requirements
- Common errors
- FAQ

Link to from: `web/index.html` → "Help" section

---

## 🤖 Part 6: Automation Rules

### 6.1 Auto-Reply to Customers

```
Zendesk Admin Center → Objects & Rules → Business Rules → Triggers
```

Create trigger: **Confirm Ticket Receipt**

```
Conditions:
- Ticket is created
- Tags contains pzdetector

Actions:
- Send email to requester
```

Template:
```
Subject: Your support ticket #{{ticket.id}} has been received

Hi {{ticket.requester.name}},

Thank you for contacting PZDetector™ support!

We've received your ticket #{{ticket.id}} and will respond within 24 hours.

In the meantime, you might find helpful answers in our knowledge base:
https://pzdetector.zendesk.com/hc/en-us

Best regards,
PZDetector™ Support Team
Chair-to-Keyboard™
```

### 6.2 Notify Support Team

```
Zendesk Admin Center → Objects & Rules → Business Rules → Triggers
```

Create trigger: **Notify Support on New Tickets**

```
Conditions:
- Ticket is created
- Tags contains pzdetector

Actions:
- Send email to group: PZDetector Support
```

---

## 📊 Part 7: Reporting & Metrics

### 7.1 Create Support Dashboard

```
Zendesk Admin Center → Reports → Dashboard
```

Add widgets:

**Ticket Volume**
```
- Tickets created this week
- Tickets created this month
- Avg resolution time
```

**Response Performance**
```
- Average first response time
- SLA compliance %
- Resolution time trend
```

**Top Issues**
```
- Most common keywords
- Most tagged issues
- Most reopened tickets
```

### 7.2 Export for Analysis

```
Zendesk Admin Center → Reports → Exports
```

Export weekly:
- Ticket list (all open tickets)
- Customer satisfaction (CSAT)
- Agent productivity

Use for: identifying common issues, prioritizing fixes

---

## 🔒 Part 8: Security & Best Practices

### 8.1 API Token Security

```
. Never commit API token to GitHub
. Store only in Netlify environment variables
. Rotate token every 90 days
. Remove old tokens from integrations
```

### 8.2 Data Privacy

```
. Obscure license keys in Zendesk tickets (show only first 5 chars)
. Don't store customer data longer than 180 days
. Enable GDPR-compliant data deletion
```

In Zendesk:
```
Admin Center → Account → Data Privacy
- Enable: "Delete customer data on request"
- Enable: "Anonymize closed tickets after 180 days"
```

### 8.3 Access Control

```
Admin Center → People → Agents
```

Limit access:
```
Support Agents:
- View/edit PZDetector tickets only
- Cannot access organization settings
- Cannot reset customer passwords
```

---

## 🧪 Testing Checklist

Before going live:

```
[ ] API credentials working (Part 1.3)
[ ] Support group created (Part 2.1)
[ ] License field created (Part 2.2)
[ ] Env vars in Netlify (Part 3.1)
[ ] Function deployed (Part 3.2)
[ ] Function test successful (Part 3.3)
[ ] Support email receiving (Part 5.1)
[ ] Help Center accessible (Part 5.2)
[ ] Auto-reply trigger working (Part 6.1)
[ ] Dashboard displaying (Part 7.1)
[ ] Desktop app submitting tickets (Part 4)
```

Test ticket creation:
```powersh
# Submit test ticket from desktop app
# Or via API (see Part 3.3)

# Verify in Zendesk:
1. Zendesk Dashboard → Incoming tickets
2. Should see new ticket within 2 seconds
3. Requester email should be auto-filled
4. License field should be populated
```

---

## 🚀 Go-Live Checklist

From [GO_LIVE_CHECKLIST.md](GO_LIVE_CHECKLIST.md) Phase 5:

```
[ ] Zendesk account created & verified
[ ] API credentials in Netlify env vars
[ ] Support group configured
[ ] Custom fields created
[ ] Help Center live
[ ] Automation rules active
[ ] Desktop app support button working
[ ] Support email address configured
[ ] Test ticket created successfully
[ ] Dashboard accessible
[ ] Team trained on Zendesk UI
```

---

## 📞 Support Workflows

### Workflow 1: Desktop App Support Request

```
User clicks "Contact Support" in app
           ↓
Support dialog opens (pre-fills email, OS, license status)
           ↓
User enters: Subject & Description
           ↓
Submits → Netlify function: create-support-ticket
           ↓
Function creates Zendesk ticket
           ↓
Auto-reply sent to customer email
           ↓
Support team sees ticket in dashboard
           ↓
Agent responds (via Zendesk or email)
           ↓
Customer sees update in email or support portal
```

### Workflow 2: Email Support Request

```
Customer emails: support@pzdetector.com
           ↓
Email auto-forwarded to Zendesk
           ↓
Ticket created automatically
           ↓
Auto-reply sent
           ↓
Support team sees ticket
           ↓
Agent investigates & responds
           ↓
Customer gets response via email
```

### Workflow 3: Help Center Self-Service

```
Customer visits: pzdetector.zendesk.com/hc
           ↓
Searches for issue (e.g., "license activation")
           ↓
Finds article with solution
           ↓
Problem resolved without ticket creation
           ↓
Improved customer satisfaction & reduced support load
```

---

## 💡 Performance Targets

Set these SLAs in Zendesk:

```
First Response: 4 hours
Resolution Target: 24 hours
Re-open %: < 5%
Customer Satisfaction: > 85%
```

Review weekly in dashboard and adjust if needed.

---

## Troubleshooting

### Function not creating tickets

```powershell
# Check Netlify function logs
Netlify Dashboard → Functions → create-support-ticket → Logs

# Look for error messages:
# "Unauthorized" → Check API token
# "Invalid subdomain" → Check ZENDESK_SUBDOMAIN env var
# "Missing field" → Check email/subject/description
```

### Tickets not appearing in Zendesk

```
Check:
1. Zendesk email address configured (Part 5.1)
2. API token has access to tickets.create permission
3. Function logs show [SUCCESS] message
4. Check Zendesk Views for hidden tickets
```

### Auto-reply not sending

```
Admin Center → Objects & Rules → Business Rules → Triggers
- Verify trigger is "Active"
- Check condition matches incoming tickets
- Test trigger manually on existing ticket
```

---

## Next Steps

1. **Set up Help Center content** (articles for common issues)
2. **Configure email templates** (customize responses)
3. **Train team on Zendesk** (use, automation, reporting)
4. **Monitor metrics** (weekly dashboard review)
5. **Gather customer feedback** (improve articles based on support patterns)

---

**Questions? See [GO_LIVE_CHECKLIST.md](GO_LIVE_CHECKLIST.md) Phase 5 or email support@pzdetector.com**
