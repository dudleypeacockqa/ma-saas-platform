(function () {
  const mobileMenuButton = document.querySelector('.mobile-menu-button');
  const mobileMenu = document.querySelector('.mobile-menu');

  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
  }

  for (const anchor of document.querySelectorAll('a[href^="#"]')) {
    anchor.addEventListener('click', (event) => {
      event.preventDefault();
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }

  for (const link of document.querySelectorAll('a[href*="signup"]')) {
    link.addEventListener('click', () => {
      if (typeof globalThis.gtag === 'function') {
        globalThis.gtag('event', 'signup_click', {
          event_category: 'engagement',
          event_label: 'header_cta',
        });
      }
    });
  }
})();
