/* ═══════════════════════════════════════════════════════════════
   金庸人物志研究院 — 水墨粒子动画 Canvas
   ═══════════════════════════════════════════════════════════════ */
(function(){
  const canvas = document.createElement('canvas');
  canvas.className = 'ink-particles';
  document.body.prepend(canvas);
  const ctx = canvas.getContext('2d');
  
  let W,H;
  const particles = [];
  const MAX = 60;
  
  function resize(){
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);
  
  class InkParticle {
    constructor(){
      this.reset(true);
    }
    reset(initial){
      this.x = Math.random() * W;
      this.y = initial ? Math.random() * H : H + 20;
      this.size = Math.random() * 2.5 + 0.5;
      this.speed = Math.random() * 0.4 + 0.1;
      this.drift = (Math.random() - 0.5) * 0.3;
      this.opacity = Math.random() * 0.5 + 0.1;
      this.life = Math.random() * 600 + 300;
      this.age = initial ? Math.random() * this.life : 0;
      this.type = Math.floor(Math.random() * 3); // 0=墨点 1=金粉 2=微光
    }
    update(){
      this.y -= this.speed;
      this.x += this.drift + Math.sin(this.age * 0.02) * 0.15;
      this.age++;
      if(this.y < -20 || this.age > this.life) this.reset(false);
    }
    draw(ctx){
      const alpha = this.opacity * (1 - this.age / this.life);
      if(this.type === 0){
        // 墨点
        ctx.fillStyle = `rgba(180,160,140,${alpha})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
        ctx.fill();
      } else if(this.type === 1){
        // 金粉
        ctx.fillStyle = `rgba(212,165,116,${alpha * 0.8})`;
        ctx.fillRect(this.x, this.y, this.size * 0.8, this.size * 0.8);
      } else {
        // 微光
        const g = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size * 3);
        g.addColorStop(0, `rgba(200,180,150,${alpha})`);
        g.addColorStop(1, 'rgba(200,180,150,0)');
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI*2);
        ctx.fill();
      }
    }
  }
  
  for(let i=0; i<MAX; i++) particles.push(new InkParticle());
  
  function animate(){
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => { p.update(); p.draw(ctx); });
    requestAnimationFrame(animate);
  }
  animate();
})();
