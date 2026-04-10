(function () {
  'use strict';

  /* ---- NAV INJECTION ---- */
  var NAV_LINKS = [
    { href: '/',                    label: 'Início',       match: ['index.html', '/'] },
    { href: '/saude_engine_v3.html',label: 'Engine',       match: ['saude_engine_v3.html'] },
    { href: '/grafo_saude_v2.html', label: 'Grafo',        match: ['grafo_saude_v2.html'] },
    { href: '/docs_saude_v3.html',  label: 'Documentação', match: ['docs_saude_v3.html'] },
    { href: '/about_saude.html',    label: 'About',        match: ['about_saude.html'] },
    { href: '/app',                 label: 'Acesso',       match: ['/app', 'app'], cta: true },
  ];

  function currentPage() {
    return window.location.pathname;
  }

  function isActive(link) {
    var cur = currentPage();
    return link.match.some(function (m) {
      return cur === m || cur.endsWith(m) || cur === '/' + m;
    });
  }

  function buildNav() {
    var linksHtml = NAV_LINKS.map(function (l) {
      var cls = [];
      if (isActive(l)) cls.push('sn-active');
      if (l.cta) cls.push('sn-cta');
      return '<a href="' + l.href + '" class="' + cls.join(' ') + '">' + l.label + '</a>';
    }).join('');

    var drawerLinks = NAV_LINKS.map(function (l) {
      var cls = [];
      if (isActive(l)) cls.push('sn-active');
      if (l.cta) cls.push('sn-cta');
      return '<a href="' + l.href + '" class="' + cls.join(' ') + '">' + l.label + '</a>';
    }).join('');

    var nav = document.createElement('nav');
    nav.id = 'site-nav';
    nav.setAttribute('role', 'navigation');
    nav.setAttribute('aria-label', 'Site navigation');
    nav.innerHTML =
      '<div class="sn-inner">' +
        '<a href="/" class="sn-logo">Inferência em <em>saúde masculina</em></a>' +
        '<div class="sn-links">' + linksHtml + '</div>' +
        '<button class="sn-burger" id="sn-burger" aria-label="Menu" aria-expanded="false">' +
          '<span></span><span></span><span></span>' +
        '</button>' +
      '</div>' +
      '<div class="sn-drawer" id="sn-drawer">' + drawerLinks + '</div>';

    document.body.insertBefore(nav, document.body.firstChild);
  }

  /* ---- HAMBURGER TOGGLE ---- */
  function initHamburger() {
    var burger = document.getElementById('sn-burger');
    var drawer = document.getElementById('sn-drawer');
    if (!burger || !drawer) return;

    burger.addEventListener('click', function () {
      var isOpen = drawer.classList.toggle('open');
      burger.classList.toggle('open', isOpen);
      burger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    drawer.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        drawer.classList.remove('open');
        burger.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    });
  }

  /* ---- SCROLL ANIMATIONS ---- */
  function initScrollAnimations() {
    var els = document.querySelectorAll('.fade-up');
    if (!els.length) return;

    if (!('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('visible'); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    els.forEach(function (el) { observer.observe(el); });
  }

  /* ---- READ PROGRESS BAR ---- */
  function initProgress() {
    var bar = document.getElementById('read-progress');
    if (!bar) return;
    window.addEventListener('scroll', function () {
      var total = document.documentElement.scrollHeight - window.innerHeight;
      var pct = total > 0 ? (window.scrollY / total) * 100 : 0;
      bar.style.width = Math.min(pct, 100) + '%';
    }, { passive: true });
  }

  /* ---- INIT ---- */
  function init() {
    buildNav();
    initHamburger();
    initScrollAnimations();
    initProgress();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
