/* Python de A a Z · comportamento da página
   - rolagem suave (Lenis), desligada para quem pede movimento reduzido;
   - efeitos ligados à rolagem via variáveis CSS (--p no hero, --fill na trilha);
   - revelar ao rolar, contadores e cabeçalho. Sem dependências além do Lenis. */
(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var narrow = window.matchMedia("(max-width: 820px)");
  var root = document.documentElement;
  var header = document.querySelector(".site-header");
  var hero = document.getElementById("hero");
  var trail = document.getElementById("trilha");
  var steps = Array.prototype.slice.call(document.querySelectorAll(".step"));
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

  /* ---------- rolagem suave ---------- */
  var lenis = null;
  if (!reduce.matches && typeof window.Lenis === "function") {
    lenis = new window.Lenis({ lerp: 0.1, smoothWheel: true, wheelMultiplier: 1 });
    (function raf(time) { lenis.raf(time); requestAnimationFrame(raf); })(performance.now());
  }

  function headerHeight() { return header ? header.offsetHeight : 0; }

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute("href");
    if (id === "#") { e.preventDefault(); return; }          // links de loja ainda sem endereço
    var target = document.querySelector(id);
    if (!target) return;
    e.preventDefault();
    if (lenis) lenis.scrollTo(target, { offset: -(headerHeight() + 8), duration: 1.2 });
    else target.scrollIntoView({ behavior: "auto", block: "start" });
    if (history.replaceState) history.replaceState(null, "", id);
  });

  /* ---------- efeitos ligados à rolagem ---------- */
  var ticking = false;
  function update() {
    ticking = false;
    var y = window.scrollY || window.pageYOffset;
    var vh = window.innerHeight;

    if (header) header.classList.toggle("is-scrolled", y > 8);

    if (hero && !reduce.matches) {
      var hh = hero.offsetHeight || 1;
      var p = narrow.matches ? 0 : clamp(y / hh, 0, 1);       // no celular o leque fica parado
      hero.style.setProperty("--p", p.toFixed(4));
    }

    if (trail && steps.length) {
      var r = trail.getBoundingClientRect();
      var total = r.height + vh * 0.4;
      var prog = clamp((vh * 0.85 - r.top) / total, 0, 1);    // 0 quando entra, 1 quando está quase saindo
      var scaled = prog * (steps.length + 0.35);
      steps.forEach(function (step, i) {
        var f = clamp(scaled - i, 0, 1);
        step.style.setProperty("--fill", f.toFixed(3));
        step.classList.toggle("is-on", scaled >= i + 0.12);
      });
    }
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  update();

  /* ---------- revelar ao rolar ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if (reduce.matches || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
  }

  /* ---------- contadores ---------- */
  var counters = document.querySelectorAll("[data-count]");
  function fmt(el, n) {
    return el.getAttribute("data-format") === "pt" ? n.toLocaleString("pt-BR") : String(n);
  }
  if (!reduce.matches && "IntersectionObserver" in window) {
    counters.forEach(function (el) { el.textContent = fmt(el, 0); });
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        co.unobserve(en.target);
        var el = en.target, end = parseInt(el.getAttribute("data-count"), 10), t0 = performance.now(), dur = 1400;
        (function tick(now) {
          var k = clamp((now - t0) / dur, 0, 1);
          var eased = 1 - Math.pow(1 - k, 3);
          el.textContent = fmt(el, Math.round(end * eased));
          if (k < 1) requestAnimationFrame(tick);
        })(t0);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { co.observe(el); });
  }

  /* ---------- link da seção atual no menu ---------- */
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav a[href^="#"]:not(.btn)'));
  if ("IntersectionObserver" in window && links.length) {
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (l) { l.setAttribute("aria-current", l.getAttribute("href") === "#" + en.target.id ? "true" : "false"); });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    links.forEach(function (l) { var s = document.querySelector(l.getAttribute("href")); if (s) so.observe(s); });
  }

  /* ---------- inclinação suave da capa (só mouse) ---------- */
  var tilt = document.querySelector(".bookhero__cover");
  if (tilt && !reduce.matches && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    tilt.addEventListener("mousemove", function (e) {
      var r = tilt.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      tilt.classList.add("is-tilting");
      tilt.style.setProperty("--ry", (x * 10).toFixed(2) + "deg");
      tilt.style.setProperty("--rx", (-y * 10).toFixed(2) + "deg");
    });
    tilt.addEventListener("mouseleave", function () {
      tilt.classList.remove("is-tilting");
      tilt.style.setProperty("--ry", "0deg");
      tilt.style.setProperty("--rx", "0deg");
    });
  }

  reduce.addEventListener && reduce.addEventListener("change", function () { if (reduce.matches && lenis) { lenis.destroy(); lenis = null; } });
})();
