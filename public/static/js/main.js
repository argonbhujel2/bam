/**
 * BAM Studio — Public site interactions (v2 motion)
 */
(function () {
  "use strict";

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function initLoader() {
    const loader = document.querySelector(".loader");
    const finish = () => {
      document.body.classList.add("is-loaded");
      if (loader) loader.classList.add("is-done");
    };
    const delay = prefersReduced ? 0 : 320;
    if (document.readyState === "complete") {
      setTimeout(finish, delay);
    } else {
      window.addEventListener("load", () => setTimeout(finish, delay));
      // safety: never block more than 1.2s
      setTimeout(finish, 1200);
    }
  }

  function initNav() {
    const nav = document.querySelector(".nav");
    if (!nav) return;
    const onScroll = () => {
      nav.classList.toggle("is-scrolled", window.scrollY > 32);
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

  function initReveal() {
    const targets = document.querySelectorAll("[data-reveal], [data-stagger]");
    if (!targets.length) return;
    if (prefersReduced) {
      targets.forEach((el) => el.classList.add("is-visible"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("is-visible");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -48px 0px" }
    );
    targets.forEach((el) => io.observe(el));
  }

  function initMagnetic() {
    if (prefersReduced || window.matchMedia("(pointer: coarse)").matches) return;
    document.querySelectorAll(".btn-magnetic, .btn-primary").forEach((btn) => {
      btn.addEventListener("pointermove", (e) => {
        const r = btn.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2;
        const y = e.clientY - r.top - r.height / 2;
        btn.style.transform = `translate(${x * 0.15}px, ${y * 0.2}px)`;
      });
      btn.addEventListener("pointerleave", () => {
        btn.style.transform = "";
      });
    });
  }

  function initHeroParallax() {
    if (prefersReduced) return;
    const media = document.querySelector(".hero-media");
    if (!media) return;
    let ticking = false;
    window.addEventListener(
      "scroll",
      () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
          const y = window.scrollY;
          if (y < window.innerHeight) {
            media.style.transform = `translateY(${y * 0.18}px)`;
          }
          ticking = false;
        });
      },
      { passive: true }
    );
  }

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

  function initFaq() {
    document.querySelectorAll(".faq-item").forEach((item) => {
      const btn = item.querySelector("button, .faq-q, summary");
      if (!btn) return;
      btn.addEventListener("click", () => {
        const open = item.classList.contains("is-open");
        document.querySelectorAll(".faq-item.is-open").forEach((i) => i.classList.remove("is-open"));
        if (!open) item.classList.add("is-open");
      });
    });
  }

  function initSmoothAnchors() {
    document.querySelectorAll('a[href^="#"]').forEach((a) => {
      a.addEventListener("click", (e) => {
        const id = a.getAttribute("href");
        if (!id || id === "#") return;
        const el = document.querySelector(id);
        if (!el) return;
        e.preventDefault();
        el.scrollIntoView({ behavior: prefersReduced ? "auto" : "smooth", block: "start" });
      });
    });
  }

  
  function initSpotlight() {
    if (prefersReduced || window.matchMedia("(pointer: coarse)").matches) return;
    const spot = document.createElement("div");
    spot.setAttribute("aria-hidden", "true");
    spot.style.cssText = "pointer-events:none;position:fixed;inset:0;z-index:0;opacity:0.4;background:radial-gradient(600px circle at var(--mx,50%) var(--my,50%),rgba(34,211,238,0.07),transparent 40%);transition:opacity .3s";
    document.body.appendChild(spot);
    window.addEventListener("pointermove", (e) => {
      document.documentElement.style.setProperty("--mx", e.clientX + "px");
      document.documentElement.style.setProperty("--my", e.clientY + "px");
    }, { passive: true });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initSpotlight();
    initLoader();
    initNav();
    initReveal();
    initMagnetic();
    initHeroParallax();
    initWorkFilter();
    initFaq();
    initSmoothAnchors();
  });
})();
