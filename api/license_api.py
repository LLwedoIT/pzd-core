"""
Stripe Webhook Handler for PZDetector™ License Purchases

This service handles Stripe webhook events to generate and deliver license keys.
Run as a lightweight Flask API alongside your static site (Netlify Functions or standalone).
"""

import os
import json
import hmac
import hashlib
import secrets
from datetime import datetime
from typing import Optional
from pathlib import Path

try:
    from flask import Flask, request, jsonify
    import stripe
except ImportError:
    print("Missing dependencies. Install: pip install flask stripe")
    exit(1)

app = Flask(__name__)

# Configuration from environment variables
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRICE_PERSONAL = os.getenv("STRIPE_PRICE_PERSONAL", "price_personal")
STRIPE_PRICE_PROFESSIONAL = os.getenv("STRIPE_PRICE_PROFESSIONAL", "price_professional")

stripe.api_key = STRIPE_SECRET_KEY

# Simple JSON database (replace with real DB for production)
LICENSE_DB = Path("licenses.json")


def load_licenses():
    """Load licenses from JSON file."""
    if LICENSE_DB.exists():
        with open(LICENSE_DB, "r") as f:
            return json.load(f)
    return {}


def save_licenses(licenses):
    """Save licenses to JSON file."""
    with open(LICENSE_DB, "w") as f:
        json.dump(licenses, f, indent=2)


def generate_license_key() -> str:
    """Generate a cryptographically secure license key."""
    # Format: PZDT-XXXX-XXXX-XXXX-XXXX
    parts = []
    for _ in range(4):
        part = secrets.token_hex(2).upper()
        parts.append(part)
    return f"PZDT-{'-'.join(parts)}"


def create_license(customer_email: str, plan: str, devices: int = 1) -> dict:
    """Create a new license record."""
    license_key = generate_license_key()
    
    license_data = {
        "key": license_key,
        "email": customer_email,
        "plan": plan,
        "devices": devices,
        "created": datetime.utcnow().isoformat(),
        "active": True,
        "activations": []
    }
    
    licenses = load_licenses()
    licenses[license_key] = license_data
    save_licenses(licenses)
    
    return license_data


def send_license_email(email: str, license_key: str, plan: str):
    """
    Send license key via email (implement with SendGrid, AWS SES, etc.)
    For now, just log it.
    """
    print(f"[EMAIL] To: {email}")
    print(f"[EMAIL] Subject: Your PZDetector™ License Key")
    print(f"[EMAIL] License: {license_key}")
    print(f"[EMAIL] Plan: {plan}")
    # TODO: Implement actual email sending


@app.route("/api/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """Create a Stripe Checkout session."""
    try:
        data = request.json
        price_id = data.get("priceId")
        
        # Map frontend price IDs to Stripe Price IDs
        price_map = {
            "price_personal": STRIPE_PRICE_PERSONAL,
            "price_professional": STRIPE_PRICE_PROFESSIONAL,
        }
        
        stripe_price_id = price_map.get(price_id)
        if not stripe_price_id:
            return jsonify({"error": "Invalid price ID"}), 400
        
        # Create Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": stripe_price_id,
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://pzdetector.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://pzdetector.com/pricing",
            metadata={
                "plan": price_id
            }
        )
        
        return jsonify({"id": session.id})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/webhook", methods=["POST"])
def webhook():
    """Handle Stripe webhook events."""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # Extract customer info
        customer_email = session.get("customer_details", {}).get("email")
        plan = session.get("metadata", {}).get("plan", "unknown")
        
        # Determine device count based on plan
        devices = 1 if plan == "price_personal" else 3
        
        # Generate and save license
        license_data = create_license(customer_email, plan, devices)
        
        # Send license key to customer
        send_license_email(customer_email, license_data["key"], plan)
        
        print(f"[SUCCESS] License created: {license_data['key']} for {customer_email}")
    
    return jsonify({"status": "success"})


@app.route("/api/validate-license", methods=["POST"])
def validate_license():
    """Validate a license key from the desktop app."""
    try:
        data = request.json
        license_key = data.get("licenseKey")
        device_id = data.get("deviceId")
        
        if not license_key or not device_id:
            return jsonify({"valid": False, "error": "Missing parameters"}), 400
        
        licenses = load_licenses()
        license_data = licenses.get(license_key)
        
        if not license_data:
            return jsonify({"valid": False, "error": "Invalid license key"}), 404
        
        if not license_data.get("active"):
            return jsonify({"valid": False, "error": "License deactivated"}), 403
        
        # Check device limit
        activations = license_data.get("activations", [])
        max_devices = license_data.get("devices", 1)
        
        if device_id not in activations:
            if len(activations) >= max_devices:
                return jsonify({
                    "valid": False,
                    "error": f"Device limit reached ({max_devices} devices)"
                }), 403
            
            # Add new activation
            activations.append(device_id)
            license_data["activations"] = activations
            licenses[license_key] = license_data
            save_licenses(licenses)
        
        return jsonify({
            "valid": True,
            "plan": license_data.get("plan"),
            "devices": license_data.get("devices"),
            "email": license_data.get("email")
        })
    
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "pzdetector-license-api"})


if __name__ == "__main__":
    # Check for required environment variables
    if not STRIPE_SECRET_KEY:
        print("ERROR: STRIPE_SECRET_KEY environment variable not set")
        exit(1)
    
    if not STRIPE_WEBHOOK_SECRET:
        print("WARNING: STRIPE_WEBHOOK_SECRET not set - webhooks will fail")
    
    print("🚀 PZDetector™ License API starting...")
    print(f"📦 License database: {LICENSE_DB.absolute()}")
    
    # Run Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)
