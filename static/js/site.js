/* yichengs — site scripts (no dependencies) */
(function () {
	'use strict';

	var root = document.documentElement;
	var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

	// 深淺色切換（記住使用者的選擇）
	var themeToggle = document.querySelector('[data-theme-toggle]');
	if (themeToggle) {
		themeToggle.addEventListener('click', function () {
			var dark = root.dataset.theme
				? root.dataset.theme === 'dark'
				: window.matchMedia('(prefers-color-scheme: dark)').matches;
			var next = dark ? 'light' : 'dark';
			root.dataset.theme = next;
			try { localStorage.setItem('theme', next); } catch (e) { /* storage unavailable */ }
		});
	}

	// 捲動後顯示 header 底線
	var header = document.querySelector('[data-header]');
	if (header) {
		var onScroll = function () { header.classList.toggle('is-scrolled', window.scrollY > 8); };
		window.addEventListener('scroll', onScroll, { passive: true });
		onScroll();
	}

	// 手機版選單
	var navToggle = document.querySelector('[data-nav-toggle]');
	var nav = document.getElementById('site-nav');
	if (navToggle && nav) {
		var setOpen = function (open) {
			nav.classList.toggle('is-open', open);
			navToggle.setAttribute('aria-expanded', String(open));
			var icon = navToggle.querySelector('i');
			if (icon) icon.className = open ? 'fas fa-times' : 'fas fa-bars';
		};
		navToggle.addEventListener('click', function () {
			setOpen(!nav.classList.contains('is-open'));
		});
		document.addEventListener('keydown', function (e) {
			if (e.key === 'Escape' && nav.classList.contains('is-open')) {
				setOpen(false);
				navToggle.focus();
			}
		});
		document.addEventListener('click', function (e) {
			if (nav.classList.contains('is-open') && !header.contains(e.target)) setOpen(false);
		});
	}

	// 首頁照片輪播
	document.querySelectorAll('[data-slider]').forEach(function (slider) {
		var slides = slider.querySelectorAll('.frame img');
		var counter = slider.querySelector('[data-slide-index]');
		if (slides.length < 2) return;
		var index = 0;
		var timer = null;

		var show = function (i) {
			slides[index].classList.remove('is-active');
			index = (i + slides.length) % slides.length;
			slides[index].classList.add('is-active');
			if (counter) counter.textContent = String(index + 1).padStart(2, '0');
		};
		var stop = function () { clearInterval(timer); timer = null; };
		var start = function () {
			if (reduceMotion || timer) return;
			timer = setInterval(function () { show(index + 1); }, 5000);
		};

		var prev = slider.querySelector('[data-slide-prev]');
		var next = slider.querySelector('[data-slide-next]');
		if (prev) prev.addEventListener('click', function () { stop(); show(index - 1); start(); });
		if (next) next.addEventListener('click', function () { stop(); show(index + 1); start(); });
		slider.addEventListener('mouseenter', stop);
		slider.addEventListener('mouseleave', start);
		document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });
		start();
	});

	// 捲動進場動畫
	var reveals = document.querySelectorAll('.reveal');
	if (!reduceMotion && 'IntersectionObserver' in window) {
		var observer = new IntersectionObserver(function (entries) {
			entries.forEach(function (entry) {
				if (entry.isIntersecting) {
					entry.target.classList.add('is-visible');
					observer.unobserve(entry.target);
				}
			});
		}, { rootMargin: '0px 0px -8% 0px' });
		reveals.forEach(function (el) { observer.observe(el); });
	} else {
		reveals.forEach(function (el) { el.classList.add('is-visible'); });
	}
})();
