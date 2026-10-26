// 스크롤 등장 효과, 인트로 패럴랙스, 매화 꽃잎
(() => {
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      // 빠르게 스크롤해 화면 위로 지나간 요소도 켜 둔다
      if (e.isIntersecting || e.boundingClientRect.top < 0) {
        e.target.classList.add("in");
        io.unobserve(e.target);
      }
    }
  }, { threshold: 0.18, rootMargin: "0px 0px -6% 0px" });
  document.querySelectorAll(".reveal, .stamp").forEach((el) => io.observe(el));

  const hero = document.querySelector(".hero");
  if (hero && !calm) {
    let ticking = false;
    addEventListener("scroll", () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const p = Math.min(1, scrollY / innerHeight);
        hero.style.setProperty("--p", p.toFixed(3));
        ticking = false;
      });
    }, { passive: true });
  }

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
