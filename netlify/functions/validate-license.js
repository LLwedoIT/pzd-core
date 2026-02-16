/**
 * Netlify Function: Validate License Key
 * 
 * POST /.netlify/functions/validate-license
 * Body: { licenseKey: "PZDT-...", deviceId: "abc123..." }
 */

const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase client
const supabase = process.env.SUPABASE_URL && process.env.SUPABASE_KEY
  ? createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY)
  : null;

exports.handler = async (event, context) => {
  // Only allow POST
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const { licenseKey, deviceId } = JSON.parse(event.body);

    if (!licenseKey || !deviceId) {
      return {
        statusCode: 400,
        body: JSON.stringify({
          valid: false,
          error: 'Missing licenseKey or deviceId'
        })
      };
    }

    if (!supabase) {
      return {
        statusCode: 503,
        body: JSON.stringify({
          valid: false,
          error: 'Database not configured'
        })
      };
    }

    // Look up license in database
    const { data: license, error } = await supabase
      .from('licenses')
      .select('*')
      .eq('key', licenseKey)
      .single();

    if (error || !license) {
      return {
        statusCode: 404,
        body: JSON.stringify({
          valid: false,
          error: 'Invalid license key'
        })
      };
    }

    // Check if license is active
    if (!license.active) {
      return {
        statusCode: 403,
        body: JSON.stringify({
          valid: false,
          error: 'License deactivated'
        })
      };
    }

    // Check device limit
    const activations = license.activations || [];
    const maxDevices = license.devices || 1;

    if (!activations.includes(deviceId)) {
      if (activations.length >= maxDevices) {
        return {
          statusCode: 403,
          body: JSON.stringify({
            valid: false,
            error: `Device limit reached (${maxDevices} devices)`
          })
        };
      }

      // Add new device activation
      const updatedActivations = [...activations, deviceId];
      await supabase
        .from('licenses')
        .update({ activations: updatedActivations })
        .eq('key', licenseKey);
    }

    // Valid license!
    return {
      statusCode: 200,
      body: JSON.stringify({
        valid: true,
        plan: license.plan,
        devices: license.devices,
        email: license.email
      })
    };

  } catch (error) {
    console.error('License validation error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        valid: false,
        error: error.message
      })
    };
  }
};
