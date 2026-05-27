(function () {
  var mq = window.matchMedia("(max-width: 720px)");

  function nav() {
    return document.getElementById("site-nav");
  }

  function toggle() {
    return document.querySelector(".nav-toggle");
  }

  function setOpen(open) {
    var el = nav();
    var btn = toggle();
    if (!el || !btn) {
      return;
    }
    el.classList.toggle("site-nav--open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    btn.setAttribute("aria-label", open ? "Закрити меню" : "Відкрити меню");
    document.body.classList.toggle("nav-open", open);
  }

  function close() {
    setOpen(false);
  }

  function onResize() {
    if (!mq.matches) {
      close();
    }
  }

  function init() {
    var btn = toggle();
    var el = nav();
    if (!btn || !el) {
      return;
    }

    btn.addEventListener("click", function () {
      setOpen(!el.classList.contains("site-nav--open"));
    });

    el.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (mq.matches) {
          close();
        }
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        close();
      }
    });

    if (mq.addEventListener) {
      mq.addEventListener("change", onResize);
    } else {
      mq.addListener(onResize);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
