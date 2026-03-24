import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Info, Settings2, ChevronUp, ChevronDown, Minus, Play, Hand, Target, Camera, Monitor, Mic, Video, Globe } from 'lucide-react';
import { TileData, TileSize } from '../types';
import { KinectService } from '../services/kinectService';
import { 
  useBackground, 
  BackgroundMode, 
  FLUID_PRESETS 
} from '../context/BackgroundContext';

interface TileProps {
  data: TileData;
  onClick: (data: TileData) => void;
}

const Tile: React.FC<TileProps> = ({ data, onClick }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const { bgMode, setBgMode, colorMode, setColorMode, currentPalette, fluidConfig, updateFluidConfig, glimmerConfig, updateGlimmerConfig, preferences, updatePreferences } = useBackground();
  const [motorAngle, setMotorAngle] = useState(0);
  const [ledMode, setLedMode] = useState('GRN');
  const [videoActive, setVideoActive] = useState(true);
  const [depthActive, setDepthActive] = useState(true);
  const [depthColormap, setDepthColormap] = useState(2);
  const [gestureSensitivity, setGestureSensitivity] = useState(50);
  const [sensorType, setSensorType] = useState<'KINECT' | 'WEBCAM'>('KINECT');
  const [kinectStatus, setKinectStatus] = useState<any>(null);
  const [cameras, setCameras] = useState<MediaDeviceInfo[]>([]);
  const [mics, setMics] = useState<MediaDeviceInfo[]>([]);

  // Helper para traducir strings estáticos (ES/EN)
  const t = (text: string) => {
    if (preferences.language === 'en') return text;
    const dict: Record<string, string> = {
      'dashboard': 'tablero',
      'gestures': 'gestos',
      'advanced controls': 'control avanzado',
      'magic hand': 'mano mágica',
      'kinect test': 'prueba kinect',
      'settings': 'ajustes',
      'Total Gestures': 'Gestos Totales',
      'Lifetime': 'Histórico',
      'Accuracy': 'Precisión',
      'Session': 'Sesión',
      'Active Time': 'Tiempo Activo',
      'Today': 'Hoy',
      'Top Gesture': 'Gesto Principal',
      'Most Used': 'Más Usado',
      'Errors': 'Errores',
      'Logs': 'Registros',
      'New Gesture': 'Nuevo Gesto',
      'Record': 'Grabar',
      'Sensitivity': 'Sensibilidad',
      'Fine Tune': 'Ajuste Fino',
      'Test Zone': 'Zona de Prueba',
      'Sandbox': 'Pruebas',
      'Redo Last': 'Rehacer',
      'Clear All': 'Limpiar Todo',
      'Image Analyzer': 'Analizador Imagen',
      'Process Stream': 'Procesar Flujo',
      'Object Detect': 'Detector Objetos',
      'Bounding Box': 'Recuadro',
      'Smart Crop': 'Recorte Inteligente',
      'Auto-Frame': 'Auto-Encuadre',
      'Filters': 'Filtros',
      'FX Library': 'Biblioteca FX',
      'Contrast': 'Contraste',
      'Adjust': 'Ajustar',
      'Depth Map': 'Mapa de Profundidad',
      'Visualizer': 'Visualizador',
      'Hand Monitor': 'Monitor de Mano',
      'Detection Board': 'Panel Detección',
      'Effect: Particle': 'Efecto: Partículas',
      'Visual FX': 'Efectos Visuales',
      'Physics': 'Física',
      'Collision': 'Colisión',
      'Show Skeleton': 'Mostrar Esqueleto',
      'Debug': 'Depurar',
      'Info': 'Información',
      'LED': 'LED',
      'Motor': 'Motor',
      'RGB Stream': 'Flujo RGB',
      'Video': 'Video',
      'Depth Stream': 'Flujo Profundidad',
      'Depth': 'Profundidad',
      'Input Source': 'Fuente Entrada',
      'Sensor Config': 'Config Sensor',
      'Background': 'Fondo',
      'Visual Theme': 'Tema Visual',
      'System': 'Sistema',
      'Profile': 'Perfil',
      'Preferences': 'Preferencias',
      'Language & Devices': 'Idioma y Dispositivos',
      'Dark': 'Oscuro',
      'Light': 'Claro',
      'Speed': 'Velocidad',
      'Intensity': 'Intensidad',
      'Flow': 'Flujo',
      'Density': 'Densidad',
      'Shader WebGL — Reinicia si no se ve': 'Shader WebGL — Reinicia si no carga',
      'Camera': 'Cámara',
      'Microphone': 'Micrófono',
      'Discrete Mode': 'Modo Discreto',
      'System blocks recording': 'Bloquea grabación del sistema'
    };
    return dict[text] || text;
  };

  const p = currentPalette; // Alias corto para usar en el JSX

  // Poll status occasionally to sync UI with hardware
  useEffect(() => {
    if (data.kinectControl) {
      KinectService.getStatus().then(status => {
        if (status) {
          setKinectStatus(status);
          setMotorAngle(status.tilt);
          // Inverse map LED int to string if needed, or just keep syncing
          if (status.video_enabled !== undefined) setVideoActive(status.video_enabled);
          if (status.depth_enabled !== undefined) setDepthActive(status.depth_enabled);
        }
      });
    }
  }, []);

  useEffect(() => {
    let localStream: MediaStream | null = null;

    // --- WEBCAM MODE ---
    if (data.isWebcam && sensorType === 'WEBCAM') {
      navigator.mediaDevices.getUserMedia({ video: { aspectRatio: 1.777 } })
        .then(stream => {
          localStream = stream;
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play();
          }
        })
        .catch(err => console.error("Webcam error:", err));
    }

    // --- KINECT MODE ---
    else if (data.isWebcam && sensorType === 'KINECT') {
      if (videoRef.current) {
        videoRef.current.srcObject = null;
        videoRef.current.src = "";
      }
    }

    return () => {
      if (localStream) localStream.getTracks().forEach(track => track.stop());
    };
  }, [data.isWebcam, sensorType]);

  // Handler for Motor
  const handleMotorChange = (val: number) => {
    setMotorAngle(val);
    // Debounce could be added, but simple set for now
    KinectService.setTilt(val);
  };

  // Handler for LED
  const handleLedChange = (mode: string) => {
    setLedMode(mode);
    KinectService.setLed(mode);
  };

  // Determine Grid Spans
  let spanClass = '';
  switch (data.size) {
    case TileSize.Small: spanClass = 'col-span-1 row-span-1'; break;
    case TileSize.Medium: spanClass = 'col-span-1 row-span-2'; break;
    case TileSize.Wide: spanClass = 'col-span-2 row-span-1'; break;
    case TileSize.Large: spanClass = 'col-span-2 row-span-2'; break;
  }

  // Glassmorfismo: variaciones de color según el tema (tileBase) y preferencias globales de opacidad
  const tileBg = p.tileBase.replace(/[\d.]+\)$/g, `${preferences.boxOpacity})`);
  const dynamicBlur = Math.max(2, preferences.boxOpacity * 40 + 5);

  const tileGlassStyle: React.CSSProperties = data.isWebcam ? {} : {
    background: tileBg,
    backdropFilter: `blur(${dynamicBlur}px) saturate(160%)`,
    WebkitBackdropFilter: `blur(${dynamicBlur}px) saturate(160%)`,
    border: 'none',
    borderTop: `1px solid ${colorMode === 'dark' ? 'rgba(255,255,255,0.15)' : 'rgba(255,255,255,0.4)'}`,
    boxShadow: colorMode === 'dark' 
      ? `0 15px 35px -5px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(255,255,255,0.05), inset 0 8px 16px -8px rgba(255,255,255,0.1), inset 20px 0 30px -15px ${p.tileAccent}30`
      : `0 10px 25px -5px rgba(0,0,0,0.1), inset 0 0 0 1px rgba(255,255,255,0.8), inset 0 8px 16px -8px rgba(255,255,255,0.9), inset 20px 0 30px -15px ${p.tileAccent}20`,
    transition: 'all 0.6s cubic-bezier(0.165, 0.84, 0.44, 1)',
  };

  const baseStyles = `
    group relative rounded-2xl overflow-hidden
    hover:scale-[1.02] transition-all duration-300
    flex flex-col justify-between
  `;

  const finalBg = data.isWebcam ? 'bg-black' : '';
  const stopProp = (e: React.MouseEvent) => e.stopPropagation();

  const iconStyle: React.CSSProperties = {
    color: colorMode === 'light' ? p.primary : p.tileText,
    opacity: colorMode === 'light' ? 1 : 0.9,
    filter: colorMode === 'light' ? 'drop-shadow(0px 2px 4px rgba(0,0,0,0.2))' : 'drop-shadow(2px 3px 2px rgba(0,0,0,0.5))',
    transition: 'all 0.3s',
  };
  const iconNeumorphicStyle = "transition-all duration-300";

  const BackgroundEffects = () => (
    <>
      <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(135deg, ${p.tileAccent}12 0%, transparent 60%, ${p.ring} 100%)`, pointerEvents: 'none' }} />
      {data.icon && (
        <div style={{ position: 'absolute', bottom: -12, right: -12, opacity: 0.06, transform: 'rotate(-10deg) scale(3.5)', transformOrigin: 'bottom right', pointerEvents: 'none', color: p.tileText }}>{data.icon}</div>
      )}
    </>
  );

  // --- MOTOR COMPONENT (INTERNAL LAYOUT FOR MASKING) ---
  // El número siempre está absolutamente centrado en el tile.
  // El fill sube desde abajo sin mover el contenido.
  const MotorContent = ({ colorClass }: { colorClass: string }) => (
    <div className={`absolute inset-0 flex flex-col items-center justify-center ${colorClass}`}>
      <ChevronUp size={48} className={`transition-opacity duration-300 ${motorAngle > 5 ? 'opacity-100' : 'opacity-20'}`} strokeWidth={3} />
      <div className="text-6xl font-display font-bold tracking-tighter my-2">{motorAngle}°</div>
      <ChevronDown size={48} className={`transition-opacity duration-300 ${motorAngle < -5 ? 'opacity-100' : 'opacity-20'}`} strokeWidth={3} />
      <div className="absolute bottom-4 text-[10px] font-mono uppercase tracking-[0.2em] opacity-60">Motor Axis</div>
    </div>
  );

  // Helper to render specific Kinect Controls
  const renderKinectControl = () => {
    switch (data.kinectControl) {
      case 'motor':
        const fillPercentage = ((motorAngle + 30) / 60) * 100;
        return (
          <div className="w-full h-full relative" style={{ background: '#050505' }} onClick={stopProp}>
            {/* CAPA 1: Texto Blanco (Base) */}
            <div className="absolute inset-0 z-0 pointer-events-none">
              <MotorContent colorClass="text-white/90" />
            </div>

            {/* CAPA 2: Relleno Verde (Clipped) */}
            <div
              className="absolute inset-0 z-10 bg-white shadow-[0_0_40px_rgba(255,255,255,0.4)] transition-all duration-300 ease-out pointer-events-none"
              style={{ clipPath: `inset(${100 - fillPercentage}% 0 0 0)` }}
            />

            {/* CAPA 3: Texto Negro (Clipped) */}
            <div
              className="absolute inset-0 z-20 pointer-events-none transition-all duration-300 ease-out"
              style={{ clipPath: `inset(${100 - fillPercentage}% 0 0 0)` }}
            >
              <MotorContent colorClass="text-black" />
            </div>

            <input
              type="range"
              min="-30"
              max="30"
              value={motorAngle}
              onChange={(e) => handleMotorChange(parseInt(e.target.value))}
              className="absolute inset-0 w-full h-full opacity-0 cursor-ns-resize z-50 overflow-hidden"
              style={{ writingMode: 'vertical-rl', direction: 'rtl', WebkitAppearance: 'slider-vertical' } as any}
            />
          </div>
        );

      case 'sensor-config':
        return (
          <div className="flex flex-col h-full p-6 relative z-10 overflow-y-auto scrollbar-hide" onClick={stopProp}>
            <div className="flex justify-between items-start mb-4">
              <span className="font-display font-bold uppercase tracking-widest text-sm text-gray-400">Sensor Config</span>
              <div className={iconNeumorphicStyle}><Settings2 size={18} /></div>
            </div>

            <div className="flex-1 flex flex-col justify-center gap-3">
              <button
                onClick={() => updatePreferences({ sensorType: 'KINECT' })}
                className={`flex items-center gap-3 p-3 rounded-xl border transition-all duration-300
                     ${preferences.sensorType === 'KINECT' ? 'bg-primary border-primary text-black shadow-neon' : 'bg-black/40 border-white/10 text-gray-500 hover:border-white/30'}`}
              >
                <Monitor size={24} />
                <div className="text-left">
                  <div className="font-bold text-sm">Kinect 1414</div>
                  <div className="text-[10px] opacity-70">Hardware Sensor</div>
                </div>
              </button>

              <button
                onClick={() => updatePreferences({ sensorType: 'WEBCAM' })}
                className={`flex items-center gap-3 p-3 rounded-xl border transition-all duration-300
                     ${preferences.sensorType === 'WEBCAM' ? 'bg-primary border-primary text-black shadow-neon' : 'bg-black/40 border-white/10 text-gray-500 hover:border-white/30'}`}
              >
                <Camera size={24} />
                <div className="text-left">
                  <div className="font-bold text-sm">Webcam</div>
                  <div className="text-[10px] opacity-70">IntegratedUVC</div>
                </div>
              </button>
            </div>

            <div className="mt-2 text-center text-[10px] text-gray-500 font-mono">
              {preferences.sensorType === 'WEBCAM' ? 'Using standard UVC Driver' : 'Requires localhost:5001'}
            </div>
          </div>
        );

      case 'led':
        return (
          <div className="flex flex-col h-full p-4 relative z-10 w-full" onClick={stopProp}>
            <div className="font-display font-bold uppercase tracking-widest text-[10px] mb-3 text-gray-400">LED Config</div>
            <div className="flex flex-wrap gap-2 flex-1 justify-center content-center">
              {['OFF', 'GRN', 'RED', 'YEL', 'BLINK'].map((opt) => (
                <button
                  key={opt}
                  onClick={() => handleLedChange(opt)}
                  className={`max-h-12 py-2 px-3 rounded-lg text-[10px] font-bold flex items-center justify-center transition-all duration-200 border flex-grow
                    ${ledMode === opt
                      ? 'bg-white/20 border-white text-white shadow-[0_0_15px_rgba(255,255,255,0.3)] scale-[1.05]'
                      : 'bg-black/20 border-white/10 text-gray-500 hover:border-white/30 backdrop-blur-sm'}`}
                >
                  {opt}
                </button>
              ))}
            </div>
          </div>
        );

      case 'hand-monitor':
        // Simulated Magic Hand Monitor
        return (
          <div className="flex flex-col h-full w-full relative z-10 bg-black">
            <div className="absolute inset-0 z-0 opacity-20"
              style={{ backgroundImage: 'linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>

            <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-start z-20 bg-gradient-to-b from-black/90 to-transparent">
              <div>
                <div className="text-primary font-mono text-xs uppercase tracking-widest mb-1">Tracking Active</div>
                <div className="text-white/60 text-[10px] font-mono">X: 142 Y: 89 Z: 1.2m</div>
              </div>
              <div className="flex gap-1.5">
                <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                <div className="w-2 h-2 rounded-full bg-primary/20"></div>
              </div>
            </div>

            <div className="flex-1 relative flex items-center justify-center z-10">
              <div className="relative w-48 h-48 animate-pulse border border-white/5 rounded-full flex items-center justify-center">
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-16 h-16 border border-primary/40 rounded-full flex items-center justify-center">
                  <div className="w-3 h-3 bg-white rounded-full shadow-[0_0_15px_rgba(255,255,255,0.8)]"></div>
                </div>
                {[0, 45, 90, -45, -90].map((rot, i) => (
                  <div key={i} className="absolute top-1/2 left-1/2 w-24 h-px bg-primary/30 origin-left" style={{ transform: `rotate(${rot - 90}deg)` }}>
                    <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-2 h-2 bg-primary/60 rounded-full"></div>
                  </div>
                ))}
              </div>
              <div className="absolute top-12 right-12 w-1.5 h-1.5 bg-white/50 rounded-full animate-ping"></div>
            </div>

            <div className="absolute bottom-0 left-0 right-0 p-3 bg-black/80 backdrop-blur-sm border-t border-white/10 flex justify-between text-[10px] font-mono" style={{ color: p.tileSubtext }}>
              <span>FPS: 30</span>
              <span>CONF: 0.94</span>
            </div>
          </div>
        );

      case 'analytics':
        return (
          <div className="flex flex-col h-full justify-between p-5 relative z-10">
            <div className="flex justify-between items-start mb-2">
              <span className="font-mono text-[10px] uppercase tracking-widest" style={{ color: p.tileSubtext }}>{data.statLabel || 'Stat'}</span>
              <div className={iconNeumorphicStyle}>{data.icon}</div>
            </div>
            <div className="flex flex-col mt-auto">
              <span className="text-5xl font-display font-bold tracking-tighter drop-shadow-lg" style={{ color: p.tileText }}>{data.statValue}</span>
              {data.subtitle && <span className="text-xs mt-2 uppercase tracking-wide" style={{ color: p.tileSubtext }}>{data.subtitle}</span>}
            </div>
            <div className="w-full h-1 bg-white/10 rounded-full mt-4 overflow-hidden">
              <div className="h-full bg-white w-2/3 shadow-[0_0_10px_rgba(255,255,255,0.5)]"></div>
            </div>
          </div>
        );

      case 'gesture-tune':
        return (
          <div className="flex flex-col h-full p-5 relative z-10" onClick={stopProp}>
            <div className="flex justify-between items-center mb-6">
              <span className="font-display font-bold uppercase tracking-widest text-sm" style={{ color: p.tileText }}>Sensitivity</span>
              <span className="text-primary font-mono text-sm font-bold">{gestureSensitivity}%</span>
            </div>

            <div className="flex-1 flex items-center justify-center">
              <input
                type="range"
                min="0"
                max="100"
                value={gestureSensitivity}
                onChange={(e) => setGestureSensitivity(parseInt(e.target.value))}
                className="w-full h-3 bg-white/10 rounded-full appearance-none cursor-pointer
                    [&::-webkit-slider-thumb]:appearance-none
                    [&::-webkit-slider-thumb]:w-6
                    [&::-webkit-slider-thumb]:h-6
                    [&::-webkit-slider-thumb]:bg-white
                    [&::-webkit-slider-thumb]:rounded-full
                    [&::-webkit-slider-thumb]:shadow-[0_0_15px_rgba(255,255,255,0.8)]
                    [&::-webkit-slider-thumb]:border-2
                    [&::-webkit-slider-thumb]:border-black"
              />
            </div>
            <div className="flex justify-between text-[10px] text-gray-500 font-mono mt-4">
              <span>Low Latency</span>
              <span>High Precision</span>
            </div>
          </div>
        );

      case 'gesture-action':
        return (
          <div className="flex flex-col items-center justify-center h-full p-4 gap-3 z-10 relative">
            <div className={iconNeumorphicStyle}>
              {data.icon}
            </div>
            <span className="text-sm font-bold uppercase tracking-wide text-white">{data.title}</span>
            <div className="px-3 py-1 rounded bg-white/10 text-[9px] font-mono text-primary border border-white/5 uppercase tracking-wider">
              {data.subtitle || 'ACTION'}
            </div>
          </div>
        );

      case 'info':
        return (
          <div className="flex flex-col h-full p-4 text-white justify-center items-center gap-2 relative z-10" onClick={stopProp}>
            <div className={iconNeumorphicStyle}><Info size={36} /></div>
            <span className="font-mono text-[10px] text-gray-600 uppercase group-hover:text-gray-300">v1.0.4</span>
          </div>
        );

      case 'video-settings':
        return (
          <div className="flex flex-col h-full p-4 relative z-10 w-full" onClick={stopProp}>
            <div className="flex justify-between items-start mb-4">
              <span className="font-display font-bold uppercase tracking-widest text-[10px]" style={{ color: p.tileSubtext }}>Video Config</span>
              <div className={iconNeumorphicStyle}><Settings2 size={16} /></div>
            </div>
            
            <div className="flex-1 flex flex-col justify-center">
              <button
                onClick={() => {
                  const newState = !videoActive;
                  setVideoActive(newState);
                  KinectService.setVideoEnabled(newState);
                }}
                className={`w-full py-2.5 rounded-xl border flex items-center justify-center gap-2 transition-all duration-300
                  ${videoActive 
                    ? 'border-transparent text-black' 
                    : 'bg-black/40 border-white/10 text-gray-500 hover:border-white/30'}`}
                style={videoActive ? { background: p.tileAccent, boxShadow: `0 0 15px ${p.tileAccent}50` } : {}}
              >
                <Video size={16} className={videoActive ? "text-black" : "text-gray-500"} />
                <span className="text-[11px] font-bold uppercase tracking-wider">
                  {videoActive ? 'RGB Sensor ON' : 'RGB Sensor OFF'}
                </span>
              </button>
            </div>
            
            <div className="mt-auto flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${videoActive ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]'}`}></div>
              <span className="text-[10px] font-mono uppercase" style={{ color: p.tileSubtext }}>Res: 640x480</span>
            </div>
          </div>
        );

      case 'depth-settings':
        const colormaps = [
          { id: 2, label: 'JET' },
          { id: 16, label: 'VIRIDIS' },
          { id: 14, label: 'INFERNO' },
          { id: 9, label: 'BONE' },
          { id: 5, label: 'OCEAN' },
          { id: 10, label: 'SPRING' }
        ];
        return (
          <div className="flex flex-col h-full p-4 relative z-10 w-full" onClick={stopProp}>
            <div className="flex justify-between items-start mb-2">
              <span className="font-display font-bold uppercase tracking-widest text-[10px]" style={{ color: p.tileSubtext }}>Depth Config</span>
              <button
                onClick={() => {
                  const newState = !depthActive;
                  setDepthActive(newState);
                  KinectService.setDepthEnabled(newState);
                }}
                className={`px-3 py-1 rounded text-[9px] font-bold uppercase transition-all border
                  ${depthActive 
                    ? 'text-black border-transparent' 
                    : 'bg-black/40 border-white/10 hover:border-white/30'}`}
                style={depthActive ? { background: p.tileAccent } : { color: p.tileSubtext }}
              >
                {depthActive ? 'SENS ON' : 'SENS OFF'}
              </button>
            </div>
            
            <div className="flex-1 flex flex-col justify-center">
              <span className="text-[9px] font-mono uppercase mb-1.5 ml-1 drop-shadow-md" style={{ color: p.tileSubtext }}>ColorMaps (OpenCV)</span>
              <div className="grid grid-cols-3 gap-1 mb-1">
                {colormaps.map(cmap => (
                  <button
                    key={cmap.id}
                    onClick={() => {
                      setDepthColormap(cmap.id);
                      KinectService.setDepthColormap(cmap.id);
                    }}
                    className={`py-1 rounded-md text-[8px] font-bold uppercase transition-all duration-200 border
                      ${depthColormap === cmap.id
                        ? `bg-white/20 border-white text-white shadow-[0_0_10px_rgba(255,255,255,0.2)]`
                        : 'bg-black/20 border-white/5 hover:bg-black/40'}`}
                    style={depthColormap === cmap.id ? {} : { color: p.tileSubtext }}
                  >
                    {cmap.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-auto flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${depthActive ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]'}`}></div>
              <span className="text-[10px] font-mono uppercase" style={{ color: p.tileSubtext }}>IR Sensor 11-Bit</span>
            </div>
          </div>
        );

      case 'background-settings':
        const bgOptions: { id: any; label: string }[] = [
          { id: 'aurora',   label: 'Aurora'   },
          { id: 'pulse',    label: 'Pulse'    },
          { id: 'metro',    label: 'Metro'    },
          { id: 'spheres',  label: 'Lines'    },
          { id: 'fluid',    label: 'Fluid'    },
          { id: 'glimmer',  label: 'Glimmer'  },
        ];
        return (
          <div className="flex flex-col h-full p-4 relative z-10 w-full" onClick={stopProp}>
            <div className="flex items-center justify-between mb-3">
              <span style={{ color: p.tileText }} className="font-display font-bold uppercase tracking-widest text-sm">{t('Background')}</span>
            </div>

            {/* 6 fondos en cuadrícula 3x2 */}
            <div className="grid grid-cols-3 gap-1.5 mb-3">
              {bgOptions.map(opt => (
                <button
                  key={opt.id}
                  onClick={() => setBgMode(opt.id)}
                  className="flex items-center justify-center py-2 px-1 rounded-lg text-center transition-all duration-200"
                  style={bgMode === opt.id
                    ? { background: p.tileAccent, color: '#000', fontWeight: 700, border: `1px solid ${p.tileAccent}` }
                    : { background: 'rgba(0,0,0,0.35)', color: p.tileSubtext, border: `1px solid ${p.tileAccent}22` }}
                >
                  <span className="text-[9px] uppercase font-bold">{opt.label}</span>
                </button>
              ))}
            </div>

            {/* Controles Fluid */}
            {bgMode === 'fluid' && (
              <div className="flex flex-col gap-2 overflow-y-auto flex-1 pr-1 scrollbar-hide">
                <span style={{ color: p.tileSubtext }} className="text-[9px] font-mono uppercase mb-1">▸ {t('Temas Orgánicos')}</span>
                <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide mask-fade-right">
                  {Object.keys(FLUID_PRESETS).map(name => (
                    <button
                      key={name}
                      onClick={() => updateFluidConfig({ ...FLUID_PRESETS[name], preset: name })}
                      className={`whitespace-nowrap px-3 py-1 rounded-full text-[9px] font-bold uppercase transition-all
                        ${fluidConfig.preset === name 
                          ? 'bg-white text-black scale-105 shadow-lg' 
                          : 'bg-black/40 text-gray-400 border border-white/10 hover:border-white/30'}`}
                    >
                      {name}
                    </button>
                  ))}
                </div>

                <span style={{ color: p.tileSubtext }} className="text-[9px] font-mono uppercase mt-1">▸ {t('Ajuste de Física')}</span>
                {[
                  { label: t('Velocidad'), key: 'speed', min: 0, max: 0.4, step: 0.01 },
                  { label: t('Ángulo'), key: 'angle', min: -3.14, max: 3.14, step: 0.1 },
                  { label: t('Warp'), key: 'warp', min: 0, max: 4, step: 0.1 },
                  { label: t('Ondas'), key: 'freq', min: 0, max: 5, step: 0.1 },
                  { label: t('Ruido'), key: 'noise', min: 0, max: 3, step: 0.1 },
                  { label: t('Conexión'), key: 'flow', min: 0, max: 1.5, step: 0.05 },
                  { label: t('Suavidad'), key: 'depth', min: 0, max: 2.5, step: 0.01 },
                  { label: t('Sombra'), key: 'shadow', min: 0.01, max: 0.4, step: 0.01 },
                ].map(s => (
                  <div key={s.key} className="flex flex-col gap-1">
                    <div className="flex justify-between text-[8px] uppercase font-mono" style={{ color: p.tileSubtext }}>
                      <span>{s.label}</span>
                      <span style={{ color: p.tileAccent }}>{Number((fluidConfig as any)[s.key]).toFixed(2)}</span>
                    </div>
                    <input type="range" min={s.min} max={s.max} step={s.step}
                      value={(fluidConfig as any)[s.key]}
                      onChange={e => updateFluidConfig({ [s.key]: parseFloat(e.target.value) })}
                      className="w-full h-1 rounded-full appearance-none cursor-pointer"
                      style={{ background: `${p.tileAccent}33` }} />
                  </div>
                ))}
              </div>
            )}

            {/* Controles Glimmer */}
            {bgMode === 'glimmer' && (
              <div className="flex flex-col gap-2 overflow-y-auto flex-1 pr-1 scrollbar-hide">
                {[
                  { label: t('Speed'), key: 'speed', min: 0.02, max: 0.2, step: 0.005 },
                  { label: t('Intensity'), key: 'intensity', min: 0.2, max: 1.0, step: 0.05 },
                ].map(s => (
                  <div key={s.key} className="flex flex-col gap-1">
                    <div className="flex justify-between text-[9px] uppercase font-mono" style={{ color: p.tileSubtext }}>
                      <span>{s.label}</span>
                      <span style={{ color: p.tileAccent }}>{(glimmerConfig as any)[s.key].toFixed(3)}</span>
                    </div>
                    <input type="range" min={s.min} max={s.max} step={s.step}
                      value={(glimmerConfig as any)[s.key]}
                      onChange={e => updateGlimmerConfig({ [s.key]: parseFloat(e.target.value) })}
                      className="w-full h-1 rounded-full appearance-none cursor-pointer"
                      style={{ background: `${p.tileAccent}33` }} />
                  </div>
                ))}
              </div>
            )}

            {/* Info para modos sin controles */}
            {['aurora','pulse','metro','spheres'].includes(bgMode) && (
              <div className="flex-1 flex items-center justify-center">
                <span className="text-[9px] font-mono uppercase text-center px-2" style={{ color: p.tileSubtext }}>
                  {bgMode === 'aurora'   && 'Aurora boreal Xbox — Suave'}
                  {bgMode === 'pulse'    && 'Xbox Ring — Ondas pulsantes'}
                  {bgMode === 'metro'    && 'Metro UI — Tiles animados'}
                  {bgMode === 'spheres'  && 'Flowing Lines — Estética fibra óptica'}
                </span>
              </div>
            )}
          </div>
        );

      case 'preferences':
        return (
          <div className="flex flex-col h-full p-4 relative z-10 w-full overflow-y-auto scrollbar-hide" onClick={stopProp}>
            <span className="font-display font-bold uppercase tracking-widest text-sm mb-4" style={{ color: p.tileText }}>
              {preferences.language === 'es' ? 'Preferencias' : 'Preferences'}
            </span>

            {/* Idioma — sin banderas, solo el nombre */}
            <div className="mb-3">
              <div className="flex items-center gap-2 mb-2">
                <Globe size={11} style={{ color: p.tileAccent }} />
                <span className="text-[9px] uppercase font-mono font-bold tracking-widest" style={{ color: p.tileSubtext }}>
                  {preferences.language === 'es' ? 'Idioma' : 'Language'}
                </span>
              </div>
              <div className="flex gap-2">
                {[{ code: 'es', label: 'Español' }, { code: 'en', label: 'English' }].map(l => (
                  <button key={l.code}
                    onClick={() => updatePreferences({ language: l.code as any })}
                    className="flex-1 py-1.5 rounded-lg border text-[10px] font-bold uppercase transition-all"
                    style={preferences.language === l.code
                      ? { background: p.tileAccent, color: '#000', borderColor: p.tileAccent }
                      : { background: 'rgba(0,0,0,0.4)', color: p.tileSubtext, borderColor: `${p.tileAccent}22` }}
                  >{l.label}</button>
                ))}
              </div>
            </div>

            {/* Cámara */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Video size={12} style={{ color: p.tileAccent }} />
                  <span className="text-[10px] uppercase font-bold tracking-widest" style={{ color: p.tileSubtext }}>
                    {preferences.language === 'es' ? 'Cámara' : 'Camera'}
                  </span>
                </div>
                <button 
                  onClick={() => navigator.mediaDevices.enumerateDevices().then(d => setCameras(d.filter(x => x.kind === 'videoinput')))}
                  className="text-[8px] uppercase font-mono opacity-60 hover:opacity-100 transition-opacity"
                  style={{ color: p.tileAccent }}
                >
                  {preferences.language === 'es' ? '[ Refrescar ]' : '[ Refresh ]'}
                </button>
              </div>
              <div className="flex flex-col gap-1 max-h-[100px] overflow-y-auto scrollbar-hide py-1">
                {cameras.length === 0 && (
                  <div className="py-2 text-center text-[9px] opacity-40 uppercase font-mono italic">No devices found</div>
                )}
                {cameras.map(c => (
                  <button
                    key={c.deviceId}
                    onClick={() => updatePreferences({ cameraId: c.deviceId })}
                    className={`text-left px-3 py-2 rounded-lg text-[9px] font-bold uppercase transition-all
                      ${preferences.cameraId === c.deviceId 
                        ? 'text-black' 
                        : 'bg-white/5 hover:bg-white/10'}`}
                    style={preferences.cameraId === c.deviceId ? { background: p.tileAccent } : { color: p.tileSubtext }}
                  >
                    {c.label || `Camera ${c.deviceId.slice(0,5)}...`}
                  </button>
                ))}
              </div>
            </div>

            {/* Micrófono */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Mic size={12} style={{ color: p.tileAccent }} />
                  <span className="text-[10px] uppercase font-bold tracking-widest" style={{ color: p.tileSubtext }}>
                    {preferences.language === 'es' ? 'Micrófono' : 'Microphone'}
                  </span>
                </div>
                <button 
                  onClick={() => navigator.mediaDevices.enumerateDevices().then(d => setMics(d.filter(x => x.kind === 'audioinput')))}
                  className="text-[8px] uppercase font-mono opacity-60 hover:opacity-100 transition-opacity"
                  style={{ color: p.tileAccent }}
                >
                  {preferences.language === 'es' ? '[ Refrescar ]' : '[ Refresh ]'}
                </button>
              </div>
              <div className="flex flex-col gap-1 max-h-[100px] overflow-y-auto scrollbar-hide py-1">
                {mics.length === 0 && (
                  <div className="py-2 text-center text-[9px] opacity-40 uppercase font-mono italic">No audio devices found</div>
                )}
                {mics.map(m => (
                  <button
                    key={m.deviceId}
                    onClick={() => updatePreferences({ microphoneId: m.deviceId })}
                    className={`text-left px-3 py-2 rounded-lg text-[9px] font-bold uppercase transition-all
                      ${preferences.microphoneId === m.deviceId 
                        ? 'text-black' 
                        : 'bg-white/5 hover:bg-white/10'}`}
                    style={preferences.microphoneId === m.deviceId ? { background: p.tileAccent } : { color: p.tileSubtext }}
                  >
                    {m.label || `Mic ${m.deviceId.slice(0,5)}...`}
                  </button>
                ))}
              </div>
            </div>

            {/* Modo Discreto — Switch visual */}
            <div className="mt-auto pt-2">
              <button
                onClick={() => updatePreferences({ discreteMode: !preferences.discreteMode })}
                className="w-full group flex items-center justify-between px-4 py-3 rounded-2xl transition-all duration-500 overflow-hidden relative"
                style={{ 
                  background: preferences.discreteMode ? p.tileAccent : 'rgba(0,0,0,0.4)',
                  boxShadow: preferences.discreteMode ? `0 8px 32px 0 rgba(0, 0, 0, 0.4), inset 0 0 0 1px ${p.tileAccent}20` : 'none',
                  backdropFilter: preferences.discreteMode ? 'blur(20px)' : 'none',
                  WebkitBackdropFilter: preferences.discreteMode ? 'blur(20px)' : 'none',
                  transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)'
                }}
              >
                <div className="flex flex-col items-start relative z-10">
                  <span className={`text-[10px] font-bold uppercase tracking-widest`} style={{ color: preferences.discreteMode ? '#000' : p.tileText }}>
                    {preferences.language === 'es' ? 'Modo Discreto' : 'Discrete Mode'}
                  </span>
                  <span className={`text-[7px] font-mono uppercase`} style={{ color: preferences.discreteMode ? 'rgba(0,0,0,0.6)' : p.tileSubtext }}>
                    {preferences.language === 'es' 
                      ? (preferences.discreteMode ? 'Privacidad Activa' : 'Grabación Estándar')
                      : (preferences.discreteMode ? 'Privacy Active' : 'Standard Recording')}
                  </span>
                </div>
                <div className={`w-8 h-4 rounded-full relative transition-all duration-300 border ${preferences.discreteMode ? 'bg-black/20 border-black/10' : 'bg-white/10 border-white/5'}`}>
                  <div className={`absolute top-0.5 w-3 h-3 rounded-full transition-all duration-300 ${preferences.discreteMode ? 'right-0.5 bg-black' : 'left-0.5'}`} style={preferences.discreteMode ? {} : { background: p.tileSubtext }} />
                </div>
              </button>
            </div>
          </div>
        );

      case 'tile-settings':
        return (
          <div className="flex flex-col h-full p-6 relative z-10" onClick={stopProp}>
            <div className="flex justify-between items-start mb-4">
              <span className="font-display font-bold uppercase tracking-widest text-sm" style={{ color: p.tileText }}>
                {preferences.language === 'es' ? 'Apariencia de Cajas' : 'Tile UI Style'}
              </span>
              <div className={iconNeumorphicStyle}><Settings2 size={18} /></div>
            </div>
            <div className="flex-1 flex flex-col justify-center">
              <label className="text-[10px] font-mono mb-2 uppercase tracking-wider" style={{ color: p.tileSubtext }}>
                 {preferences.language === 'es' ? 'Opacidad Global del Cristal' : 'Global Glass Opacity'}: {Math.round(preferences.boxOpacity * 100)}%
              </label>
              <input 
                type="range" min="0" max="1" step="0.05" 
                value={preferences.boxOpacity}
                onChange={e => updatePreferences({ boxOpacity: parseFloat(e.target.value) })}
                className="w-full h-1.5 rounded-full appearance-none outline-none cursor-pointer transition-all"
                style={{ background: `${p.tileAccent}40`, accentColor: p.primary, opacity: 0.9 }}
              />
              <div className="mt-4 text-[9px] font-mono leading-relaxed" style={{ color: p.tileSubtext }}>
                {preferences.language === 'es' 
                  ? 'Ajusta el nivel de transparencia y desenfoque (blur) de los paneles de la interfaz principal.' 
                  : 'Adjusts global panel transparency and internal blur intensity across the user interface.'}
              </div>
            </div>
          </div>
        );

      default: return null;
    }
  };

  // Main Render Logic
  const renderContent = () => {
    const title = t(data.title);
    const subtitle = data.subtitle ? t(data.subtitle) : '';

    // 1. Kinect Controls
    if (data.kinectControl) {
      return (
        <>
          <BackgroundEffects />
          {renderKinectControl()}
        </>
      );
    }

    // 2. Webcam Feed (16:9 Aspect Ratio)
    if (data.isWebcam) {
      return (
        <div className="absolute inset-0 bg-black flex items-center justify-center overflow-hidden">
          <div className="absolute bottom-[-10%] right-[-10%] z-0 opacity-[0.1]">
            {data.icon && React.cloneElement(data.icon as React.ReactElement, { size: 200, strokeWidth: 1 })}
          </div>
          <div className="w-full h-full flex items-center justify-center bg-black">
            {sensorType === 'WEBCAM' ? (
              <video
                ref={videoRef}
                className="w-full h-full object-contain opacity-80 grayscale-[20%] contrast-125 relative z-10"
                muted
                playsInline
                style={{ transform: 'scaleX(-1)' }}
              />
            ) : (
              <img
                key={`${sensorType}-${data.title}`}
                src={data.title.includes('Depth') ? KinectService.getDepthStreamUrl() : KinectService.getVideoStreamUrl()}
                className="w-full h-full object-contain opacity-80 grayscale-[20%] contrast-125 relative z-10"
                alt="Kinect Stream"
                style={{ transform: 'scaleX(-1)' }}
              />
            )}
          </div>
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 mix-blend-overlay z-20 pointer-events-none"></div>
          <div className="absolute top-3 left-3 flex items-center gap-2 bg-black/60 px-2 py-1 rounded border border-white/10 backdrop-blur-md z-30">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></div>
            <span className="text-gray-200 text-[9px] font-bold tracking-wider uppercase font-mono">REC</span>
          </div>
          <div className="absolute bottom-4 left-4 text-white font-display font-bold text-2xl drop-shadow-lg tracking-wide z-30">{title}</div>
        </div>
      );
    }

    // 3. Image Tile / Standard
    if (data.image) {
      return (
        <>
          <BackgroundEffects />
          <img src={data.image} alt={title} className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105 opacity-80 group-hover:opacity-40 z-0" />
          <div className="absolute inset-0 bg-gradient-to-t from-background-dark via-background-dark/50 to-transparent opacity-90 z-10" />
          <div className="absolute inset-x-0 bottom-0 p-5 z-20">
            <div className="text-white font-display font-bold text-2xl leading-none mb-3">{title}</div>
            {subtitle && <div className="text-primary text-[10px] font-mono uppercase tracking-widest">{subtitle}</div>}
          </div>
        </>
      );
    }

    // 4. Standard Icon Tile
    return (
      <>
        <BackgroundEffects />
        <div className="flex flex-col justify-between h-full p-5 relative z-10">
          <div className="flex justify-between items-start">
            <div className={iconNeumorphicStyle}>
              {data.icon}
            </div>
            <div className="w-1 h-1 bg-white/20 rounded-full group-hover:bg-primary group-hover:shadow-[0_0_5px_rgba(255,255,255,0.8)] transition-all"></div>
          </div>
          <div>
            <div className="font-display font-bold text-2xl leading-none mb-3 tracking-wide transition-colors drop-shadow-sm" style={{ color: p.tileText }}>{title}</div>
            {subtitle && <div className="text-[10px] font-mono font-medium uppercase tracking-wider transition-colors" style={{ color: p.tileSubtext }}>{subtitle}</div>}
          </div>
          <div className="absolute bottom-0 left-0 h-[2px] bg-primary w-0 group-hover:w-full transition-all duration-500 ease-out"></div>
        </div>
      </>
    );

  };

  return (
    <motion.button
      whileHover={{ scale: 1.02, zIndex: 10 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onClick(data)}
      className={`${spanClass} ${baseStyles} ${finalBg} cursor-pointer select-none text-left`}
      style={tileGlassStyle}
    >
      {renderContent()}
    </motion.button>
  );
};

export default Tile;