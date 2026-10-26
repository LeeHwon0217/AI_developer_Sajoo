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

  // 문서 자체는 절대 스크롤되지 않게 한다 (스크롤 복원, 포커스 이동 등으로 밀리는 것 방지)
  history.scrollRestoration = "manual";
  document.documentElement.style.overflow = "hidden";
  addEventListener("scroll", () => { if (scrollY) scrollTo(0, 0); });

  let idx = -1;
  let lastMove = 0;   // 마지막으로 장을 넘긴 시각
  let lastWheel = 0;  // 마지막 휠 이벤트 시각 (관성 스크롤 묶음 판별)
  let lastInner = 0;  // 슬라이드 안쪽 스크롤에 휠을 쓴 시각
  const LOCK = calm ? 300 : 1000;

  function go(n) {
    n = Math.max(0, Math.min(slides.length - 1, n));
    if (n === idx) return;
    if (idx >= 0) slides[idx].classList.remove("active");
    idx = n;
    const s = slides[idx];
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
  const canScroll = (el, dir) =>
    el && (dir > 0 ? el.scrollTop + el.clientHeight < el.scrollHeight - 2 : el.scrollTop > 1);

  addEventListener("wheel", (e) => {
    const dir = Math.sign(e.deltaY);
    if (!dir) return;
    const now = performance.now();
    const gap = now - lastWheel;
    lastWheel = now;
    // 내용이 긴 장은 안쪽부터 끝까지 읽게 한다
    if (canScroll(inner(), dir)) { lastInner = now; return; }
    e.preventDefault();
    if (now - lastInner < 500) return;              // 안쪽 스크롤 끝에 닿은 같은 제스처
    if (now - lastMove < LOCK) return;              // 넘어가는 중
    if (gap < 220 && now - lastMove < 2200) return; // 트랙패드 관성으로 이어지는 같은 제스처
    go(idx + dir);
  }, { passive: false });

  let y0 = null;
  let innerTop0 = 0;
  addEventListener("touchstart", (e) => {
    y0 = e.touches[0].clientY;
    innerTop0 = inner()?.scrollTop || 0;
  }, { passive: true });
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
