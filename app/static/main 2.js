(function () {
  // Header shadow on scroll
  var header = document.querySelector('.site-header');
  function onScroll() { header && header.classList.toggle('scrolled', window.scrollY > 10); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // Mobile menu
  var toggle = document.querySelector('.menu-toggle');
  var menu = document.querySelector('.mobile-menu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open);
    });
    menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { menu.classList.remove('open'); }); });
  }

  // Reveal on scroll
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  // Count-up stats
  var nums = document.querySelectorAll('[data-count]');
  function run(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    var suffix = el.getAttribute('data-suffix') || '';
    var plain = el.hasAttribute('data-plain');
    var start = plain ? Math.max(0, target - 40) : 0;
    var t0 = null, dur = 1600;
    function step(ts) {
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(start + (target - start) * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { run(e.target); cio.unobserve(e.target); } });
    }, { threshold: 0.4 });
    nums.forEach(function (n) { cio.observe(n); });
  }

  // Gallery filter
  var tabs = document.querySelectorAll('.tab[data-filter]');
  var items = Array.prototype.slice.call(document.querySelectorAll('.g-item'));
  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      tabs.forEach(function (x) { x.classList.remove('active'); x.setAttribute('aria-selected', 'false'); });
      t.classList.add('active'); t.setAttribute('aria-selected', 'true');
      var f = t.getAttribute('data-filter');
      items.forEach(function (it) { it.classList.toggle('hide', f !== 'all' && it.getAttribute('data-cat') !== f); });
    });
  });

  // Lightbox
  var lb = document.querySelector('.lightbox');
  if (lb && items.length) {
    var img = lb.querySelector('img'), cap = lb.querySelector('.lb-cap'), idx = 0;
    function visible() { return items.filter(function (i) { return !i.classList.contains('hide'); }); }
    function show(i) {
      var v = visible(); idx = (i + v.length) % v.length;
      var it = v[idx];
      img.src = it.getAttribute('data-full');
      img.alt = it.querySelector('img').alt;
      cap.textContent = it.querySelector('figcaption').textContent + '  ·  ' + (idx + 1) + ' / ' + v.length;
    }
    items.forEach(function (it) {
      it.addEventListener('click', function () { show(visible().indexOf(it)); lb.classList.add('open'); document.body.style.overflow = 'hidden'; });
    });
    function close() { lb.classList.remove('open'); document.body.style.overflow = ''; }
    lb.querySelector('.lb-close').addEventListener('click', close);
    lb.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); show(idx - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); show(idx + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      var rtl = document.documentElement.dir === 'rtl';
      if (e.key === 'ArrowLeft') show(idx + (rtl ? 1 : -1));
      if (e.key === 'ArrowRight') show(idx + (rtl ? -1 : 1));
    });
  }

  // ---------------------------------------------------------------
  // Contact form
  //  • "Send inquiry"      -> emails info@paragoncmc.com via FormSubmit (no email app needed)
  //  • "Send on WhatsApp"  -> opens WhatsApp chat with the details pre-filled
  // ---------------------------------------------------------------
  // Contact details come from the CMS settings (rendered as data attributes on <body>)
  var EMAIL_TO = (document.body.getAttribute('data-email') || '').trim();
  var WA_NUMBER = (document.body.getAttribute('data-wa') || '').replace(/\D/g, '');

  function strings() {
    var ar = document.documentElement.lang === 'ar';
    return ar ? {
      sub: 'طلب مشروع جديد من الموقع', gen: 'عام', name: 'الاسم', email: 'البريد الإلكتروني', phone: 'الهاتف',
      loc: 'الموقع', svc: 'الخدمة', det: 'تفاصيل المشروع', lang: 'لغة الموقع', langv: 'العربية',
      hi: 'مرحباً باراجون، أود الاستفسار عن مشروع.', sending: 'جارٍ الإرسال…',
      needName: 'يرجى كتابة اسمك أولاً.'
    } : {
      sub: 'New project inquiry from the website', gen: 'General', name: 'Name', email: 'Email', phone: 'Phone',
      loc: 'Location', svc: 'Service', det: 'Project details', lang: 'Site language', langv: 'English',
      hi: "Hello Paragon, I'd like to ask about a project.", sending: 'Sending…',
      needName: 'Please enter your name first.'
    };
  }

  function collect(form) {
    var d = new FormData(form), g = function (k) { return (d.get(k) || '').toString().trim(); };
    return { name: g('name'), email: g('email'), phone: g('phone'), location: g('location'), service: g('service'), details: g('details'), honey: g('_honey') };
  }

  function setState(form, state) {
    ['ok', 'err'].forEach(function (k) {
      var el = form.querySelector('.form-' + k); if (el) el.classList.toggle('show', k === state);
    });
  }

  function waLink(text) { return 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(text); }

  document.querySelectorAll('form.inquiry').forEach(function (form) {
    var btn = form.querySelector('button[type="submit"]');
    var waBtn = form.querySelector('.wa-send');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      setState(form, null);
      if (!form.reportValidity()) return;
      var L = strings(), v = collect(form);
      if (v.honey) return;                      // spam bot filled the hidden field
      var payload = { name: v.name, email: v.email, phone: v.phone, location: v.location, service: v.service,
                      details: v.details, _honey: v.honey, lang: document.documentElement.lang };
      var ENDPOINT = form.getAttribute('data-endpoint') || '/api/inquiry';

      var label = btn.innerHTML;
      btn.disabled = true; btn.classList.add('is-loading'); btn.lastChild.textContent = L.sending;

      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok && String(res.j.success) === 'true') { setState(form, 'ok'); form.reset(); }
          else { throw new Error(res.j.message || 'Send failed'); }
        })
        .catch(function () { setState(form, 'err'); })
        .then(function () { btn.disabled = false; btn.classList.remove('is-loading'); btn.innerHTML = label; });
    });

    // Send the same details through WhatsApp
    function sendWhatsApp() {
      var L = strings(), v = collect(form);
      if (!v.name) { var n = form.querySelector('[name="name"]'); n.setCustomValidity(L.needName); n.reportValidity(); n.setCustomValidity(''); return; }
      var lines = [L.hi, '', L.name + ': ' + v.name];
      if (v.phone) lines.push(L.phone + ': ' + v.phone);
      if (v.email) lines.push(L.email + ': ' + v.email);
      if (v.location) lines.push(L.loc + ': ' + v.location);
      if (v.service) lines.push(L.svc + ': ' + v.service);
      if (v.details) lines.push('', L.det + ':', v.details);
      window.open(waLink(lines.join('\n')), '_blank', 'noopener');
    }
    if (waBtn) waBtn.addEventListener('click', sendWhatsApp);
    form.querySelectorAll('.wa-fallback').forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); sendWhatsApp(); }); });

    // Fallback in the error message: open the visitor's own email app with everything filled in
    form.querySelectorAll('.mail-fallback').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var L = strings(), v = collect(form);
        var body = [L.name + ': ' + v.name, L.email + ': ' + v.email, L.phone + ': ' + (v.phone || '-'), L.loc + ': ' + (v.location || '-'),
                    L.svc + ': ' + (v.service || '-'), '', L.det + ':', v.details || '-'].join('\n');
        window.location.href = 'mailto:' + EMAIL_TO + '?subject=' + encodeURIComponent(L.sub + ' — ' + v.name) + '&body=' + encodeURIComponent(body);
      });
    });
  });

  // ---------------------------------------------------------------
  // Project finder: instant search + sector / contract filters
  // ---------------------------------------------------------------
  var grid = document.getElementById('project-grid');
  if (grid) {
    var input = document.getElementById('project-search');
    var chips = Array.prototype.slice.call(document.querySelectorAll('.chip-f'));
    var contract = document.getElementById('contract-filter');
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.p-card'));
    var countEl = document.querySelector('.result-count');
    var empty = document.querySelector('.empty');
    var isAr = document.documentElement.lang === 'ar';

    // Normalise text so "Café" = "cafe", "أماني" = "اماني", "مكتبة" = "مكتبه", etc.
    function norm(s) {
      return (s || '').toString().toLowerCase()
        .normalize('NFD').replace(/[̀-ͯ]/g, '')          // Latin accents
        .replace(/[ً-ٰٟـ]/g, '')                // Arabic diacritics + tatweel
        .replace(/[أإآٱ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').replace(/ؤ/g, 'و').replace(/ئ/g, 'ي')
        .replace(/[&.,'’"()|–—\-_/]+/g, ' ').replace(/\s+/g, ' ').trim();
    }
    cards.forEach(function (c) { c._s = norm(c.getAttribute('data-search')); });

    var state = { q: '', sector: 'all', contract: 'all' };
    function readURL() {
      var p = new URLSearchParams(location.search);
      state.q = p.get('q') || ''; state.sector = p.get('sector') || 'all'; state.contract = p.get('type') || 'all';
      if (!chips.some(function (c) { return c.getAttribute('data-sector') === state.sector; })) state.sector = 'all';
      input.value = state.q; contract.value = state.contract;
      if (contract.value !== state.contract) { state.contract = 'all'; contract.value = 'all'; }
    }
    function writeURL() {
      var p = new URLSearchParams();
      if (state.q) p.set('q', state.q);
      if (state.sector !== 'all') p.set('sector', state.sector);
      if (state.contract !== 'all') p.set('type', state.contract);
      var qs = p.toString();
      try { history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash); } catch (e) {}
    }
    function apply() {
      var words = norm(state.q).split(' ').filter(Boolean), shown = 0;
      cards.forEach(function (c) {
        var ok = (state.sector === 'all' || c.getAttribute('data-sector') === state.sector) &&
                 (state.contract === 'all' || c.getAttribute('data-contract') === state.contract) &&
                 words.every(function (w) { return c._s.indexOf(w) !== -1; });
        c.hidden = !ok; if (ok) { shown++; c.classList.add('in'); }
      });
      chips.forEach(function (c) {
        var on = c.getAttribute('data-sector') === state.sector;
        c.classList.toggle('active', on); c.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      var tpl = countEl.getAttribute(isAr ? 'data-tpl-ar' : 'data-tpl-en');
      countEl.textContent = tpl.replace('{n}', shown).replace('{t}', cards.length);
      empty.hidden = shown !== 0;
      writeURL();
    }
    var timer;
    input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(function () { state.q = input.value.trim(); apply(); }, 80); });
    input.addEventListener('keydown', function (e) { if (e.key === 'Escape') { input.value = ''; state.q = ''; apply(); } });
    chips.forEach(function (c) { c.addEventListener('click', function () { state.sector = c.getAttribute('data-sector'); apply(); }); });
    contract.addEventListener('change', function () { state.contract = contract.value; apply(); });
    document.querySelectorAll('.reset-search').forEach(function (b) {
      b.addEventListener('click', function () { state = { q: '', sector: 'all', contract: 'all' }; input.value = ''; contract.value = 'all'; apply(); input.focus(); });
    });
    // Press "/" anywhere to jump to the search box
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && document.activeElement !== input && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); input.focus(); }
    });
    readURL(); apply();
  }

  var y = document.getElementById('year'); if (y) y.textContent = new Date().getFullYear();
})();
