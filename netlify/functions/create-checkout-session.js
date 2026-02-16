/**
 * Netlify Function: Create Stripe Checkout Session
 * 
 * POST /.netlify/functions/create-checkout-session
 * Body: { priceId: "price_personal" | "price_professional" }
 */

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event, context) => {
  // Only allow POST
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const { priceId } = JSON.parse(event.body);

    // Map frontend price IDs to Stripe Price IDs
    const priceMap = {
      'price_personal': process.env.STRIPE_PRICE_PERSONAL,
      'price_professional': process.env.STRIPE_PRICE_PROFESSIONAL,
    };

    const stripePriceId = priceMap[priceId];
    if (!stripePriceId) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Invalid price ID' })
      };
    }

    // Create Checkout Session
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [{
        price: stripePriceId,
        quantity: 1,
      }],
      mode: 'payment',
      success_url: `${process.env.URL}/success.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.URL}/pricing.html`,
      metadata: {
        plan: priceId
      }
    });

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id: session.id })
    };

  } catch (error) {
    console.error('Checkout session creation error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
