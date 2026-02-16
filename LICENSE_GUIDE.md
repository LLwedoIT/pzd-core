# License Activation & Management Guide

**PZDetector™** by Chair-to-Keyboard™

Complete guide for activating and managing your PZDetector™ license.

---

## Overview

PZDetector™ uses a **7-day trial + one-time purchase** license model:

- **Trial Period:** 7 days full-featured access (no credit card required)
- **Purchase:** One-time payment for  lifetime access
- **Activation:** Enter license key received via email
- **Validation:** Online validation with offline fallback (7-day grace period)

---

## Trial Period

### What You Get

- **Full Feature Access:** All Professional features available during trial
- **7 Days:** Starts from first launch
- **No Limitations:** No feature restrictions during trial
- **No Credit Card:** Trial starts automatically, no payment info needed

### Trial Status

View your trial status in the app:

```
License & Trial Section (bottom of main window)
⏱ Trial Mode - 5 days remaining
```

**Status Colors:**
- **Gray (#888):** 4+ days remaining
- **Yellow (#ffcc00):** 1-3 days remaining  
- **Orange (#ff6600):** Trial expired

---

## Purchasing a License

### Step 1: Choose Your Plan

Click **"Purchase"** button in the app or visit:
https://pzdetector.com/pricing

**Available Plans:**

| Plan | Price | Devices | Features |
|------|-------|---------|----------|
| **Personal** | $49 | 1 | Core PZ detection, Glazed Vision, Process Guardian |
| **Professional** | $99 | 3 | + Network Control, Biometric, Advanced Logging |
| **Enterprise** | Custom | Unlimited | + SSO, AD Deployment, Custom Branding |

### Step 2: Complete Checkout

1. Click "Start 7-Day Trial" on desired plan
2. Enter payment details (via Stripe)
3. Complete purchase

**Test Card (for testing only):**
```
Card: 4242 4242 4242 4242
Expiry: 12/34
CVC: 123
```

### Step 3: Receive License Key

Your license key will be emailed within minutes:

**Format:** `PZDT-XXXX-XXXX-XXXX-XXXX`

**Example:** `PZDT-A3F2-9B7C-1D8E-5K4J`

---

## Activating Your License

### Method 1: In-App Activation (Recommended)

1. **Open PZDetector™**
2. **Scroll to License & Trial section** (bottom of window)
3. **Click "Activate License" button**
4. **Enter your license key** (copy from email)
5. **Click "Activate"**

The app will validate your key online and activate immediately.

**Success Message:**
```
✓ License activated! Plan: Professional
```

### Method 2: Offline Activation

If the app can't reach the license server:

1. Check your internet connection
2. Try again in a few minutes
3. If problem persists, email support@pzdetector.com with:
   - Your license key
   - Error message received
   - Device ID (shown in error if validation fails)

### What Happens After Activation

- ✅ Trial period bypassed
- ✅ Full access to all features (based on plan)
- ✅ License automatically revalidates every 7 days
- ✅ Works offline for up to 7 days between validations
- ✅ Status shows: `✓ Licensed (Professional) - PZDT-A3F2-...`

---

## License Validation

### Online Validation

**When it happens:**
- First activation
- Every 7 days (automatic revalidation)
- When app detects it's been offline >7 days

**What it checks:**
- License key is valid
- Not revoked or refunded
- Device limit not exceeded
- License is active

### Offline Mode

**Grace Period:** 7 days

If you're offline for <7 days:
- App continues working normally
- Uses cached validation
- Will revalidate when back online

If you're offline for >7 days:
- App shows warning but continues working
- Will revalidate when back online
- No data loss or feature restrictions

---

## Device Limits

### Personal Plan (1 Device)

- License key works on **one device** at a time
- To move to a new device:
  1. Uninstall from old device
  2. Install on new device
  3. Activate with same license key
  4. Old device automatically deactivated

### Professional Plan (3 Devices)

- License key works on **up to 3 devices** simultaneously
- Can be your desktop, laptop, and work computer
- All devices use the same license key
- No manual device management needed

### Enterprise Plan (Unlimited Devices)

- No device limits
- Ideal for teams and organizations
- Centralized license management available
- Contact sales@pzdetector.com for setup

---

## Troubleshooting

### "Invalid license key format"

**Cause:** License key doesn't match expected format

**Solution:**
1. Copy key directly from email (don't type manually)
2. Ensure format is: `PZDT-XXXX-XXXX-XXXX-XXXX`
3. Remove any spaces or extra characters
4. Key should be uppercase (app auto-converts)

### "Validation failed: Device limit reached"

**Cause:** License already activated on maximum devices

**Solution:**

**Personal Plan (1 device):**
- Uninstall from other device
- Wait 5 minutes for sync
- Try activation again

**Professional Plan (3 devices):**
- Check which devices are using the license
- Deactivate one by uninstalling PZDetector
- Try activation again

**Need more devices?**
- Upgrade to Professional (3 devices)
- Or purchase additional licenses

### "Cannot reach license server"

**Cause:** Network issue or API temporarily unavailable

**Solution:**
1. **Check internet connection**
2. **Try again in 5 minutes**
3. **Check firewall settings** - Allow api.pzdetector.com
4. **Verify proxy settings** (if on corporate network)
5. **Contact support** if problem persists

**Temporary Workaround:**
- App will continue working for 7 days in offline mode
- Activation can complete later when server is reachable

### "Validation timeout"

**Cause:** Slow connection or server overloaded

**Solution:**
1. Wait 30 seconds
2. Try activation again
3. If persistent, wait 5-10 minutes and retry

### Trial shows expired but I just purchased

**Cause:** License key not yet activated

**Solution:**
1. Click "Activate License"
2. Enter your key from the purchase email
3. If you can't find the email:
   - Check spam folder
   - Search for "PZDetector License"
   - Email support@pzdetector.com with purchase receipt

---

## Managing Your License

### View License Status

**Location:** License & Trial section (bottom of main window)

**Status Examples:**

```
✓ Licensed (Professional) - PZDT-A3F2-...
```
You're all set! License is active.

```
⏱ Trial Mode - 5 days remaining
```
Trial is active. Purchase before it expires.

```
⚠ Trial Expired - Purchase required
```
Trial ended. Purchase to continue using.

### Change License Key

To switch to a different license (e.g., after upgrade):

1. Close PZDetector™
2. Delete license file:
   - Windows: `%APPDATA%\PZDetector\license.json`
   - macOS: `~/Library/Application Support/PZDetector/license.json`
3. Restart PZDetector™
4. Click "Activate License"
5. Enter new license key

### Transfer License to New Device

1. **On old device:** Uninstall PZDetector™
2. **Wait 5 minutes** for license server to sync
3. **On new device:** Install PZDetector™
4. **Activate** with same license key

Device limit automatically updates when old device is removed.

---

## Configuration

### Config Settings

Edit `app/config.json` for advanced options:

```json
{
  "enableLicenseCheck": true,
  "trialDays": 7,
  "purchaseUrl": "https://pzdetector.com/pricing",
  "licenseApiUrl": "https://api.pzdetector.com"
}
```

**Options:**

- `enableLicenseCheck` - Enable/disable license system
- `trialDays` - Trial period length (default: 7)
- `purchaseUrl` - Where "Purchase" button links to
- `licenseApiUrl` - License validation API endpoint

### Disable License Checking (For Testing)

**⚠️ Not recommended for production use**

```json
{
  "enableLicenseCheck": false
}
```

This bypasses all license checks. Only use for:
- Internal testing
- Development
- Special enterprise deployments

---

## Privacy & Security

### What We Store

**On Your Device:**
- License key (encrypted)
- Device ID (hardware-based hash)
- Install date
- Last validation timestamp

**On Our Servers:**
- License key
- Purchase email
- Device IDs (for device limit enforcement)
- Activation timestamps

### What We Don't Store

- ❌ Personal usage data
- ❌ PZ detection data
- ❌ Screenshots or camera feeds
- ❌ Browsing history
- ❌ File system access
- ❌ Any biometric data

### Data Retention

- License data: Lifetime (for ongoing validation)
- Purchase receipts: 7 years (tax compliance)
- Unused data: Deleted after 90 days

### GDPR Compliance

Email privacy@pzdetector.com to:
- Request data export
- Request data deletion
- Update email address
- Opt out of marketing (no marketing by default)

---

## Support

### Common Questions

**Q: Is this a subscription?**  
A: No! One-time purchase, lifetime access. No recurring fees.

**Q: Do I need internet to use PZDetector™?**  
A: Internet required for initial activation and revalidation (every 7 days). Works offline between validations.

**Q: Can I get a refund?**  
A: Yes, 30-day money-back guarantee. Email support@pzdetector.com.

**Q: What if I lose my license key?**  
A: Email support@pzdetector.com with your purchase email address.

**Q: Can I upgrade from Personal to Professional?**  
A: Yes! Email sales@pzdetector.com for upgrade pricing.

**Q: What happens if Chair-to-Keyboard shuts down?**  
A: License validation will continue via cached validation indefinitely. We'll also release a license-free version if we ever discontinue.

### Contact Support

**Email:** support@pzdetector.com  
**Response Time:** Within 24 hours (usually same day)

**Include in your email:**
- License key (if activated)
- Error message (if any)
- OS version (Windows 10/11, macOS version)
- Screenshot of issue (optional but helpful)

**Enterprise Support:** enterprise@pzdetector.com

---

## Updates

### License and Updates

Your license includes all future updates within your major version:

- **v1.x → v1.y:** ✅ Free updates
- **v1.x → v2.x:** May require upgrade (we'll notify you)

**How to Update:**
1. Download latest version from GitHub
2. Install over existing version
3. License automatically carries over
4. No need to reactivate

### Beta Access

Professional and Enterprise licenses include beta access:

1. Join #beta channel on Discord
2. Download beta releases
3. Same license works for stable and beta

---

**Need Help?** Email support@pzdetector.com

**PZDetector™** by Chair-to-Keyboard™  
*The Human Centric Software Development Company*
