/* Viraloop — progressive enhancement only. Everything works without JS. */
(function () {
  'use strict';

  /* Mobile navigation */
  var header = document.querySelector('.header');
  var toggle = document.querySelector('.nav-toggle');
  if (header && toggle) {
    toggle.addEventListener('click', function () {
      var open = header.getAttribute('data-open') === 'true';
      header.setAttribute('data-open', String(!open));
      toggle.setAttribute('aria-expanded', String(!open));
      toggle.setAttribute('aria-label', open ? 'Open menu' : 'Close menu');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.getAttribute('data-open') === 'true') {
        header.setAttribute('data-open', 'false');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  /* Forms: build a mailto: so the site stays backend-free.
     Swap the action for a real endpoint when you have one. */
  document.querySelectorAll('form[data-mailto]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var to = form.getAttribute('action').replace('mailto:', '').split('?')[0];
      var lines = [];
      new FormData(form).forEach(function (value, key) {
        if (key === 'consent') value = 'yes';
        lines.push(key.charAt(0).toUpperCase() + key.slice(1) + ': ' + value);
      });
      var subject = (form.querySelector('h3') || {}).textContent || document.title;
      var href = 'mailto:' + to +
        '?subject=' + encodeURIComponent('Website enquiry — ' + document.title) +
        '&body=' + encodeURIComponent(lines.join('\n'));
      var status = form.querySelector('.form__status');
      if (status) status.textContent = 'Opening your email app…';
      window.location.href = href;
    });
  });

  /* Current year in footers written before the build year */
  var year = String(new Date().getFullYear());
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = year; });
})();
