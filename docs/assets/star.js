// 밤하늘: 처음엔 별들이 화면 가운데서 쫙 펼쳐지고, 이후엔 반짝이며 가끔 별똥별이 떨어진다.
// 장을 넘길 때마다 별들이 깊이에 따라 조금씩 다른 속도로 흘러 입체감이 난다.
(() => {
  const cv = document.getElementById("sky");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const track = document.querySelector(".track");
  let W = 0, H = 0, dpr = 1, stars = [], shooting = [];
  const t0 = performance.now();
  const SPREAD = calm ? 0 : 2600;

  function resize() {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = innerWidth; H = innerHeight;
    cv.width = W * dpr; cv.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.min(900, Math.round((W * H) / 1700));
    stars = Array.from({ length: n }, () => {
      const depth = Math.random();
      // 은하수 띠 쪽으로 조금 더 몰리게
      let x = Math.random(), y = Math.random();
      if (Math.random() < 0.35) y = Math.min(1, Math.max(0, 0.15 + x * 0.6 + (Math.random() - 0.5) * 0.18));
      const tint = Math.random();
      return {
        x, y, depth,
        r: 0.25 + depth * depth * 1.6,
        a: 0.35 + Math.random() * 0.65,
        tw: 0.6 + Math.random() * 2.2, ph: Math.random() * 6.28,
        c: tint < 0.12 ? "255,226,170" : tint < 0.3 ? "190,205,255" : "255,255,255",
      };
    });
  }
  resize();
  addEventListener("resize", resize);

  const ease = (p) => 1 - Math.pow(1 - p, 3);
  let scroll = 0;

  function frame(now) {
    const t = (now - t0) / 1000;
    const p = SPREAD ? ease(Math.min(1, (now - t0) / SPREAD)) : 1;
    const idx = parseFloat(track?.style.getPropertyValue("--idx") || "0") || 0;
    scroll += (idx - scroll) * 0.06;
    ctx.clearRect(0, 0, W, H);
    const cx = W / 2, cy = H / 2;
    for (const s of stars) {
      let x = s.x * W, y = s.y * H - scroll * (8 + s.depth * 40);
      y = ((y % H) + H) % H;
      x = cx + (x - cx) * p;
      y = cy + (y - cy) * p;
      const tw = calm ? 1 : 0.65 + 0.35 * Math.sin(t * s.tw + s.ph);
      const a = s.a * tw * Math.min(1, p * 1.4);
      ctx.beginPath();
      ctx.fillStyle = `rgba(${s.c},${a})`;
      ctx.arc(x, y, s.r, 0, 6.283);
      ctx.fill();
      if (s.r > 1.4) {
        ctx.fillStyle = `rgba(${s.c},${a * 0.12})`;
        ctx.beginPath(); ctx.arc(x, y, s.r * 4, 0, 6.283); ctx.fill();
      }
    }
    if (!calm && p >= 1 && Math.random() < 0.004) {
      shooting.push({ x: Math.random() * W * 0.8 + W * 0.2, y: Math.random() * H * 0.4, life: 0 });
    }
    shooting = shooting.filter((s) => s.life < 1);
    for (const s of shooting) {
      s.life += 0.018;
      const len = 140, dx = -Math.cos(0.5) * len, dy = Math.sin(0.5) * len;
      const hx = s.x + dx * s.life * 4, hy = s.y + dy * s.life * 4;
      const g = ctx.createLinearGradient(hx, hy, hx - dx, hy - dy);
      g.addColorStop(0, `rgba(255,255,255,${0.9 * (1 - s.life)})`);
      g.addColorStop(1, "rgba(255,255,255,0)");
      ctx.strokeStyle = g; ctx.lineWidth = 1.4;
      ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(hx - dx, hy - dy); ctx.stroke();
    }
    if (!calm) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
