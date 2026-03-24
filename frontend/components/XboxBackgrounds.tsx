import React, { useEffect, useRef } from 'react';
import { useBackground } from '../context/BackgroundContext';

/* ─────────────────────── AURORA ─────────────────────── */
export const AuroraBackground: React.FC = () => {
  const { bgMode } = useBackground();
  const isActive = bgMode === 'aurora';
  return (
    <div style={{
      position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0,
      opacity: isActive ? 1 : 0, transition: 'opacity 1.2s ease',
    }}>
      {/* Base dark */}
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(160deg, #040d0a 0%, #050505 60%, #020608 100%)' }} />
      {/* Aurora bands */}
      <div style={{
        position: 'absolute', inset: 0,
        background: `radial-gradient(ellipse 120% 60% at 50% 110%, rgba(16,124,16,0.22) 0%, transparent 70%),
                     radial-gradient(ellipse 80% 50% at 20% 80%, rgba(0,200,160,0.10) 0%, transparent 60%),
                     radial-gradient(ellipse 60% 40% at 80% 85%, rgba(150,255,0,0.08) 0%, transparent 55%)`,
        animation: 'aurora-shift 12s ease-in-out infinite alternate'
      }} />
      {/* Subtle grid */}
      <div style={{
        position: 'absolute', inset: 0,
        backgroundImage: `linear-gradient(rgba(163,255,0,0.015) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(163,255,0,0.015) 1px, transparent 1px)`,
        backgroundSize: '80px 80px'
      }} />
      <style>{`
        @keyframes aurora-shift {
          0%   { transform: translateY(0) scale(1); }
          50%  { transform: translateY(-15px) scale(1.02); }
          100% { transform: translateY(5px) scale(0.99); }
        }
      `}</style>
    </div>
  );
};

/* ─────────────────────── PULSE ─────────────────────── */
export const PulseBackground: React.FC = () => {
  const { bgMode } = useBackground();
  const isActive = bgMode === 'pulse';
  return (
    <div style={{
      position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0,
      background: '#040905',
      opacity: isActive ? 1 : 0, transition: 'opacity 1.2s ease',
    }}>
      {/* Concentric rings - Xbox guiding ring style */}
      {[300, 450, 600, 750, 930].map((r, i) => (
        <div key={i} style={{
          position: 'absolute',
          left: '50%', top: '55%',
          width: r, height: r,
          marginLeft: -r / 2, marginTop: -r / 2,
          borderRadius: '50%',
          border: `1px solid rgba(163,255,0,${0.18 - i * 0.03})`,
          animation: `pulse-ring ${3.5 + i * 0.6}s ease-in-out infinite`,
          animationDelay: `${i * 0.4}s`,
          boxShadow: `0 0 ${20 + i * 10}px rgba(16,124,16,${0.12 - i * 0.02}) inset`
        }} />
      ))}
      {/* Center glow */}
      <div style={{
        position: 'absolute', left: '50%', top: '55%',
        width: 180, height: 180, marginLeft: -90, marginTop: -90,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(163,255,0,0.18) 0%, rgba(16,124,16,0.08) 50%, transparent 75%)',
        animation: 'pulse-glow 2.5s ease-in-out infinite'
      }} />
      <style>{`
        @keyframes pulse-ring {
          0%, 100% { opacity: 0.6; transform: scale(1); }
          50%       { opacity: 1;   transform: scale(1.03); }
        }
        @keyframes pulse-glow {
          0%, 100% { opacity: 0.7; transform: scale(1) translate(-50%,-50%); }
          50%       { opacity: 1;   transform: scale(1.08) translate(-50%,-50%); }
        }
      `}</style>
    </div>
  );
};

/* ─────────────────────── METRO (Neon Waves) ─────────────────────── */
export const MetroBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { bgMode } = useBackground();
  const isActive = bgMode === 'metro';
  const reqRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let W = 0, H = 0;
    const resize = () => { W = canvas.width = canvas.offsetWidth; H = canvas.height = canvas.offsetHeight; };
    resize();
    window.addEventListener('resize', resize);

    // Definir ondas con diferentes frecuencias y colores
    const waves = [
      { freq: 0.003, amp: 80, speed: 0.4, color: 'rgba(66,165,245,0.35)', width: 2.5, yOff: 0.30 },
      { freq: 0.005, amp: 50, speed: 0.6, color: 'rgba(66,165,245,0.20)', width: 1.5, yOff: 0.35 },
      { freq: 0.004, amp: 100, speed: 0.35, color: 'rgba(30,136,229,0.25)', width: 2, yOff: 0.50 },
      { freq: 0.006, amp: 40, speed: 0.55, color: 'rgba(100,181,246,0.15)', width: 1, yOff: 0.55 },
      { freq: 0.003, amp: 90, speed: 0.3, color: 'rgba(13,71,161,0.30)', width: 3, yOff: 0.65 },
      { freq: 0.007, amp: 30, speed: 0.7, color: 'rgba(144,202,249,0.12)', width: 1, yOff: 0.70 },
      { freq: 0.002, amp: 120, speed: 0.25, color: 'rgba(21,101,192,0.22)', width: 2, yOff: 0.80 },
    ];

    let t = 0;
    let lastT = 0;
    const render = (ts: number) => {
      if (!lastT) lastT = ts;
      const dt = (ts - lastT) / 1000;
      lastT = ts;
      if (isActive) t += dt;

      ctx.clearRect(0, 0, W, H);
      if (isActive) {
        // Fondo base oscuro azulado
        ctx.fillStyle = '#030810';
        ctx.fillRect(0, 0, W, H);

        // Resplandor central
        const grd = ctx.createRadialGradient(W * 0.5, H * 0.45, 0, W * 0.5, H * 0.45, W * 0.6);
        grd.addColorStop(0, 'rgba(21,101,192,0.08)');
        grd.addColorStop(1, 'transparent');
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, W, H);

        // Dibujar ondas
        for (const w of waves) {
          ctx.beginPath();
          const baseY = H * w.yOff;
          for (let x = 0; x <= W; x += 3) {
            const y = baseY +
              Math.sin(x * w.freq + t * w.speed) * w.amp +
              Math.sin(x * w.freq * 2.3 + t * w.speed * 0.7) * w.amp * 0.3;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }
          ctx.strokeStyle = w.color;
          ctx.lineWidth = w.width;
          ctx.stroke();
        }
      }
      reqRef.current = requestAnimationFrame(render);
    };
    reqRef.current = requestAnimationFrame(render);

    return () => {
      window.removeEventListener('resize', resize);
      if (reqRef.current) cancelAnimationFrame(reqRef.current);
    };
  }, [isActive]);

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', opacity: isActive ? 1 : 0, transition: 'opacity 1.2s ease' }}>
      <canvas ref={canvasRef} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }} />
    </div>
  );
};
