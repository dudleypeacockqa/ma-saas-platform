/**
 * Application Entry Point
 * Renders the React application to the DOM
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import * as Sentry from '@sentry/react';
import App from './App';

// Import global styles
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';

const sentryDsn = import.meta.env.VITE_SENTRY_DSN;

if (sentryDsn) {
  Sentry.init({
    dsn: sentryDsn,
    environment:
      import.meta.env.VITE_ENVIRONMENT ?? import.meta.env.MODE ?? 'development',
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllInputs: true,
        blockAllMedia: true,
      }),
    ],
    tracesSampleRate: Number(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE ?? 0.1),
    replaysSessionSampleRate: Number(
      import.meta.env.VITE_SENTRY_REPLAY_SAMPLE_RATE ?? 0.1,
    ),
    replaysOnErrorSampleRate: 1.0,
  });
}

// Create root element
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

// Render application
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
