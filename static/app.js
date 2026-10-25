'use strict';
// Delay single-click navigation just enough to recognize a second click.
for (const card of document.querySelectorAll('[data-card]')) {
  let timer;
  let lastClickTime = 0;
  const detail = () => { window.location.assign(card.dataset.eventUrl); };
  card.addEventListener('click', e => {
    if (e.target.closest('button, form')) return;
    if (e.target.closest('a')) e.preventDefault();
    const now = Date.now();
    const quickTap = now - lastClickTime < 310;
    lastClickTime = now;
    if (e.detail >= 2 || quickTap) {
      clearTimeout(timer);
      lastClickTime = 0;
      const form = card.querySelector('.quick-buy-form');
      if (form) form.requestSubmit();
    } else { clearTimeout(timer); timer = setTimeout(detail, 320); }
  });
  card.addEventListener('keydown', e => {
    if (e.target === card && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault(); detail();
    }
  });
}
const checkoutForm = document.getElementById('checkout-form');
const checkoutCancel = document.querySelector('[data-checkout-cancel]');
if (checkoutForm) {
  let leavingIntentionally = false;
  checkoutForm.addEventListener('submit', () => { leavingIntentionally = true; });
  if (checkoutCancel) checkoutCancel.addEventListener('submit', () => { leavingIntentionally = true; });
  window.addEventListener('pagehide', () => {
    if (leavingIntentionally || !navigator.sendBeacon) return;
    const form = document.getElementById('leave-checkout');
    if (form) navigator.sendBeacon(form.action, new FormData(form));
  });
}

if (checkoutForm) {
  const qty = checkoutForm.querySelector('[name="quantity"]');
  const currency = checkoutForm.querySelector('[name="currency"]');
  const preview = document.getElementById('price-preview');
  let requestCounter = 0;
  async function updatePreview() {
    if (!preview) return;
    const current = ++requestCounter;
    const url = new URL(checkoutForm.dataset.quoteUrl, window.location.href);
    url.searchParams.set('quantity', qty.value);
    url.searchParams.set('currency', currency.value);
    try {
      const response = await fetch(url, {credentials:'same-origin'});
      const data = await response.json();
      if (current !== requestCounter) return;
      preview.textContent = response.ok
        ? `Estimated total: ${data.total} (rate ${data.rate}, discount ${data.discount_percent}%)`
        : `Price not available: ${data.error || 'Please check the selection'}`;
    } catch (_error) {
      if (current === requestCounter) preview.textContent = 'Price preview is unavailable; retry checkout.';
    }
  }
  qty.addEventListener('input', updatePreview);
  currency.addEventListener('change', updatePreview);
  updatePreview();
}
