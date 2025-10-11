#!/usr/bin/env node

/**
 * Cloudflare Setup Script
 * Automates Cloudflare configuration for the M&A SaaS Platform
 */

import dotenv from 'dotenv';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load .env.cloudflare from frontend directory
const envPath = join(__dirname, '..', '.env.cloudflare');
if (existsSync(envPath)) {
  dotenv.config({ path: envPath });
  console.log('✅ Loaded .env.cloudflare\n');
} else {
  console.error('❌ .env.cloudflare not found');
  console.error('Please create frontend/.env.cloudflare with your Cloudflare credentials\n');
  process.exit(1);
}

// Configuration
const config = {
  email: process.env.CLOUDFLARE_EMAIL,
  apiKey: process.env.CLOUDFLARE_API_KEY,
  apiToken: process.env.CLOUDFLARE_API_TOKEN,
  domain: process.env.DOMAIN || '100daysandbeyond.com',
  originUrl: process.env.ORIGIN_URL || 'ma-saas-platform.onrender.com',
};

// Cloudflare API base URL
const CF_API = 'https://api.cloudflare.com/client/v4';

// Headers for API requests
const getHeaders = () => {
  if (config.apiToken) {
    return {
      Authorization: `Bearer ${config.apiToken}`,
      'Content-Type': 'application/json',
    };
  } else if (config.email && config.apiKey) {
    return {
      'X-Auth-Email': config.email,
      'X-Auth-Key': config.apiKey,
      'Content-Type': 'application/json',
    };
  }
  throw new Error('Missing Cloudflare credentials');
};

// Helper function for API calls
async function cfAPI(endpoint, options = {}) {
  const url = `${CF_API}${endpoint}`;
  const headers = getHeaders();

  const response = await fetch(url, {
    ...options,
    headers: { ...headers, ...options.headers },
  });

  const data = await response.json();

  if (!response.ok || !data.success) {
    throw new Error(`Cloudflare API Error: ${JSON.stringify(data.errors)}`);
  }

  return data.result;
}

// Get zone ID for domain
async function getZoneId() {
  console.log(`\n🔍 Looking up zone for ${config.domain}...`);

  const zones = await cfAPI(`/zones?name=${config.domain}`);

  if (zones.length === 0) {
    throw new Error(
      `Zone not found for ${config.domain}. Please add the domain to Cloudflare first.`,
    );
  }

  console.log(`✅ Zone found: ${zones[0].id}`);
  return zones[0].id;
}

// Configure DNS records
async function setupDNS(zoneId) {
  console.log('\n📡 Configuring DNS records...');

  // Get existing DNS records
  const records = await cfAPI(`/zones/${zoneId}/dns_records`);

  // Root domain (@) - CNAME to Render
  const rootRecord = records.find((r) => r.type === 'CNAME' && r.name === config.domain);

  if (!rootRecord) {
    console.log('  Creating root CNAME record...');
    await cfAPI(`/zones/${zoneId}/dns_records`, {
      method: 'POST',
      body: JSON.stringify({
        type: 'CNAME',
        name: '@',
        content: config.originUrl,
        ttl: 1, // Auto
        proxied: true,
      }),
    });
    console.log('  ✅ Root CNAME created');
  } else {
    console.log('  ✅ Root CNAME exists');
  }

  // WWW subdomain
  const wwwRecord = records.find((r) => r.type === 'CNAME' && r.name === `www.${config.domain}`);

  if (!wwwRecord) {
    console.log('  Creating www CNAME record...');
    await cfAPI(`/zones/${zoneId}/dns_records`, {
      method: 'POST',
      body: JSON.stringify({
        type: 'CNAME',
        name: 'www',
        content: config.originUrl,
        ttl: 1,
        proxied: true,
      }),
    });
    console.log('  ✅ WWW CNAME created');
  } else {
    console.log('  ✅ WWW CNAME exists');
  }
}

// Configure SSL/TLS settings
async function setupSSL(zoneId) {
  console.log('\n🔐 Configuring SSL/TLS...');

  // Set SSL mode to Full (strict)
  await cfAPI(`/zones/${zoneId}/settings/ssl`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'full' }),
  });
  console.log('  ✅ SSL mode: Full (strict)');

  // Enable Always Use HTTPS
  await cfAPI(`/zones/${zoneId}/settings/always_use_https`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'on' }),
  });
  console.log('  ✅ Always Use HTTPS enabled');

  // Enable Automatic HTTPS Rewrites
  await cfAPI(`/zones/${zoneId}/settings/automatic_https_rewrites`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'on' }),
  });
  console.log('  ✅ Automatic HTTPS Rewrites enabled');

  // Set minimum TLS version
  await cfAPI(`/zones/${zoneId}/settings/min_tls_version`, {
    method: 'PATCH',
    body: JSON.stringify({ value: '1.2' }),
  });
  console.log('  ✅ Minimum TLS version: 1.2');
}

