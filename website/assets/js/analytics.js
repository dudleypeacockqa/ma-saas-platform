(function () {
  const script = document.currentScript;
  const measurementId = script?.dataset.measurementId || 'GA_MEASUREMENT_ID';

  globalThis.dataLayer = globalThis.dataLayer || [];
  function gtag() {
    globalThis.dataLayer.push(arguments);
  }

  globalThis.gtag = globalThis.gtag || gtag;
  globalThis.gtag('js', new Date());
  globalThis.gtag('config', measurementId);
})();
