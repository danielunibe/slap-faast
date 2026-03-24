import React, { useEffect, useRef } from 'react';
import { useBackground } from '../context/BackgroundContext';

const BAND_DEFS = [
  { pos: 0.152, brightness: 0.7,  r: 120, g: 230, b: 240 },
  { pos: 0.185, brightness: 0.5,  r:  80, g: 200, b: 220 },
  { pos: 0.252, brightness: 0.85, r: 150, g: 240, b: 255 },
  { pos: 0.375, brightness: 1.0,  r: 220, g: 255, b: 255 },
  { pos: 0.425, brightness: 0.9,  r:  60, g: 190, b: 220 },
  { pos: 0.485, brightness: 0.75, r:  30, g: 140, b: 180 },
  { pos: 0.652, brightness: 0.65, r: 100, g: 220, b: 240 },
  { pos: 0.708, brightness: 0.45, r:  50, g: 160, b: 190 },
  { pos: 0.801, brightness: 0.35, r:  20, g: 100, b: 130 },
];

const ANGLE = (125 - 90) * Math.PI / 180; // 35°
const COS = Math.cos(ANGLE);
const SIN = Math.sin(ANGLE);

const GlimmerBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { bgMode, glimmerConfig, currentPalette } = useBackground();
  const reqRef = useRef<number>();
  const configRef = useRef(glimmerConfig);

  useEffect(() => { configRef.current = glimmerConfig; }, [glimmerConfig]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let W = 0, H = 0;
    const resize = () => { W = canvas.width = canvas.offsetWidth; H = canvas.height = canvas.offsetHeight; };
    resize();
    window.addEventListener('resize', resize);

    // Extraer RGB del tileAccent (asumiendo hex o algo compatible)
    const hexToRgb = (hex: string) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : { r: 163, g: 255, b: 0 }; // Default Xbox Green
    };
    const rgb = hexToRgb(currentPalette.tileAccent);

    class Glimmer {
      x: number = 0; y: number = 0; t: number = 0; speed: number = 0; size: number = 0; alpha: number = 0;
      angle: number = (125 * Math.PI) / 180;
      done: boolean = false;

      constructor() { this.spawn(); }
      spawn() {
        this.t = -0.2 - Math.random() * 0.4;
        this.speed = configRef.current.speed * (0.7 + Math.random() * 0.6);
        this.size = 0.05 + Math.random() * 0.15;
        this.alpha = configRef.current.intensity * (0.4 + Math.random() * 0.5);
        this.x = Math.random() * W;
        this.y = Math.random() * H;
        this.done = false;
      }
      update(dt: number) { this.t += this.speed * dt; if (this.t > 1.2) this.done = true; }
      draw() {
        if (!ctx) return;
        const travel = Math.sqrt(W * W + H * H);
        const distance = (this.t - 0.5) * travel;
        const cx = this.x + distance * Math.cos(this.angle);
        const cy = this.y + distance * Math.sin(this.angle);
        const len = this.size * travel * 0.4;
        const x0 = cx - len * Math.cos(this.angle);
        const y0 = cy - len * Math.sin(this.angle);
        const x1 = cx + len * Math.cos(this.angle);
        const y1 = cy + len * Math.sin(this.angle);

        const a = this.alpha * Math.sin(this.t * Math.PI); // Fade in out
        if (a <= 0) return;

        const grad = ctx.createLinearGradient(x0, y0, x1, y1);
        grad.addColorStop(0, `rgba(${rgb.r},${rgb.g},${rgb.b},0)`);
        grad.addColorStop(0.5, `rgba(255,255,255,${a})`);
        grad.addColorStop(1, `rgba(${rgb.r},${rgb.g},${rgb.b},0)`);

        ctx.beginPath();
        ctx.moveTo(x0, y0);
        ctx.lineTo(x1, y1);
        ctx.strokeStyle = grad;
        ctx.lineWidth = 2;
        ctx.stroke();

        const halo = ctx.createRadialGradient(cx, cy, 0, cx, cy, len * 0.5);
        halo.addColorStop(0, `rgba(${rgb.r},${rgb.g},${rgb.b},${a * 0.3})`);
        halo.addColorStop(1, `rgba(${rgb.r},${rgb.g},${rgb.b},0)`);
        ctx.fillStyle = halo;
        ctx.beginPath();
        ctx.arc(cx, cy, len * 0.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    const pool = Array.from({ length: 15 }, () => new Glimmer());
    let lastTime: number | null = null;
    const render = (ts: number) => {
      if (lastTime === null) lastTime = ts;
      const dt = (ts - lastTime) / 1000;
      lastTime = ts;
      ctx.clearRect(0, 0, W, H);
      pool.forEach(g => { g.update(dt); g.draw(); if (g.done) g.spawn(); });
      reqRef.current = requestAnimationFrame(render);
    };
    reqRef.current = requestAnimationFrame(render);
    return () => {
      window.removeEventListener('resize', resize);
      if (reqRef.current) cancelAnimationFrame(reqRef.current);
    };
  }, [currentPalette]);

  return (
    <div className="fixed inset-0 w-full h-full pointer-events-none z-0 overflow-hidden animate-in fade-in duration-1000" style={{ background: 'linear-gradient(215deg, #051a28 0%, #010408 80%)' }}>
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full mix-blend-screen" />
    </div>
  );
};

export default GlimmerBackground;
