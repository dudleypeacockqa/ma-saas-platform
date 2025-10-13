(function () {
  const script = document.currentScript;
  const measurementId = script?.dataset.measurementId || 'GA_MEASUREMENT_ID';

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }

  window.gtag = window.gtag || gtag;
  window.gtag('js', new Date());
  window.gtag('config', measurementId);
})();
