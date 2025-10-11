/**
 * Application Entry Point
 * Renders the React application to the DOM
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Import global styles
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';

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