import express from 'express';
import compression from 'compression';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 10000;
const distPath = join(__dirname, 'dist');

// APM Metrics Storage
const metrics = {
  requests: {
    total: 0,
    byStatus: {},
    byPath: {},
  },
  performance: {
    avgResponseTime: 0,
    maxResponseTime: 0,
    minResponseTime: Infinity,
  },
  errors: [],
  startTime: Date.now(),
  alerts: {
    lastAlertTime: 0,
    alertCooldown: 5 * 60 * 1000, // 5 minutes
  },
};

// Performance Budgets and Thresholds
const performanceBudgets = {
  maxResponseTime: 1000, // 1 second
  errorRateThreshold: 5, // 5% error rate
  memoryThreshold: 500 * 1024 * 1024, // 500 MB
  minUptime: 60 * 60 * 1000, // 1 hour
};

// Alert function
async function sendAlert(type, message, data = {}) {
  const now = Date.now();

  // Cooldown to prevent alert spam
  if (now - metrics.alerts.lastAlertTime < metrics.alerts.alertCooldown) {
    return;
  }

  metrics.alerts.lastAlertTime = now;

  const alertPayload = {
    type,
    message,
    data,
    timestamp: new Date().toISOString(),
    service: 'ma-saas-platform-frontend',
  };

  console.error('🚨 ALERT:', type, message, data);

  // Webhook alerting (Slack, Discord, etc.)
  if (process.env.ALERT_WEBHOOK_URL) {
    try {
      const response = await fetch(process.env.ALERT_WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: `🚨 *${type}*: ${message}`,
          attachments: [
            {
              color: type === 'error' ? 'danger' : 'warning',
              fields: Object.entries(data).map(([key, value]) => ({
                title: key,
                value: String(value),
                short: true,
              })),
              footer: 'M&A SaaS Platform',
              ts: Math.floor(Date.now() / 1000),
            },
          ],
        }),
      });

      if (!response.ok) {
        console.error('Failed to send webhook alert:', await response.text());
      }
    } catch (error) {
      console.error('Failed to send alert:', error);
    }
  }

  // Email alerting (using backend API)
  if (process.env.BACKEND_API_URL && process.env.ALERT_EMAIL) {
    try {
      await fetch(`${process.env.BACKEND_API_URL}/api/internal/alert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...alertPayload,
          email: process.env.ALERT_EMAIL,
        }),
      });
    } catch (error) {
      console.error('Failed to send email alert:', error);
    }
  }
}

// Check performance budgets
function checkPerformanceBudgets() {
  const errorRate = (metrics.errors.length / metrics.requests.total) * 100;

  // Check error rate
  if (errorRate > performanceBudgets.errorRateThreshold) {
    sendAlert('High Error Rate', `Error rate is ${errorRate.toFixed(2)}%`, {
      threshold: `${performanceBudgets.errorRateThreshold}%`,
      current: `${errorRate.toFixed(2)}%`,
      totalErrors: metrics.errors.length,
      totalRequests: metrics.requests.total,
    });
  }

  // Check response time
  if (metrics.performance.maxResponseTime > performanceBudgets.maxResponseTime) {
    sendAlert('Slow Response Time', 'Maximum response time exceeded budget', {
      threshold: `${performanceBudgets.maxResponseTime}ms`,
      current: `${metrics.performance.maxResponseTime}ms`,
      average: `${metrics.performance.avgResponseTime.toFixed(2)}ms`,
    });
  }

  // Check memory usage
  const memUsage = process.memoryUsage();
  if (memUsage.heapUsed > performanceBudgets.memoryThreshold) {
    sendAlert('High Memory Usage', 'Heap memory usage exceeded threshold', {
      threshold: `${(performanceBudgets.memoryThreshold / 1024 / 1024).toFixed(2)} MB`,
      current: `${(memUsage.heapUsed / 1024 / 1024).toFixed(2)} MB`,
      rss: `${(memUsage.rss / 1024 / 1024).toFixed(2)} MB`,
    });
  }
}

// Trust proxy for rate limiting behind Render's load balancer
app.set('trust proxy', 1);

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // limit each IP to 1000 requests per windowMs
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
  message: { error: 'Too many requests, please try again later.' },
  skip: (req) => req.path === '/health', // Don't rate limit health checks
});

app.use(limiter);

// Security headers with Helmet
app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: [
          "'self'",
          "'unsafe-inline'",
          'https://clerk.com',
          'https://*.clerk.accounts.dev',
        ],
        styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
        fontSrc: ["'self'", 'https://fonts.gstatic.com'],
        imgSrc: ["'self'", 'data:', 'https:', 'blob:'],
        connectSrc: [
          "'self'",
          'https://api.100daysandbeyond.com',
          'https://clerk.com',
          'https://*.clerk.accounts.dev',
        ],
        frameSrc: ["'self'", 'https://clerk.com', 'https://*.clerk.accounts.dev'],
      },
    },
    crossOriginEmbedderPolicy: false,
  }),
);

// Gzip compression
app.use(compression());

// CDN-ready headers
app.use((req, res, next) => {
  // Add timing header for monitoring
  res.setHeader('X-Response-Time', Date.now().toString());

  // Add CDN cache headers
  if (req.path.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$/)) {
    res.setHeader('CDN-Cache-Control', 'public, max-age=31536000, immutable');
  }

  next();
});

// APM Middleware - Request tracking and analytics
app.use((req, res, next) => {
  const start = Date.now();

  // Track request
  metrics.requests.total++;

  res.on('finish', () => {
    const duration = Date.now() - start;

    // Update performance metrics
    metrics.performance.avgResponseTime =
      (metrics.performance.avgResponseTime * (metrics.requests.total - 1) + duration) /
      metrics.requests.total;
    metrics.performance.maxResponseTime = Math.max(metrics.performance.maxResponseTime, duration);
    metrics.performance.minResponseTime = Math.min(metrics.performance.minResponseTime, duration);

    // Track by status code
    const statusKey = `${Math.floor(res.statusCode / 100)}xx`;
    metrics.requests.byStatus[statusKey] = (metrics.requests.byStatus[statusKey] || 0) + 1;

    // Track by path (top 20 only)
    const pathKey = req.path === '/' ? 'root' : req.path.split('/')[1] || 'unknown';
    metrics.requests.byPath[pathKey] = (metrics.requests.byPath[pathKey] || 0) + 1;

    // Log request
    const logLevel = res.statusCode >= 400 ? '❌' : res.statusCode >= 300 ? '⚠️' : '✅';
    console.log(
      `${logLevel} ${req.method} ${req.path} ${res.statusCode} ${duration}ms [${req.ip}]`,
    );

    // Track errors
    if (res.statusCode >= 500) {
      metrics.errors.push({
        path: req.path,
        method: req.method,
        status: res.statusCode,
        timestamp: new Date().toISOString(),
        ip: req.ip,
      });
      // Keep only last 100 errors
      if (metrics.errors.length > 100) {
        metrics.errors.shift();
      }

      // Check performance budgets on every error
      checkPerformanceBudgets();
    }
  });

  next();
});

// Serve static files with caching headers
app.use(
  express.static(distPath, {
    maxAge: '1y',
    immutable: true,
    setHeaders: (res, path) => {
      // Don't cache HTML files
      if (path.endsWith('.html')) {
        res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
      }
    },
  }),
);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
  });
});

// Metrics endpoint for APM monitoring
app.get('/metrics', (req, res) => {
  const uptimeSeconds = Math.floor((Date.now() - metrics.startTime) / 1000);

  res.status(200).json({
    timestamp: new Date().toISOString(),
    uptime: {
      seconds: uptimeSeconds,
      human: `${Math.floor(uptimeSeconds / 3600)}h ${Math.floor((uptimeSeconds % 3600) / 60)}m ${uptimeSeconds % 60}s`,
    },
    requests: {
      total: metrics.requests.total,
      byStatus: metrics.requests.byStatus,
      topPaths: Object.entries(metrics.requests.byPath)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .reduce((obj, [key, val]) => ({ ...obj, [key]: val }), {}),
    },
    performance: {
      avgResponseTime: Math.round(metrics.performance.avgResponseTime * 100) / 100,
      maxResponseTime: metrics.performance.maxResponseTime,
      minResponseTime:
        metrics.performance.minResponseTime === Infinity ? 0 : metrics.performance.minResponseTime,
    },
    errors: {
      count: metrics.errors.length,
      recent: metrics.errors.slice(-10),
    },
    memory: process.memoryUsage(),
    cpu: process.cpuUsage(),
  });
});

// Analytics endpoint (for client-side events)
app.post('/api/analytics', express.json(), (req, res) => {
  const { event, data } = req.body;

  // Log analytics event
  console.log(`📊 Analytics: ${event}`, {
    timestamp: new Date().toISOString(),
    ip: req.ip,
    userAgent: req.get('user-agent'),
    data,
  });

  res.status(200).json({ success: true });
});

// SPA fallback - all routes serve index.html
app.get('*', (req, res) => {
  const indexPath = join(distPath, 'index.html');
  if (existsSync(indexPath)) {
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.sendFile(indexPath);
  } else {
    res.status(503).json({
      error: 'Service Unavailable',
      message: 'Application is being deployed',
    });
  }
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'production' ? 'Something went wrong' : err.message,
  });
});

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ Frontend server running on port ${PORT}`);
  console.log(`📁 Serving from: ${distPath}`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing server gracefully...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