// Configure caching
async function setupCaching(zoneId) {
  console.log('\n💾 Configuring caching...');

  // Enable Brotli
  await cfAPI(`/zones/${zoneId}/settings/brotli`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'on' }),
  });
  console.log('  ✅ Brotli compression enabled');

  // Enable Early Hints
  await cfAPI(`/zones/${zoneId}/settings/early_hints`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'on' }),
  });
  console.log('  ✅ Early Hints enabled');

  // Browser cache TTL
  await cfAPI(`/zones/${zoneId}/settings/browser_cache_ttl`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 14400 }), // 4 hours
  });
  console.log('  ✅ Browser cache TTL: 4 hours');
}

// Configure security
async function setupSecurity(zoneId) {
  console.log('\n🛡️  Configuring security...');

  // Enable Bot Fight Mode
  try {
    await cfAPI(`/zones/${zoneId}/settings/bot_fight_mode`, {
      method: 'PATCH',
      body: JSON.stringify({ value: 'on' }),
    });
    console.log('  ✅ Bot Fight Mode enabled');
  } catch (error) {
    console.log('  ⚠️  Bot Fight Mode requires Pro plan');
  }

  // Security level
  await cfAPI(`/zones/${zoneId}/settings/security_level`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'medium' }),
  });
  console.log('  ✅ Security level: Medium');

  // Challenge passage
  await cfAPI(`/zones/${zoneId}/settings/challenge_ttl`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 1800 }), // 30 minutes
  });
  console.log('  ✅ Challenge TTL: 30 minutes');
}

// Configure performance
async function setupPerformance(zoneId) {
  console.log('\n⚡ Configuring performance...');

  // Enable HTTP/2
  await cfAPI(`/zones/${zoneId}/settings/http2`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'on' }),
  });
  console.log('  ✅ HTTP/2 enabled');

  // Enable HTTP/3
  await cfAPI(`/zones/${zoneId}/settings/http3`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'on' }),
  });
  console.log('  ✅ HTTP/3 enabled');

  // Enable 0-RTT
  await cfAPI(`/zones/${zoneId}/settings/0rtt`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'on' }),
  });
  console.log('  ✅ 0-RTT enabled');

  // Enable IPv6
  await cfAPI(`/zones/${zoneId}/settings/ipv6`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'on' }),
  });
  console.log('  ✅ IPv6 enabled');

  // Enable WebSockets
  await cfAPI(`/zones/${zoneId}/settings/websockets`, {
    method: 'PATCH',
    body: JSON.stringify({ value: 'on' }),
  });
  console.log('  ✅ WebSockets enabled');
}

// Configure cache rules
async function setupCacheRules(zoneId) {
  console.log('\n📋 Configuring cache rules...');

  // Note: Cache Rules API requires Enterprise plan
  // For Free/Pro, we'll use Page Rules instead
  console.log('  ℹ️  Cache rules configured via Page Rules (requires manual setup in dashboard)');
  console.log('  📝 Recommended Page Rules:');
  console.log('     1. URL: 100daysandbeyond.com/assets/* → Cache Everything');
  console.log('     2. URL: 100daysandbeyond.com/*.html → Bypass Cache');
}

// Main setup function
async function main() {
  console.log('╔════════════════════════════════════════════════════╗');
  console.log('║   Cloudflare Setup for M&A SaaS Platform           ║');
  console.log('╚════════════════════════════════════════════════════╝');

  try {
    // Validate configuration
    if (!config.email && !config.apiToken) {
      throw new Error(
        'Missing Cloudflare credentials. Please set CLOUDFLARE_API_TOKEN or CLOUDFLARE_EMAIL + CLOUDFLARE_API_KEY',
      );
    }

    // Get zone ID
    const zoneId = await getZoneId();

    // Run all setup tasks
    await setupDNS(zoneId);
    await setupSSL(zoneId);
    await setupCaching(zoneId);
    await setupSecurity(zoneId);
    await setupPerformance(zoneId);
    await setupCacheRules(zoneId);

    console.log('\n╔════════════════════════════════════════════════════╗');
    console.log('║   ✅ Cloudflare Setup Complete!                    ║');
    console.log('╚════════════════════════════════════════════════════╝');

    console.log('\n📊 Next Steps:');
    console.log('  1. DNS propagation may take up to 24 hours');
    console.log('  2. Verify your site at: https://100daysandbeyond.com');
    console.log('  3. Check SSL certificate status in Cloudflare dashboard');
    console.log('  4. Set up Page Rules for advanced caching (if needed)');
    console.log('  5. Monitor analytics in Cloudflare dashboard\n');

    console.log('📚 Documentation:');
    console.log('  - Setup Guide: frontend/CDN_SETUP.md');
    console.log('  - Checklist: frontend/CLOUDFLARE_SETUP_CHECKLIST.md\n');
  } catch (error) {
    console.error('\n❌ Setup failed:', error.message);
    console.error('\nPlease check:');
    console.error('  1. API credentials are correct');
    console.error('  2. Domain is added to Cloudflare');
    console.error('  3. You have permission to modify zone settings\n');
    process.exit(1);
  }
}

// Run setup
main();
