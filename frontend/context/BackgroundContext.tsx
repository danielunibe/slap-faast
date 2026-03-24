import React, { createContext, useContext, useState } from 'react';

export type BackgroundMode = 'aurora' | 'pulse' | 'metro' | 'spheres' | 'fluid' | 'glimmer';
export type ColorMode = 'dark' | 'light';
export type Language = 'es' | 'en';

// ── Paleta de colores por tema (dark y light) ──
export interface ThemePalette {
  tileBase: string;        // rgba para glassmorfismo
  tileAccent: string;      // glow / borde hover
  tileText: string;        // color texto principal
  tileSubtext: string;     // subtítulo
  hubBg: string;           // fondo del header
  primary: string;         // color primario interactivo
  ring: string;            // anillo / glow del tile activo
}

export const THEME_PALETTES: Record<BackgroundMode, Record<ColorMode, ThemePalette>> = {
  aurora: {
    dark:  { tileBase: 'rgba(20,20,20,0.45)', tileAccent: '#ffffff', tileText: '#ffffff', tileSubtext: '#999999', hubBg: 'rgba(0,0,0,0.35)', primary: '#ffffff', ring: 'rgba(255,255,255,0.15)' },
    light: { tileBase: 'rgba(255,255,255,0.85)', tileAccent: '#000000', tileText: '#000000', tileSubtext: '#444444', hubBg: 'rgba(255,255,255,0.8)', primary: '#000000', ring: 'rgba(0,0,0,0.2)' },
  },
  pulse: {
    dark:  { tileBase: 'rgba(15,15,15,0.45)', tileAccent: '#cccccc', tileText: '#f5f5f5', tileSubtext: '#888888', hubBg: 'rgba(0,0,0,0.35)', primary: '#cccccc', ring: 'rgba(200,200,200,0.1)' },
    light: { tileBase: 'rgba(245,245,245,0.85)', tileAccent: '#000000', tileText: '#000000', tileSubtext: '#444444', hubBg: 'rgba(255,255,255,0.8)', primary: '#000000', ring: 'rgba(0,0,0,0.2)' },
  },
  metro: {
    dark:  { tileBase: 'rgba(25,25,25,0.45)', tileAccent: '#eeeeee', tileText: '#ffffff', tileSubtext: '#aaaaaa', hubBg: 'rgba(0,0,0,0.35)', primary: '#eeeeee', ring: 'rgba(255,255,255,0.2)' },
    light: { tileBase: 'rgba(240,240,240,0.85)', tileAccent: '#000000', tileText: '#000000', tileSubtext: '#444444', hubBg: 'rgba(255,255,255,0.8)', primary: '#000000', ring: 'rgba(0,0,0,0.2)' },
  },
  spheres: {
    dark:  { tileBase: 'rgba(10,10,10,0.45)', tileAccent: '#999999', tileText: '#dddddd', tileSubtext: '#777777', hubBg: 'rgba(0,0,0,0.35)', primary: '#999999', ring: 'rgba(150,150,150,0.1)' },
    light: { tileBase: 'rgba(10,10,10,0.45)', tileAccent: '#999999', tileText: '#dddddd', tileSubtext: '#777777', hubBg: 'rgba(0,0,0,0.35)', primary: '#999999', ring: 'rgba(150,150,150,0.1)' },
  },
  fluid: {
    dark:  { tileBase: 'rgba(20,20,20,0.55)', tileAccent: '#ffffff', tileText: '#ffffff', tileSubtext: '#bbbbbb', hubBg: 'rgba(0,0,0,0.45)', primary: '#ffffff', ring: 'rgba(255,255,255,0.15)' },
    light: { tileBase: 'rgba(255,255,255,0.92)', tileAccent: '#000000', tileText: '#000000', tileSubtext: '#333333', hubBg: 'rgba(255,255,255,0.9)', primary: '#000000', ring: 'rgba(0,0,0,0.25)' },
  },
  glimmer: {
    dark:  { tileBase: 'rgba(5,5,5,0.45)', tileAccent: '#dddddd', tileText: '#ffffff', tileSubtext: '#999999', hubBg: 'rgba(0,0,0,0.35)', primary: '#ffffff', ring: 'rgba(255,255,255,0.1)' },
    light: { tileBase: 'rgba(255,255,255,0.9)', tileAccent: '#000000', tileText: '#000000', tileSubtext: '#333333', hubBg: 'rgba(255,255,255,0.8)', primary: '#000000', ring: 'rgba(0,0,0,0.2)' },
  },
};

export interface FluidConfig {
  preset: string;
  color1: string; color2: string; color3: string; color4: string;
  depth: number; lightX: number; lightY: number; speed: number;
  angle: number; freq: number; warp: number; noise: number; flow: number; shadow: number;
}

