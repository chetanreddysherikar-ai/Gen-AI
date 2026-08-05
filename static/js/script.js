(function () {
  "use strict";

  const root = document.documentElement;
  const themeBtn = document.getElementById("themeBtn");
  const themeIcon = document.getElementById("themeIcon");

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (themeIcon) {
      themeIcon.className = theme === "light" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
    }
  }

  const savedTheme = window.localStorage.getItem("theme") || "dark";
  applyTheme(savedTheme);

  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      const current = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      applyTheme(current);
      window.localStorage.setItem("theme", current);
    });
  }

  // Show a loading state on any "generate" form so the UI feels responsive
  // while waiting on the Gemini API call.
  document.querySelectorAll("form.generate-form").forEach(function (form) {
    form.addEventListener("submit", function () {
      const btn = form.querySelector("button[type='submit'], button.btn-generate");
      if (btn && !btn.disabled) {
        btn.disabled = true;
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Generating…';
      }
    });
  });

  // Simple show/hide password toggle for any input with a matching
  // [data-toggle-password] button.
  document.querySelectorAll("[data-toggle-password]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const targetId = btn.getAttribute("data-toggle-password");
      const input = document.getElementById(targetId);
      if (!input) return;
      const showing = input.type === "text";
      input.type = showing ? "password" : "text";
      btn.querySelector("i").className = showing ? "bi bi-eye" : "bi bi-eye-slash";
    });
  });
})();

function copyText(elementId) {
  const el = document.getElementById(elementId || "result");
  if (!el) return;
  navigator.clipboard.writeText(el.innerText).then(function () {
    const toastEl = document.getElementById("copyToast");
    if (toastEl && window.bootstrap) {
      new bootstrap.Toast(toastEl).show();
    } else {
      alert("Copied to clipboard!");
    }
  });
}
