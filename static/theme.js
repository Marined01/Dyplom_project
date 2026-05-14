(function () {
  function label(theme) {
    return theme === "dark"
      ? "Увімкнути світлу тему"
      : "Увімкнути темну тему";
  }

  function syncButtons() {
    var theme =
      document.documentElement.getAttribute("data-theme") === "dark"
        ? "dark"
        : "light";
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      btn.setAttribute("aria-label", label(theme));
      btn.setAttribute("title", label(theme));
    });
  }

  function toggle() {
    var root = document.documentElement;
    var next =
      root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {
      localStorage.setItem("theme", next);
    } catch (e) {
      /* ignore */
    }
    syncButtons();
  }

  function init() {
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      btn.addEventListener("click", toggle);
    });
    syncButtons();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
