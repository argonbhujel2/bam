/**
 * BAM Studio — Public site interactions
 */
(function () {
  "use strict";

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Page loader
  function initLoader() {
    const loader = document.querySelector(".loader");
    if (!loader) return;
    const hide = () => loader.classList.add("is-done");
    if (document.readyState === "complete") {
      setTimeout(hide, prefersReduced ? 0 : 600);
    } else {
      window.addEventListener("load", () => setTimeout(hide, prefersReduced ? 0 : 600));
    }
  }

  // Sticky nav
  function initNav() {
    const nav = document.querySelector(".nav");
    if (!nav) return;
    const onScroll = () => {
      nav.classList.toggle("is-scrolled", window.scrollY > 40);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    const toggle = document.querySelector(".nav-toggle");
    const mobile = document.querySelector(".mobile-nav");
    if (toggle && mobile) {
      toggle.addEventListener("click", () => {
        toggle.classList.toggle("is-open");
        mobile.classList.toggle("is-open");
        document.body.style.overflow = mobile.classList.contains("is-open") ? "hidden" : "";
      });
      mobile.querySelectorAll("a").forEach((a) => {
        a.addEventListener("click", () => {
          toggle.classList.remove("is-open");
          mobile.classList.remove("is-open");
          document.body.style.overflow = "";
        });
      });
    }
  }

  // Scroll reveal
  function initReveal() {
    if (prefersReduced) {
      document.querySelectorAll("[data-reveal]").forEach((el) => el.classList.add("is-visible"));
      return;
    }
    const els = document.querySelectorAll("[data-reveal]");
    if (!els.length) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("is-visible");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    els.forEach((el) => io.observe(el));
  }

  // Portfolio filter (AJAX)
  function initWorkFilter() {
    const filters = document.querySelector(".work-filters");
    const grid = document.querySelector(".work-grid");
    if (!filters || !grid) return;

    filters.addEventListener("click", async (e) => {
      const btn = e.target.closest("button[data-category]");
      if (!btn) return;
      filters.querySelectorAll("button").forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");
      const cat = btn.dataset.category;
      try {
        const res = await fetch(`/api/projects?category=${encodeURIComponent(cat)}`);
        const data = await res.json();
        grid.innerHTML = data.projects
          .map(
            (p) => `
          <a href="${p.url}" class="work-card" data-reveal>
            ${
              p.cover_image
                ? `<img src="${p.cover_image}" alt="${p.title}" loading="lazy">`
                : `<div class="work-card-placeholder">${p.title}</div>`
            }
            <div class="work-card-overlay">
              <h3>${p.title}</h3>
              <span class="cat">${p.category || ""}</span>
            </div>
          </a>`
          )
          .join("");
        initReveal();
      } catch (err) {
        console.error(err);
      }
    });
  }

  // Magnetic buttons (subtle)
  function initMagnetic() {
    if (prefersReduced || window.innerWidth < 900) return;
    document.querySelectorAll(".btn-magnetic").forEach((btn) => {
      btn.addEventListener("mousemove", (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
      });
      btn.addEventListener("mouseleave", () => {
        btn.style.transform = "";
      });
    });
  }

  // Flash auto-dismiss
  function initFlash() {
    document.querySelectorAll(".flash").forEach((el) => {
      setTimeout(() => {
        el.style.opacity = "0";
        el.style.transition = "opacity 0.4s";
        setTimeout(() => el.remove(), 400);
      }, 5000);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initLoader();
    initNav();
    initReveal();
    initWorkFilter();
    initMagnetic();
    initFlash();
  });
})();

// Scroll to hash after page load (e.g. #behind-work)
window.addEventListener('load', function () {
  if (window.location.hash) {
    var el = document.querySelector(window.location.hash);
    if (el) setTimeout(function () { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 400);
  }
});