export const FLUID_PRESETS: Record<string, Partial<FluidConfig>> = {
  'Blue/Cyan': { color1: '#000000', color2: '#0048ff', color3: '#0088ff', color4: '#ffffff', depth: 0.12, speed: 0.12, angle: 0.0, freq: 1.4, warp: 1.2, noise: 0.8, flow: 0.6, shadow: 0.05 },
  'Purple Flow': { color1: '#0f002b', color2: '#4a00e0', color3: '#d9005a', color4: '#ff80bf', depth: 0.08, speed: 0.15, angle: 1.5, freq: 2.2, warp: 3.5, noise: 1.5, flow: 1.1, shadow: 0.02 },
  'Dark Ocean': { color1: '#000000', color2: '#0b132b', color3: '#1c2541', color4: '#5bc0be', depth: 0.25, speed: 0.08, angle: 0.5, freq: 0.9, warp: 0.5, noise: 0.4, flow: 0.3, shadow: 0.15 },
  'Sunset Glow': { color1: '#26001b', color2: '#bd0034', color3: '#ff5e00', color4: '#ffcc00', depth: 0.05, speed: 0.22, angle: -0.8, freq: 3.5, warp: 2.1, noise: 2.0, flow: 1.4, shadow: 0.01 },
  'Toxic Mint': { color1: '#001a09', color2: '#006633', color3: '#00cc66', color4: '#ccffdd', depth: 0.03, speed: 0.18, angle: 2.1, freq: 4.2, warp: 4.0, noise: 1.2, flow: 1.5, shadow: 0.01 },
  'Cyberpunk': { color1: '#12003b', color2: '#b100e8', color3: '#ff007c', color4: '#00ffff', depth: 0.06, speed: 0.25, angle: 0.1, freq: 1.8, warp: 6.0, noise: 2.5, flow: 1.0, shadow: 0.01 },
  'Liquid Gold': { color1: '#1f1300', color2: '#8c5900', color3: '#d9a300', color4: '#fff1b8', depth: 0.18, speed: 0.05, angle: 0.3, freq: 0.6, warp: 0.8, noise: 0.5, flow: 0.4, shadow: 0.25 },
  'Cherry Blossom': { color1: '#2e0014', color2: '#b80052', color3: '#ff66a3', color4: '#ffe6f0', depth: 0.04, speed: 0.14, angle: 0.8, freq: 2.5, warp: 1.5, noise: 1.1, flow: 0.9, shadow: 0.03 },
  'Volcanic Magma': { color1: '#1a0000', color2: '#8a0a00', color3: '#ff4d00', color4: '#ffea00', depth: 0.02, speed: 0.35, angle: -1.2, freq: 6.0, warp: 8.0, noise: 4.0, flow: 2.5, shadow: 0.01 },
  'Aurora Borealis': { color1: '#000a14', color2: '#00594d', color3: '#00ff88', color4: '#aaffff', depth: 0.10, speed: 0.09, angle: 0.4, freq: 1.1, warp: 2.5, noise: 0.9, flow: 0.7, shadow: 0.05 },
  'Amethyst Dream': { color1: '#10001a', color2: '#4e008e', color3: '#9933ff', color4: '#e6ccff', depth: 0.07, speed: 0.12, angle: 1.2, freq: 1.9, warp: 2.0, noise: 1.4, flow: 1.2, shadow: 0.02 },
  'Abyssal Pearl': { color1: '#000f1a', color2: '#004d66', color3: '#00b3b3', color4: '#ffe6f2', depth: 0.15, speed: 0.07, angle: -0.5, freq: 1.5, warp: 1.2, noise: 0.6, flow: 0.8, shadow: 0.10 },
  'Autumn Ember': { color1: '#260d00', color2: '#8c3a00', color3: '#d96600', color4: '#ffb366', depth: 0.12, speed: 0.10, angle: 0.9, freq: 2.1, warp: 1.8, noise: 1.3, flow: 1.0, shadow: 0.04 },
};

export interface GlimmerConfig { speed: number; intensity: number; }

export interface AppPreferences {
  language: Language;
  cameraId: string;
  microphoneId: string;
  discreteMode: boolean; // reemplaza voiceRecording — modo discreto = no graba
  sensorType: 'KINECT' | 'WEBCAM';
  boxOpacity: number;
}

export const DEFAULT_FLUID_CONFIG: FluidConfig = {
  preset: 'Blue/Cyan',
  color1: '#000000', color2: '#0048ff', color3: '#0088ff', color4: '#ffffff',
  depth: 0.04, lightX: 0.96, lightY: -0.36, speed: 0.11,
  angle: 1.08, freq: 1.86, warp: 4.0, noise: 0.71, flow: 0.87, shadow: 0.01
};

export const DEFAULT_GLIMMER_CONFIG: GlimmerConfig = { speed: 0.065, intensity: 0.7 };
export const DEFAULT_PREFERENCES: AppPreferences = { language: 'es', cameraId: '', microphoneId: '', discreteMode: false, sensorType: 'KINECT', boxOpacity: 0.45 };

interface AppContextType {
  bgMode: BackgroundMode;
  setBgMode: (mode: BackgroundMode) => void;
  colorMode: ColorMode;
  setColorMode: (mode: ColorMode) => void;
  currentPalette: ThemePalette;
  fluidConfig: FluidConfig;
  updateFluidConfig: (updates: Partial<FluidConfig>) => void;
  glimmerConfig: GlimmerConfig;
  updateGlimmerConfig: (updates: Partial<GlimmerConfig>) => void;
  preferences: AppPreferences;
  updatePreferences: (updates: Partial<AppPreferences>) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const BackgroundProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [bgMode, setBgMode] = useState<BackgroundMode>('spheres');
  const [colorMode, setColorMode] = useState<ColorMode>('dark');
  const [fluidConfig, setFluidConfig] = useState<FluidConfig>(DEFAULT_FLUID_CONFIG);
  const [glimmerConfig, setGlimmerConfig] = useState<GlimmerConfig>(DEFAULT_GLIMMER_CONFIG);
  const [preferences, setPreferences] = useState<AppPreferences>(DEFAULT_PREFERENCES);

  const currentPalette = THEME_PALETTES[bgMode][colorMode];

  return (
    <AppContext.Provider value={{
      bgMode, setBgMode, colorMode, setColorMode, currentPalette,
      fluidConfig, updateFluidConfig: u => setFluidConfig(p => ({ ...p, ...u })),
      glimmerConfig, updateGlimmerConfig: u => setGlimmerConfig(p => ({ ...p, ...u })),
      preferences, updatePreferences: u => setPreferences(p => ({ ...p, ...u })),
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useBackground = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useBackground must be used within BackgroundProvider');
  return ctx;
};
