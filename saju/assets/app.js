// 슬라이드 덱: 휠·스와이프·키 한 번에 정확히 한 장. 그리고 매화 꽃잎.
(() => {
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const track = document.querySelector(".track");
  const slides = [...document.querySelectorAll(".slide")];
  if (!track || !slides.length) return;

  // 내비게이션 UI
  const dots = document.createElement("nav");
  dots.className = "dots";
  dots.setAttribute("aria-label", "섹션 이동");
  slides.forEach((s, i) => {
    const b = document.createElement("button");
    b.innerHTML = `<span>${String(i).padStart(2, "0")} ${s.dataset.nav || ""}</span>`;
    b.setAttribute("aria-label", s.dataset.nav || `섹션 ${i}`);
    b.addEventListener("click", () => go(i));
    dots.appendChild(b);
  });
  const counter = Object.assign(document.createElement("div"), { className: "counter" });
  const bar = Object.assign(document.createElement("div"), { className: "progress" });
  const hint = Object.assign(document.createElement("div"), { className: "nav-hint", textContent: "휠 · 스와이프 · ↑↓ 로 한 장씩" });
  document.body.append(dots, counter, bar, hint);

  // 슬라이드 높이 = 지금 실제로 보이는 화면 높이. 모바일 주소창이 접히고 펴져도 어긋나지 않게.
  const setHeight = () => {
    const h = (window.visualViewport?.height || innerHeight);
    document.documentElement.style.setProperty("--h", `${Math.round(h)}px`);
  };
  setHeight();
  addEventListener("resize", setHeight);
  window.visualViewport?.addEventListener("resize", setHeight);

  // 문서 자체는 절대 스크롤되지 않게 한다 (스크롤 복원, 포커스 이동 등으로 밀리는 것 방지)
  history.scrollRestoration = "manual";
  document.documentElement.style.overflow = "hidden";
  addEventListener("scroll", () => { if (scrollY) scrollTo(0, 0); });

  let idx = -1;
  let lastMove = 0;   // 마지막으로 장을 넘긴 시각
  let lastWheel = 0;  // 마지막 휠 이벤트 시각 (관성 스크롤 묶음 판별)
  let lastInner = 0;  // 슬라이드 안쪽 스크롤에 휠을 쓴 시각
  let lastAbs = 0;    // 직전 휠 세기 (관성은 점점 약해지고, 새 제스처는 다시 세진다)
  const LOCK = calm ? 250 : 550;

  function go(n) {
    n = Math.max(0, Math.min(slides.length - 1, n));
    if (n === idx) return;
    if (idx >= 0) {
      const prev = slides[idx];
      prev.classList.remove("active");
      prev.classList.add("leaving");
      clearTimeout(prev._leave);
      prev._leave = setTimeout(() => prev.classList.remove("leaving"), 1100);
    }
    idx = n;
    const s = slides[idx];
    clearTimeout(s._leave);
    s.classList.remove("leaving");
    s.classList.add("active");
    s.querySelector(".slide-inner")?.scrollTo(0, 0);
    track.style.setProperty("--idx", idx);
    scrollTo(0, 0);
    [...dots.children].forEach((d, i) => d.classList.toggle("on", i === idx));
    counter.innerHTML = `<b>${String(idx + 1).padStart(2, "0")}</b> / ${String(slides.length).padStart(2, "0")}`;
    bar.style.width = `${(idx / (slides.length - 1)) * 100}%`;
    if (idx > 0) hint.classList.add("gone");
    history.replaceState(null, "", idx ? `#${idx}` : location.pathname);
    lastMove = performance.now();
  }

  const inner = () => slides[idx].querySelector(".slide-inner");
  // 안쪽 스크롤은 모바일에서, 진짜로 내용이 넘칠 때만 쓴다.
  // (등장 애니메이션 중인 요소가 잠깐 아래로 밀려 생기는 작은 넘침은 무시)
  const canScroll = (el, dir) =>
    el && innerWidth <= 700 && el.scrollHeight - el.clientHeight > 40 &&
    (dir > 0 ? el.scrollTop + el.clientHeight < el.scrollHeight - 2 : el.scrollTop > 1);

  addEventListener("wheel", (e) => {
    const dir = Math.sign(e.deltaY);
    if (!dir) return;
    const now = performance.now();
    const gap = now - lastWheel;
    const abs = Math.abs(e.deltaY);
    const stronger = abs > lastAbs * 1.5 && abs > 15;
    lastWheel = now;
    lastAbs = abs;
    // 내용이 긴 장은 안쪽부터 끝까지 읽게 한다
    if (canScroll(inner(), dir)) { lastInner = now; return; }
    e.preventDefault();
    if (now - lastInner < 300) return;              // 안쪽 스크롤 끝에 닿은 같은 제스처
    if (now - lastMove < LOCK) return;              // 막 넘어가는 중
    if (gap < 120 && !stronger) return;             // 약해지는 관성 스크롤은 같은 제스처로 본다
    go(idx + dir);
  }, { passive: false });

  let y0 = null;
  let innerTop0 = 0;
  addEventListener("touchstart", (e) => {
    y0 = e.touches[0].clientY;
    innerTop0 = inner()?.scrollTop || 0;
  }, { passive: true });
  addEventListener("touchmove", (e) => {
    const el = e.target.closest(".slide-inner");
    if (!el || el.scrollHeight <= el.clientHeight + 2) e.preventDefault();
  }, { passive: false });
  addEventListener("touchend", (e) => {
    if (y0 === null) return;
    const dy = y0 - e.changedTouches[0].clientY;
    y0 = null;
    if (Math.abs(dy) < 50 || performance.now() - lastMove < LOCK) return;
    const dir = Math.sign(dy);
    const el = inner();
    // 이번 터치로 안쪽이 스크롤됐거나, 아직 더 스크롤할 게 있으면 장을 넘기지 않는다
    if (el && (Math.abs(el.scrollTop - innerTop0) > 2 || canScroll(el, dir))) return;
    go(idx + dir);
  }, { passive: true });

  addEventListener("keydown", (e) => {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    const k = e.key;
    if (["ArrowDown", "PageDown", " "].includes(k)) { e.preventDefault(); go(idx + 1); }
    else if (["ArrowUp", "PageUp"].includes(k)) { e.preventDefault(); go(idx - 1); }
    else if (k === "Home") { e.preventDefault(); go(0); }
    else if (k === "End") { e.preventDefault(); go(slides.length - 1); }
  });

  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-go]");
    if (!t) return;
    go(t.dataset.go === "next" ? idx + 1 : Number(t.dataset.go));
  });

  // 데스크톱에선 화면보다 긴 장을 살짝 축소해 한 화면에 맞춘다 (휠이 안쪽 스크롤에 걸리지 않게).
  // 모바일은 손가락으로 읽는 게 자연스러워서 안쪽 스크롤을 그대로 둔다.
  const fit = () => slides.forEach((s) => {
    const el = s.querySelector(".slide-inner");
    if (!el) return;
    el.style.cssText = "";
    if (innerWidth <= 700) return;
    const h = s.clientHeight, H = el.scrollHeight;
    if (H > h + 2) {
      // 안쪽 스크롤을 끄고, 내용 높이 그대로 둔 채 화면 높이에 맞게 줄인다
      el.style.cssText = `max-height:none;height:${H}px;overflow:visible;flex:none;` +
        `transform-origin:top center;transform:scale(${(h / H).toFixed(3)})`;
    }
  });
  fit();
  document.fonts?.ready.then(fit);
  addEventListener("resize", fit);

  // 화면보다 긴 장(주로 모바일)은 아래쪽에 '더 보기' 표시를 띄운다
  const markMore = (s) => {
    const el = s.querySelector(".slide-inner");
    if (el) s.classList.toggle("more", el.scrollTop + el.clientHeight < el.scrollHeight - 8);
  };
  slides.forEach((s) => s.querySelector(".slide-inner")?.addEventListener("scroll", () => markMore(s), { passive: true }));
  addEventListener("resize", () => slides.forEach(markMore));
  slides.forEach(markMore);

  go(Number(location.hash.slice(1)) || 0);
  addEventListener("hashchange", () => go(Number(location.hash.slice(1)) || 0));

  const box = document.querySelector(".petals");
  if (box && !calm) {
    const n = innerWidth < 600 ? 10 : 18;
    for (let i = 0; i < n; i++) {
      const s = document.createElement("span");
      s.className = "petal";
      const size = 8 + Math.random() * 8;
      s.style.cssText =
        `left:${Math.random() * 100}vw;width:${size}px;height:${size}px;` +
        `animation-duration:${9 + Math.random() * 9}s;animation-delay:${2 + Math.random() * 12}s;` +
        `--sway:${(Math.random() * 30 - 15).toFixed(1)}vw;opacity:${0.5 + Math.random() * 0.4}`;
      box.appendChild(s);
    }
  }
})();
