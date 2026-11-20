// Propagate the `data-theme` attribute of <html> to <body>
// Needed to fix dark mode handling of sphinx-tabs:
// https://github.com/executablebooks/sphinx-tabs/pull/201
(function () {
  const html = document.documentElement;
  function propagateHtmlDataTheme() {
    const theme = html.getAttribute('data-theme');
    if (theme === null) {
      document.body.removeAttribute('data-theme');
    } else {
      document.body.setAttribute('data-theme', theme);
    }
  }
  document.addEventListener('DOMContentLoaded', function () {
    propagateHtmlDataTheme();
    new MutationObserver(propagateHtmlDataTheme).observe(html, {
      attributes: true,
      attributeFilter: ['data-theme'],
    });
  });
})();
