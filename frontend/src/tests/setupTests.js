require('@testing-library/jest-dom');

const { TextEncoder, TextDecoder } = require('util');

if (!global.TextEncoder) {
  global.TextEncoder = TextEncoder;
}

if (!global.TextDecoder) {
  global.TextDecoder = TextDecoder;
}

class ResizeObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe(target) {
    const entry = {
      target,
      contentRect: target && typeof target.getBoundingClientRect === 'function'
        ? target.getBoundingClientRect()
        : { width: (target?.clientWidth || 0), height: (target?.clientHeight || 0) },
    };
    this.callback([entry]);
  }
  unobserve() {}
  disconnect() {}
}

if (!global.ResizeObserver) {
  global.ResizeObserver = ResizeObserver;
}

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: window.matchMedia || ((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })),
});

if (!window.scrollTo) {
  window.scrollTo = () => {};
}

if (!global.structuredClone) {
  global.structuredClone = (value) => JSON.parse(JSON.stringify(value));
}

