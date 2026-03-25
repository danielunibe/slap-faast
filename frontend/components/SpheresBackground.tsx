import React, { useEffect, useRef } from 'react';
import { useBackground, LIGHT_VARIANTS } from '../context/BackgroundContext';
import { AuroraBackground, PulseBackground, MetroBackground } from './XboxBackgrounds';
import FluidBackground from './FluidBackground';
import GlimmerBackground from './GlimmerBackground';

interface Particle {
  pos: number;
  length: number;
  speed: number;
  flare: number;
}

interface Strand {
  offset: number;
  width: number;
  alpha: number;
  glow: number;
  speed: number;
  type: 'traffic' | 'continuous';
  particles: Particle[];
}

/* ─────────────── RENDERIZADO DE ONDAS LUMINOSAS CON PARTÍCULAS Y DESTELLOS ─────────────── */
export const SpheresBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { bgMode, lightVariant } = useBackground();
  const variant = LIGHT_VARIANTS[lightVariant] || LIGHT_VARIANTS.fiber;
  const isActive = bgMode === 'spheres';

  const hexToRgb = (hex: string) => {
    const parsed = hex.replace('#', '');
    const bigint = parseInt(parsed, 16);
    return { 
      r: (bigint >> 16) & 255, 
      g: (bigint >> 8) & 255, 
      b: bigint & 255 
    };
  };

  useEffect(() => {
    if (!isActive) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return;

    let width: number, height: number;
    let spline: any[] = [];
    let time = 0;
    let animationFrameId: number;
    const primary = hexToRgb(variant.primary);
    const accent = hexToRgb(variant.accent);
    const primaryColor = (a: number) => `rgba(${primary.r},${primary.g},${primary.b},${a})`;
    const accentColor = (a: number) => `rgba(${accent.r},${accent.g},${accent.b},${a})`;
    const backgroundColor = variant.background;
    const speedBoost = variant.speed;
    const glowBoost = variant.glow;

    const strands: Strand[] = [
      { offset: -70, width: 0.5, alpha: 0.15, glow: 0, speed: 0.5, type: 'traffic', particles: [] },
      { offset: -50, width: 1, alpha: 0.3, glow: 5, speed: 0.8, type: 'traffic', particles: [] },
      { offset: -35, width: 2, alpha: 0.5, glow: 10, speed: 1.1, type: 'traffic', particles: [] },
      { offset: -22, width: 1.5, alpha: 0.8, glow: 15, speed: 1.3, type: 'traffic', particles: [] },
      { offset: -10, width: 3, alpha: 1.0, glow: 20, speed: 1.6, type: 'traffic', particles: [] },
      { offset: -2, width: 1.5, alpha: 0.9, glow: 12, speed: 1.8, type: 'traffic', particles: [] },
      { offset: 5, width: 1.5, alpha: 0.85, glow: 15, speed: 1.7, type: 'traffic', particles: [] },
      { offset: 14, width: 2.5, alpha: 0.7, glow: 10, speed: 1.4, type: 'traffic', particles: [] },
      { offset: 25, width: 1.2, alpha: 0.4, glow: 5, speed: 1.0, type: 'traffic', particles: [] },
      { offset: 40, width: 2, alpha: 0.3, glow: 8, speed: 0.7, type: 'traffic', particles: [] },
      { offset: 55, width: 0.8, alpha: 0.15, glow: 0, speed: 0.4, type: 'traffic', particles: [] },
      { offset: 75, width: 4.5, alpha: 1.0, glow: 25, speed: 1.5, type: 'continuous', particles: [] }
    ];

    function init() {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      spline = [];

      const x_left = width * 0.20;
      const x_right = width * 0.80;
      const y_mid = height * 0.50;
      const r = Math.min(height * 0.35, Math.abs(x_right - x_left) * 0.45);
      const step = 4;

      for (let y = -100; y <= y_mid - r; y += step) spline.push({ x: x_left, y });

      const cx1 = x_left + r, cy1 = y_mid - r;
      const arcSteps = Math.floor((Math.PI / 2 * r) / step);
      for (let i = 0; i <= arcSteps; i++) {
        const angle = Math.PI - (i / arcSteps) * (Math.PI / 2);
        spline.push({ x: cx1 + r * Math.cos(angle), y: cy1 + r * Math.sin(angle) });
      }

      for (let x = x_left + r; x <= x_right - r; x += step) spline.push({ x, y: y_mid });

      const cx2 = x_right - r, cy2 = y_mid + r;
      for (let i = 0; i <= arcSteps; i++) {
        const angle = -Math.PI / 2 + (i / arcSteps) * (Math.PI / 2);
        spline.push({ x: cx2 + r * Math.cos(angle), y: cy2 + r * Math.sin(angle) });
      }

      for (let y = y_mid + r; y <= height + 100; y += step) spline.push({ x: x_right, y });

      for (let i = 0; i < spline.length; i++) {
        const p_curr = spline[i];
        const p_next = spline[i + 1] || spline[i];
        const p_prev = spline[i - 1] || spline[i];
        let dx = i === 0 ? p_next.x - p_curr.x : i === spline.length - 1 ? p_curr.x - p_prev.x : p_next.x - p_prev.x;
        let dy = i === 0 ? p_next.y - p_curr.y : i === spline.length - 1 ? p_curr.y - p_prev.y : p_next.y - p_prev.y;
        const mag = Math.sqrt(dx * dx + dy * dy) || 1;
        p_curr.normal = { x: -dy / mag, y: dx / mag };
      }

      strands.forEach(strand => {
        strand.particles = [];
        if (strand.type === 'traffic') {
          const numParticles = Math.floor(Math.random() * 4) + 3;
          for (let i = 0; i < numParticles; i++) {
            strand.particles.push({
              pos: Math.random() * spline.length,
              length: Math.random() * 40 + 10,
              speed: strand.speed * speedBoost * (Math.random() * 0.6 + 0.7),
              flare: 0
            });
          }
        } else {
          for (let i = 0; i < 2; i++) {
            strand.particles.push({ pos: Math.random() * spline.length, length: 20, speed: strand.speed * speedBoost * 2, flare: 0 });
          }
        }
      });
    }

    function draw() {
      ctx.fillStyle = backgroundColor;
      ctx.fillRect(0, 0, width, height);
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';

      strands.forEach(strand => {
        if (strand.type === 'continuous') {
          ctx.shadowColor = 'transparent';
          ctx.shadowBlur = 0;

          for (let i = 0; i < spline.length - 1; i++) {
            const node = spline[i];
            const nextNode = spline[i + 1];
            const px1 = node.x + node.normal.x * strand.offset, py1 = node.y + node.normal.y * strand.offset;
            const px2 = nextNode.x + nextNode.normal.x * strand.offset, py2 = nextNode.y + nextNode.normal.y * strand.offset;

            const wave = (Math.sin(i * 0.05 - time * strand.speed * speedBoost * 0.05) + Math.sin(i * 0.12 + time * 0.02) + 2) / 4;
            const currentWidth = strand.width * (0.3 + wave * 1.5);
            const currentAlpha = strand.alpha * (0.2 + wave * 0.8);

            ctx.beginPath();
            ctx.moveTo(px1, py1); ctx.lineTo(px2, py2);
            ctx.lineWidth = currentWidth * 3.5;
            ctx.strokeStyle = primaryColor(currentAlpha * 0.15);
            ctx.stroke();

            ctx.lineWidth = currentWidth;
            ctx.strokeStyle = accentColor(currentAlpha);
            ctx.stroke();
          }

          strand.particles.forEach(p => {
            p.pos += p.speed;
            if (p.pos > spline.length) p.pos = 0;
            if (Math.random() < 0.005) p.flare = 1.0;
            p.flare *= 0.92;

            if (p.flare > 0.1) {
              let idx = Math.floor(p.pos);
              if (idx >= spline.length - 1) idx = spline.length - 2;
              const node = spline[idx];
              const px = node.x + node.normal.x * strand.offset;
              const py = node.y + node.normal.y * strand.offset;
              ctx.beginPath();
              ctx.arc(px, py, strand.width * 2 * p.flare, 0, Math.PI * 2);
              ctx.fillStyle = accentColor(p.flare);
              ctx.shadowColor = accentColor(p.flare);
              ctx.shadowBlur = 30 * p.flare * glowBoost;
              ctx.fill();
            }
          });
        } else {
          strand.particles.forEach(p => {
            p.pos += p.speed;
            if (p.pos - p.length > spline.length) {
              p.pos = 0;
              p.length = Math.random() * 50 + 10;
              p.speed = strand.speed * speedBoost * (Math.random() * 0.6 + 0.7);
              p.flare = 0;
            }
            if (Math.random() < 0.002) p.flare = 1.0;
            p.flare *= 0.94;

            let startIdx = Math.floor(p.pos);
            let endIdx = Math.floor(p.pos - p.length);
            if (startIdx >= spline.length) startIdx = spline.length - 1;
            if (endIdx < 0) endIdx = 0;
            if (startIdx <= endIdx) return;

            ctx.beginPath();
            for (let i = endIdx; i <= startIdx; i++) {
              const node = spline[i];
              const px = node.x + node.normal.x * strand.offset;
              const py = node.y + node.normal.y * strand.offset;
              if (i === endIdx) ctx.moveTo(px, py);
              else ctx.lineTo(px, py);
            }

            const flareBoost = p.flare * 25;
            const coreColor = accentColor(strand.alpha);
            ctx.shadowColor = 'transparent';
            ctx.lineWidth = strand.width * 6;
            ctx.strokeStyle = primaryColor(strand.alpha * 0.15);
            ctx.stroke();

            ctx.lineWidth = strand.width + (p.flare * 1.5);
            ctx.strokeStyle = coreColor;
            ctx.shadowColor = accentColor(strand.alpha);
            ctx.shadowBlur = (strand.glow + flareBoost) * glowBoost;
            ctx.stroke();
          });
        }
      });
    }

    function animate() {
      time++;
      draw();
      animationFrameId = requestAnimationFrame(animate);
    }

    window.addEventListener('resize', init);
    init();
    animate();

    return () => {
      window.removeEventListener('resize', init);
      cancelAnimationFrame(animationFrameId);
    };
  }, [isActive, lightVariant]);

  return (
    <div 
      style={{ 
        position: 'fixed', 
        inset: 0, 
        zIndex: 0, 
        pointerEvents: 'none', 
        opacity: isActive ? 1 : 0, 
        transition: 'opacity 1s ease',
        background: '#030a05' 
      }}
    >
      {isActive && <canvas ref={canvasRef} style={{ display: 'block', width: '100vw', height: '100vh' }} />}
    </div>
  );
};

export { AuroraBackground, PulseBackground, MetroBackground, FluidBackground, GlimmerBackground };
