// Entrechat Press site scripts
(function () {
  // mobile menu
  var btn = document.querySelector('.menu-btn');
  if (btn) {
    btn.addEventListener('click', function () {
      var open = document.body.classList.toggle('menu-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // testimonial carousel arrows
  document.querySelectorAll('[data-carousel]').forEach(function (wrap) {
    var track = wrap.querySelector('.carousel');
    var step = function () { var c = track.querySelector('.quote'); return c ? c.offsetWidth + 40 : 300; };
    wrap.querySelector('.prev').addEventListener('click', function () {
      if (track.scrollLeft <= 4) track.scrollTo({ left: track.scrollWidth, behavior: 'smooth' });
      else track.scrollBy({ left: -step(), behavior: 'smooth' });
    });
    wrap.querySelector('.next').addEventListener('click', function () {
      if (track.scrollLeft + track.clientWidth >= track.scrollWidth - 4) track.scrollTo({ left: 0, behavior: 'smooth' });
      else track.scrollBy({ left: step(), behavior: 'smooth' });
    });
  });

  // Zoho forms: build the iframe (passes the page as referrer, like Zoho's own embed code)
  document.querySelectorAll('.zform[data-src]').forEach(function (box) {
    var src = box.getAttribute('data-src');
    src += (src.indexOf('?') > 0 ? '&' : '?') + 'referrername=' + encodeURIComponent(location.href.split('?')[0]);
    var f = document.createElement('iframe');
    f.src = src;
    f.title = box.getAttribute('data-title') || 'Contact form';
    f.style.height = (box.getAttribute('data-h') || '600') + 'px';
    f.setAttribute('aria-label', f.title);
    box.appendChild(f);
  });
  // Zoho posts "permalink|height" when the form changes size
  window.addEventListener('message', function (e) {
    if (typeof e.data !== 'string' || !/zohopublic|zoho|forms\.entrechatpress\.com/.test(e.origin)) return;
    var parts = e.data.split('|');
    if (parts.length < 2) return;
    var h = parseInt(parts[1], 10);
    if (!h) return;
    document.querySelectorAll('.zform iframe').forEach(function (f) {
      if (f.src.indexOf(parts[0]) > -1) f.style.height = (h + 15) + 'px';
    });
  });

  // YouTube: load the player only when someone presses play
  document.querySelectorAll('.video button[data-yt]').forEach(function (b) {
    var id = b.getAttribute('data-yt');
    b.style.backgroundImage = 'url(https://i.ytimg.com/vi/' + id + '/hqdefault.jpg)';
    b.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      f.title = b.getAttribute('aria-label') || 'Video';
      b.replaceWith(f);
    });
  });

  // Build Your Book buttons pop when they come into view, then again every 7 seconds while visible
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
    var pop = function (b) { b.classList.remove('popping'); void b.offsetWidth; b.classList.add('popping'); };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var b = e.target;
        if (e.isIntersecting) {
          setTimeout(function () { pop(b); }, 300);
          b._popTimer = setInterval(function () { pop(b); }, 7000);
        } else { clearInterval(b._popTimer); }
      });
    }, { threshold: 0.8 });
    document.querySelectorAll('a.btn[href="/contact/"]').forEach(function (b) {
      b.addEventListener('animationend', function () { b.classList.remove('popping'); });
      io.observe(b);
    });
  }
})();
