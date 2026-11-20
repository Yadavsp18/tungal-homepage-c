/* Tungal Option C interactions. Vanilla JS + GSAP/ScrollTrigger. Every module guards for missing markup and respects reduced motion. */
(function () {
  'use strict';
  var D = window.TUNGAL || {};
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var hasG = typeof gsap !== 'undefined';
  if (hasG && window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };

  /* ---------- header, progress, menu ---------- */
  (function header() {
    var hd = $('[data-hd]'); if (!hd) return;
    var bar = $('.hd__prog span', hd), last = scrollY, body = document.body;
    function onS() {
      var y = scrollY, max = document.documentElement.scrollHeight - innerHeight;
      if (bar) bar.style.setProperty('--p', max > 0 ? (y / max).toFixed(4) : 0);
      if (y > last + 6 && y > 480 && !body.classList.contains('menu-open')) hd.classList.add('is-hidden');
      else if (y < last - 6 || y < 200) hd.classList.remove('is-hidden');
      last = y;
    }
    addEventListener('scroll', onS, { passive: true }); onS();
    hd.addEventListener('focusin', function () { hd.classList.remove('is-hidden'); });
    var links = $$('.nav a'), map = {};
    links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { links.forEach(function (l) { l.classList.remove('on'); l.removeAttribute('aria-current'); }); var a = map[e.target.id]; if (a) { a.classList.add('on'); a.setAttribute('aria-current', 'true'); } } });
      }, { rootMargin: '-45% 0px -50% 0px' });
      Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) io.observe(s); });
    }
    var burger = $('.burger'), mm = $('#mm');
    function setMenu(open) {
      body.classList.toggle('menu-open', open); body.style.overflow = open ? 'hidden' : '';
      burger.setAttribute('aria-expanded', open); burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      mm.inert = !open;
      if (open) { hd.classList.remove('is-hidden'); mm.querySelector('a').focus(); }
    }
    mm.inert = true;
    burger.addEventListener('click', function () { setMenu(!body.classList.contains('menu-open')); });
    $$('a', mm).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
    document.addEventListener('keydown', function (e) {
      if (!body.classList.contains('menu-open')) return;
      if (e.key === 'Escape') { setMenu(false); burger.focus(); return; }
      if (e.key !== 'Tab') return;
      var f = [burger].concat($$('a', mm)).filter(function (x) { return x.offsetParent !== null || x === burger; });
      var i = f.indexOf(document.activeElement);
      if (e.shiftKey && (i <= 0)) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
    });
    addEventListener('resize', function () { if (innerWidth > 1100 && body.classList.contains('menu-open')) setMenu(false); });
  })();

  /* ---------- reveal ---------- */
  (function reveal() {
    var els = $$('.rv');
    if (!('IntersectionObserver' in window) || reduced) { els.forEach(function (e) { e.classList.add('in'); }); return; }
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    els.forEach(function (e) { io.observe(e); });
  })();

  /* ---------- aurora canvas ---------- */
  var aurora = (function () {
    var cv = $('#aurora'); if (!cv) return { set: function () {} };
    var ctx = cv.getContext('2d'), W, H, t = 0, run = true, px = .5, py = .5, tx = .5, ty = .5;
    var pals = [[[124, 108, 255], [255, 107, 74], [255, 200, 87]], [[79, 224, 196], [92, 168, 255], [255, 200, 87]], [[124, 108, 255], [255, 143, 177], [255, 200, 87]]];
    var cur = pals[0].map(function (c) { return c.slice(); }), tgt = pals[0];
    var blobs = [{ x: .2, y: .3, r: .55, s: .0004, p: 0 }, { x: .8, y: .25, r: .5, s: .0005, p: 2 }, { x: .6, y: .85, r: .6, s: .0003, p: 4 }, { x: .35, y: .9, r: .4, s: .0006, p: 1 }];
    function size() { var s = .5; W = cv.width = Math.ceil(cv.clientWidth * s); H = cv.height = Math.ceil(cv.clientHeight * s); }
    function draw() {
      ctx.globalCompositeOperation = 'source-over'; ctx.fillStyle = '#080B14'; ctx.fillRect(0, 0, W, H);
      ctx.globalCompositeOperation = 'lighter';
      for (var k = 0; k < 3; k++) for (var j = 0; j < 3; j++) cur[k][j] += (tgt[k][j] - cur[k][j]) * .03;
      px += (tx - px) * .04; py += (ty - py) * .04;
      blobs.forEach(function (b, i) {
        var c = cur[i % 3], x = (b.x + Math.sin(t * b.s * 1000 * .001 + b.p) * .12 + (px - .5) * .12 * (i % 2 ? 1 : -1)) * W, y = (b.y + Math.cos(t * b.s * 1000 * .001 + b.p) * .1 + (py - .5) * .1) * H, r = b.r * Math.max(W, H);
        var g = ctx.createRadialGradient(x, y, 0, x, y, r);
        g.addColorStop(0, 'rgba(' + (c[0] | 0) + ',' + (c[1] | 0) + ',' + (c[2] | 0) + ',.34)'); g.addColorStop(1, 'rgba(' + (c[0] | 0) + ',' + (c[1] | 0) + ',' + (c[2] | 0) + ',0)');
        ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      });
    }
    function loop() { if (run) { t += 16; draw(); } requestAnimationFrame(loop); }
    size(); draw(); addEventListener('resize', function () { size(); draw(); });
    if (!reduced) {
      requestAnimationFrame(loop);
      if ('IntersectionObserver' in window) new IntersectionObserver(function (e) { run = e[0].isIntersecting && !document.hidden; }).observe(cv);
      document.addEventListener('visibilitychange', function () { run = !document.hidden; });
      var hero = $('[data-hero]');
      hero.addEventListener('pointermove', function (e) { var r = hero.getBoundingClientRect(); tx = (e.clientX - r.left) / r.width; ty = (e.clientY - r.top) / r.height; });
    }
    return { set: function (i) { tgt = pals[i % 3]; if (reduced) { cur = tgt.map(function (c) { return c.slice(); }); draw(); } } };
  })();

  /* ---------- hero slider ---------- */
  (function hero() {
    var root = $('[data-hero]'); if (!root) return;
    var slides = $$('.slide', root), imgs = $$('.poster img', root), steps = $$('.step', root), poster = $('[data-poster]', root);
    var idx = 0, auto = !reduced, paused = false, hovering = false, t0 = 0, el = 0, dur = D.heroInterval || 7000, rafId;
    var pauseBtn = $('[data-pause]', root);
    function show(i, user) {
      i = (i + slides.length) % slides.length; idx = i;
      slides.forEach(function (s, k) { s.classList.toggle('on', k === i); s.setAttribute('aria-hidden', k !== i); });
      imgs.forEach(function (m, k) { m.classList.toggle('on', k === i); });
      steps.forEach(function (s, k) { s.setAttribute('aria-selected', k === i); var b = $('i', s); b.style.transform = k < i ? 'scaleX(1)' : 'scaleX(0)'; });
      aurora.set(i); el = 0;
      if (hasG && !reduced) gsap.fromTo($$('.w>span', slides[i]), { yPercent: 115, rotate: 4 }, { yPercent: 0, rotate: 0, duration: 1, ease: 'expo.out', stagger: .07, overwrite: true });
      if (hasG && !reduced) gsap.fromTo($('.slide__p', slides[i]), { y: 18, opacity: 0 }, { y: 0, opacity: 1, duration: .9, delay: .25, ease: 'power3.out', overwrite: true });
    }
    function tick(ts) {
      if (!t0) t0 = ts; var d = ts - t0; t0 = ts;
      if (auto && !paused && !hovering && !document.hidden) { el += d; var b = $('i', steps[idx]); b.style.transform = 'scaleX(' + clamp(el / dur, 0, 1) + ')'; if (el >= dur) show(idx + 1); }
      rafId = requestAnimationFrame(tick);
    }
    steps.forEach(function (s, k) { s.addEventListener('click', function () { show(k); }); });
    $('[data-next]', root).addEventListener('click', function () { show(idx + 1); });
    $('[data-prev]', root).addEventListener('click', function () { show(idx - 1); });
    pauseBtn.addEventListener('click', function () {
      paused = !paused; if (reduced) { auto = true; paused = false; }
      pauseBtn.setAttribute('aria-pressed', paused); pauseBtn.setAttribute('aria-label', paused ? 'Play slideshow' : 'Pause slideshow');
    });
    if (reduced) { pauseBtn.hidden = true; }
    root.addEventListener('mouseenter', function () { hovering = true; }); root.addEventListener('mouseleave', function () { hovering = false; });
    root.addEventListener('focusin', function () { hovering = true; }); root.addEventListener('focusout', function () { hovering = false; });
    root.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') show(idx + 1); if (e.key === 'ArrowLeft') show(idx - 1); });
    if (fine && !reduced && poster) {
      root.addEventListener('pointermove', function (e) {
        var r = root.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        poster.style.setProperty('--ry', (x * 9).toFixed(2) + 'deg'); poster.style.setProperty('--rx', (-y * 7).toFixed(2) + 'deg');
        imgs.forEach(function (m) { m.style.setProperty('--tx', (x * -16).toFixed(1) + 'px'); m.style.setProperty('--ty', (y * -16).toFixed(1) + 'px'); });
      });
      root.addEventListener('mouseleave', function () { poster.style.setProperty('--ry', '0deg'); poster.style.setProperty('--rx', '0deg'); });
    }
    slides.forEach(function (s, k) { s.setAttribute('aria-hidden', k !== 0); });
    function loadRest() { imgs.forEach(function (m) { if (m.dataset.src) { m.src = m.dataset.src; m.removeAttribute('data-src'); } }); }
    if (document.readyState === 'complete') setTimeout(loadRest, 300); else addEventListener('load', function () { setTimeout(loadRest, 300); });
    show(0);
    if (auto) rafId = requestAnimationFrame(tick); else steps.forEach(function (s) { $('i', s).style.transform = 'scaleX(0)'; });
  })();

  /* ---------- marquee ---------- */
  (function marquee() {
    var rows = $$('[data-mq] .mq__row'); if (!rows.length || reduced || !rows[0].animate) return;
    var anims = rows.map(function (r, i) { return r.animate([{ transform: 'translateX(0)' }, { transform: 'translateX(-50%)' }], { duration: 52000 - i * 6000, iterations: Infinity, direction: i ? 'reverse' : 'normal' }); });
    var rate = 1, target = 1, lastY = scrollY, hover = false, host = $('[data-mq]');
    host.addEventListener('mouseenter', function () { hover = true; }); host.addEventListener('mouseleave', function () { hover = false; });
    addEventListener('scroll', function () { var v = Math.abs(scrollY - lastY); lastY = scrollY; target = 1 + clamp(v / 14, 0, 5); }, { passive: true });
    var vis = true; if ('IntersectionObserver' in window) new IntersectionObserver(function (e) { vis = e[0].isIntersecting; }).observe(host);
    (function loop() {
      if (vis) { var want = hover ? .15 : target; rate += (want - rate) * .08; target += (1 - target) * .05; anims.forEach(function (a) { a.playbackRate = rate; }); }
      requestAnimationFrame(loop);
    })();
  })();

  /* ---------- counters ---------- */
  (function counters() {
    var els = $$('[data-count]'); if (!els.length || reduced || !('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return; io.unobserve(e.target);
        var el = e.target, to = +el.dataset.count, t0 = performance.now(), d = 1400;
        (function f(n) { var p = clamp((n - t0) / d, 0, 1); el.textContent = Math.round(to * (1 - Math.pow(1 - p, 4))); if (p < 1) requestAnimationFrame(f); })(t0);
      });
    }, { threshold: .6 });
    els.forEach(function (e) { io.observe(e); });
  })();

  /* ---------- big 25 ---------- */
  (function big25() {
    var el = $('[data-big25]'), sec = $('.legacy__grid'); if (!el) return;
    if (!hasG || !window.ScrollTrigger || reduced) { el.style.setProperty('--p', 100); return; }
    el.style.setProperty('--p', 0); el.textContent = '0';
    ScrollTrigger.create({ trigger: sec, start: 'top 75%', end: 'bottom 60%', onUpdate: function (s) {
      el.style.setProperty('--p', (clamp(s.progress * 1.25, 0, 1) * 100).toFixed(1));
      el.textContent = Math.round(25 * clamp(s.progress * 2.4, 0, 1));
    } });
  })();

  /* ---------- finder ---------- */
  var F = { campus: '', prog: '' };
  (function finder() {
    var box = $('[data-finder]'); if (!box) return;
    var out = $('[data-out]', box), stage = 'puc', hostel = false;
    var N = { jamkhandi: 'Jamkhandi', hulyal: 'Hulyal', bagalkot: 'Bagalkot', vijayapura: 'Vijayapura' };
    var data = {
      montessori: { l: 'Montessori to Std V', prog: '', c: [{ k: 'jamkhandi', t: 'Montessori stream and Karnataka State curriculum.' }] },
      school: { l: 'Std VI to X (CBSE)', prog: 'cbse-6-10', c: [{ k: 'hulyal', t: 'CBSE, Std VI to X.' }, { k: 'vijayapura', t: 'CBSE, Std VI to X.' }] },
      puc: { l: 'PUC Science', prog: 'puc', c: [{ k: 'jamkhandi', t: 'KCET, NEET and IIT-JEE preparation.' }, { k: 'hulyal', t: 'KCET, NEET and IIT-JEE Advanced preparation.', h: 1 }, { k: 'bagalkot', t: 'KCET, NEET and IIT-JEE Advanced preparation.', h: 1 }, { k: 'vijayapura', t: 'KCET, NEET and IIT-JEE Advanced preparation.', h: 1 }] },
      degree: { l: 'B.Sc & BCA', prog: '', c: [{ k: 'jamkhandi', t: 'Affiliated with Bagalkot University, Jamkhandi.' }] }
    };
    function render() {
      var d = data[stage], list = d.c.filter(function (c) { return !hostel || c.h; });
      out.innerHTML = '';
      if (!list.length) {
        var p = document.createElement('p'); p.className = 'finder__empty';
        p.innerHTML = 'Hostels are available for PUC students only, at Hulyal, Bagalkot and Vijayapura. <button type="button" data-showpuc>Show PUC campuses with hostel</button>';
        out.appendChild(p); $('[data-showpuc]', p).addEventListener('click', function () { setStage('puc'); }); return;
      }
      list.forEach(function (c, i) {
        var a = document.createElement('article'); a.className = 'fc'; a.style.setProperty('--i', i);
        a.innerHTML = '<h3>' + N[c.k] + '</h3><p>' + c.t + '</p>' + (c.h ? '<span class="tag">Hostel for boys &amp; girls</span>' : '') + '<button type="button">Enquire for ' + N[c.k] + ' <span aria-hidden="true">→</span></button>';
        $('button', a).addEventListener('click', function () { enquire(c.k, d.prog); });
        out.appendChild(a);
      });
    }
    function setStage(s) { stage = s; $$('[data-stage]', box).forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.stage === s); }); render(); }
    $$('[data-stage]', box).forEach(function (b) { b.addEventListener('click', function () { setStage(b.dataset.stage); }); });
    $('[data-hostel]', box).addEventListener('click', function (e) { hostel = !hostel; e.currentTarget.setAttribute('aria-pressed', hostel); render(); });
    render();
  })();

  /* ---------- programmes ---------- */
  var openCampus = function () {};
  (function programmes() {
    var tabsEl = $('[data-ptabs]'), panel = $('[data-pp]'); if (!tabsEl) return;
    var tabs = $$('.ptab', tabsEl), imgs = $$('.pp__img img', panel);
    var P = [
      { t: 'Montessori', d: 'Montessori to Standard V, with a Montessori stream and the Karnataka State curriculum.', n: '', c: ['jamkhandi'] },
      { t: 'School Education', d: 'Up to Standard V on the State curriculum at Jamkhandi; Standard VI to X on the CBSE curriculum at Hulyal and Vijayapura.', n: '', c: ['jamkhandi', 'hulyal', 'vijayapura'] },
      { t: 'PU Science', d: 'The two-year integrated course designed to provide students with intense and rigorous training for Board examinations as well as competitive examinations.', n: 'PCMB · PCMC · PCMS · PCME (Jamkhandi)', c: ['jamkhandi', 'hulyal', 'bagalkot', 'vijayapura'] },
      { t: 'Competitive Exam Preparation', d: 'KCET, NEET and IIT-JEE preparation at Jamkhandi; KCET, NEET and IIT-JEE Advanced preparation at Hulyal, Bagalkot and Vijayapura.', n: '', c: ['jamkhandi', 'hulyal', 'bagalkot', 'vijayapura'] },
      { t: 'Undergraduate Programmes', d: 'B.Sc and BCA, affiliated with Bagalkot University, Jamkhandi.', n: '', c: ['jamkhandi'] }
    ];
    var N = { jamkhandi: 'Jamkhandi', hulyal: 'Hulyal', bagalkot: 'Bagalkot', vijayapura: 'Vijayapura' };
    function set(i, focus) {
      tabs.forEach(function (b, k) { b.setAttribute('aria-selected', k === i); b.tabIndex = k === i ? 0 : -1; });
      imgs.forEach(function (m, k) { m.classList.toggle('on', k === i); });
      panel.setAttribute('aria-labelledby', 'pt' + i);
      var p = P[i];
      $('[data-pt]', panel).textContent = p.t; $('[data-pd]', panel).textContent = p.d; $('[data-pn]', panel).textContent = p.n;
      var at = $('[data-pa]', panel); at.innerHTML = '<small>Offered at</small>';
      p.c.forEach(function (k) { var b = document.createElement('button'); b.type = 'button'; b.textContent = N[k]; b.setAttribute('aria-label', 'Open the ' + N[k] + ' campus'); b.addEventListener('click', function () { openCampus(k, true); }); at.appendChild(b); });
      if (focus) tabs[i].focus();
    }
    tabs.forEach(function (b, i) { b.addEventListener('click', function () { set(i); }); b.addEventListener('mouseenter', function () { if (fine) set(i); }); });
    tabsEl.addEventListener('keydown', function (e) {
      var i = tabs.indexOf(document.activeElement); if (i < 0) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowRight') { e.preventDefault(); set((i + 1) % tabs.length, true); }
      if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); set((i - 1 + tabs.length) % tabs.length, true); }
      if (e.key === 'Home') { e.preventDefault(); set(0, true); } if (e.key === 'End') { e.preventDefault(); set(tabs.length - 1, true); }
    });
    set(0);
  })();

  /* ---------- campuses ---------- */
  (function campuses() {
    var list = $('[data-cp]'); if (!list) return;
    var ps = $$('.cpanel', list);
    var lock = 0, timer;
    function open(k, scroll) {
      if (scroll) lock = Date.now() + 1500;
      ps.forEach(function (p) {
        var on = p.dataset.campus === k; p.classList.toggle('on', on);
        $('.cpanel__tap', p).setAttribute('aria-expanded', on); $('.cpanel__body', p).inert = !on;
      });
      if (scroll) { var el = document.getElementById('campuses'); el.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' }); }
    }
    ps.forEach(function (p) { $('.cpanel__tap', p).addEventListener('click', function () { open(p.dataset.campus); }); if (fine) { p.addEventListener('mouseenter', function () { if (innerWidth <= 860 || p.classList.contains('on')) return; clearTimeout(timer); timer = setTimeout(function () { if (Date.now() > lock) open(p.dataset.campus); }, 150); }); p.addEventListener('mouseleave', function () { clearTimeout(timer); }); } });
    openCampus = open;
  })();

  /* ---------- glow follow ---------- */
  (function glow() {
    $$('[data-glow],.wrow').forEach(function (el) { el.addEventListener('pointermove', function (e) { var r = el.getBoundingClientRect(); el.style.setProperty('--mx', (e.clientX - r.left) + 'px'); el.style.setProperty('--my', (e.clientY - r.top) + 'px'); }); });
  })();

  /* ---------- life carousel ---------- */
  (function life() {
    var tr = $('[data-life]'); if (!tr) return;
    var bar = $('[data-lbar]'); function prog() { var m = tr.scrollWidth - tr.clientWidth; if (bar) bar.style.setProperty('--p', m > 0 ? clamp(.12 + .88 * tr.scrollLeft / m, .12, 1).toFixed(3) : 1); }
    tr.addEventListener('scroll', prog, { passive: true }); addEventListener('resize', prog); prog();
    function step(d) { var c = $('.lc', tr); tr.scrollBy({ left: d * (c.offsetWidth + 16), behavior: reduced ? 'auto' : 'smooth' }); }
    $('[data-lprev]').addEventListener('click', function () { step(-1); }); $('[data-lnext]').addEventListener('click', function () { step(1); });
    var down = false, sx = 0, sl = 0;
    tr.addEventListener('pointerdown', function (e) { if (e.pointerType !== 'mouse') return; down = true; sx = e.clientX; sl = tr.scrollLeft; tr.classList.add('drag'); tr.setPointerCapture(e.pointerId); });
    tr.addEventListener('pointermove', function (e) { if (down) tr.scrollLeft = sl - (e.clientX - sx); });
    function up() { down = false; tr.classList.remove('drag'); }
    tr.addEventListener('pointerup', up); tr.addEventListener('pointercancel', up);
  })();

  /* ---------- magnetic buttons ---------- */
  (function mag() {
    if (!fine || reduced) return;
    $$('[data-mag],.hd__cta').forEach(function (b) {
      b.addEventListener('pointermove', function (e) { var r = b.getBoundingClientRect(); b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * .22).toFixed(1) + 'px,' + ((e.clientY - r.top - r.height / 2) * .3).toFixed(1) + 'px)'; });
      b.addEventListener('pointerleave', function () { b.style.transform = ''; });
    });
  })();

  /* ---------- cursor ---------- */
  (function cursor() {
    if (!fine || reduced) return;
    var dot = $('.cur'), ring = $('.cur-ring'), x = -100, y = -100, rx = -100, ry = -100;
    document.documentElement.classList.add('has-cur');
    document.addEventListener('pointermove', function (e) {
      x = e.clientX; y = e.clientY; dot.style.transform = 'translate(' + x + 'px,' + y + 'px)';
      var t = e.target.closest ? e.target.closest('a,button,select,input,textarea,label,[data-cursor]') : null;
      var drag = e.target.closest && e.target.closest('[data-life]') && !t;
      ring.classList.toggle('is-link', !!t && !drag); ring.classList.toggle('is-drag', !!drag);
      ring.dataset.label = drag ? 'Drag' : (t && t.dataset.cursor) || '';
    });
    document.addEventListener('mouseleave', function () { document.body.classList.add('cur-hide'); }); document.addEventListener('mouseenter', function () { document.body.classList.remove('cur-hide'); });
    (function loop() { rx += (x - rx) * .16; ry += (y - ry) * .16; ring.style.transform = 'translate(' + rx.toFixed(1) + 'px,' + ry.toFixed(1) + 'px)'; requestAnimationFrame(loop); })();
  })();

  /* ---------- enquiry form ---------- */
  var enquire = function () {};
  (function form() {
    var f = $('[data-form]'); if (!f) return;
    var campus = f.campus, prog = f.programme, hrow = $('[data-hostelrow]', f), prb = $('.fprog', f);
    function fillProg(sel) {
      var opts = (D.programmes || {})[campus.value] || [];
      prog.innerHTML = '';
      var o0 = new Option(opts.length ? 'Select a programme' : 'Choose a campus first', ''); prog.add(o0);
      opts.forEach(function (o) { prog.add(new Option(o.label, o.value)); });
      prog.disabled = !opts.length; if (sel) prog.value = sel; hostelRow(); progress();
    }
    function hostelRow() {
      var ok = ((D.hostel || {})[campus.value] || []).indexOf(prog.value) > -1; hrow.hidden = !ok; if (!ok) f.hostel.checked = false;
    }
    function norm(v) { var d = String(v).replace(/\D/g, ''); if (d.length === 12 && d.indexOf('91') === 0) d = d.slice(2); if (d.length === 11 && d[0] === '0') d = d.slice(1); return d; }
    function msg(el, t) { var e = el.closest('.fld').querySelector('[data-err]'); if (e) e.textContent = t || ''; el.setAttribute('aria-invalid', t ? 'true' : 'false'); if (t) el.setAttribute('aria-describedby', ''); }
    var rules = {
      student_name: function (v) { return v.trim().length >= 2 ? '' : "Enter the student's name."; },
      parent_name: function (v) { return v.trim().length >= 2 ? '' : 'Enter the parent or guardian name.'; },
      phone: function (v) { return /^[6-9]\d{9}$/.test(norm(v)) ? '' : 'Enter a valid 10-digit mobile number.'; },
      email: function (v) { return !v || /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v) ? '' : 'Enter a valid email address.'; },
      campus: function (v) { return v ? '' : 'Select a campus.'; },
      programme: function (v) { return v ? '' : 'Select a programme.'; },
      consent: function () { return f.consent.checked ? '' : 'Please agree to be contacted.'; }
    };
    function check(el) { var r = rules[el.name]; if (!r) return true; var m = r(el.value); msg(el, m); return !m; }
    function progress() {
      var names = ['student_name', 'parent_name', 'phone', 'campus', 'programme', 'consent'], ok = 0;
      names.forEach(function (n) { var e = f[n]; if (rules[n](e.type === 'checkbox' ? '' : e.value) === '') ok++; });
      prb.style.setProperty('--p', (ok / names.length).toFixed(2));
    }
    campus.addEventListener('change', function () { fillProg(); });
    prog.addEventListener('change', function () { hostelRow(); progress(); });
    $$('input,select,textarea', f).forEach(function (el) { el.addEventListener('blur', function () { check(el); }); el.addEventListener('input', function () { if (el.getAttribute('aria-invalid') === 'true') check(el); progress(); }); el.addEventListener('change', progress); });
    f.addEventListener('submit', function (e) {
      e.preventDefault(); var bad = null;
      ['student_name', 'parent_name', 'phone', 'email', 'campus', 'programme', 'consent'].forEach(function (n) { var el = f[n]; if (!check(el) && !bad) bad = el; });
      var m = $('[data-msg]', f); m.textContent = '';
      if (bad) { bad.focus(); return; }
      var fd = new FormData(f); fd.set('phone', norm(f.phone.value));
      var btn = $('button[type=submit]', f); btn.disabled = true;
      fetch(f.action, { method: 'POST', body: fd }).then(function (r) { return r.json().catch(function () { return { ok: r.ok }; }); }).then(function (j) {
        if (j && j.ok) { f.classList.add('done'); $('.form__ok', f).focus(); } else { m.textContent = 'We could not send your enquiry. Please call a campus office.'; btn.disabled = false; }
      }).catch(function () { m.textContent = 'We could not send your enquiry. Please call a campus office.'; btn.disabled = false; });
    });
    enquire = function (k, p) {
      campus.value = k; fillProg(p || '');
      document.getElementById('admissions').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
      setTimeout(function () { (p ? f.student_name : prog).focus({ preventScroll: true }); }, reduced ? 0 : 700);
    };
    $$('[data-enquire]').forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); enquire(a.dataset.enquire); }); });
    progress();
  })();
})();
