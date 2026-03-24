import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import TopMenu from './components/TopMenu';
import HubView from './components/HubView';
import { HUBS } from './constants';
import { TileData, HubId } from './types';
import { BackgroundProvider, useBackground } from './context/BackgroundContext';
import { AuroraBackground, MetroBackground } from './components/XboxBackgrounds';
import PulseNeonBackground from './components/PulseNeonBackground';
import FluidBackground from './components/FluidBackground';
import GlimmerBackground from './components/GlimmerBackground';
import { SpheresBackground } from './components/SpheresBackground';

const AppShell: React.FC = () => {
  const { bgMode, currentPalette, preferences } = useBackground();
  const [activeHubIndex, setActiveHubIndex] = useState(4);
  const [direction, setDirection] = useState(0);
  const prevIndex = useRef(activeHubIndex);

  const handleTileClick = (tile: TileData) => {};

  const changeHub = (newIndex: number) => {
    setDirection(newIndex > activeHubIndex ? 1 : newIndex < activeHubIndex ? -1 : 0);
    prevIndex.current = activeHubIndex;
    setActiveHubIndex(newIndex);
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === 'd') { if (activeHubIndex < HUBS.length - 1) changeHub(activeHubIndex + 1); }
      else if (e.key === 'ArrowLeft' || e.key === 'a') { if (activeHubIndex > 0) changeHub(activeHubIndex - 1); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [activeHubIndex]);

  // Compute dynamic hubs depending on sensorType
  const computedHubs = React.useMemo(() => {
    if (preferences.sensorType === 'KINECT') return HUBS;
    
    return HUBS.map(hub => {
      if (hub.id === HubId.Apps) { // This is the 'kinect test' tab
        return {
          ...hub,
          label: 'webcam test',
          // Only show tiles compatible with webcam. RGB Stream, Depth Stream (if simulated), Info, Video Settings
          // Hide motor and led controls.
          tiles: hub.tiles.filter(t => t.isWebcam || t.kinectControl === 'video-settings' || t.kinectControl === 'info')
        };
      }
      return hub;
    });
  }, [preferences.sensorType]);

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', color: currentPalette.tileText, position: 'relative' }}>
      
      {/* ── Fondo base sólido ── */}
      <div style={{ position: 'fixed', inset: 0, zIndex: -1, backgroundColor: '#050505' }} />

      {/* ── Todos los fondos (renderizado condicional para optimizar GPU) ── */}
      {bgMode === 'aurora' && <AuroraBackground />}
      {bgMode === 'pulse' && <PulseNeonBackground />}
      {bgMode === 'metro' && <MetroBackground />}
      {bgMode === 'spheres' && <SpheresBackground />}
      {bgMode === 'fluid' && <FluidBackground />}
      {bgMode === 'glimmer' && <GlimmerBackground />}

      {/* ── Scanlines ── */}
      <div className="scanlines" style={{ position: 'fixed', inset: 0, zIndex: 2, opacity: 0.06, pointerEvents: 'none' }} />

      {/* ── Header dinámico — Solo textos flotantes sin contenedor ── */}
      <div style={{ position: 'relative', zIndex: 40, width: '100%', paddingTop: 20, paddingBottom: 10 }}>
        <TopMenu hubs={computedHubs} activeIndex={activeHubIndex} onSelect={changeHub} />
      </div>

      {/* ── Contenido principal ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', overflow: 'hidden', position: 'relative', zIndex: 10 }}>
        <AnimatePresence mode='popLayout' custom={direction}>
          <motion.div
            key={activeHubIndex}
            custom={direction}
            initial={{ x: direction * 200, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: direction * -200, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 280, damping: 28 }}
            style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <HubView activeHub={computedHubs[activeHubIndex]} onTileClick={handleTileClick} direction={direction} />
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

const App: React.FC = () => (
  <BackgroundProvider>
    <AppShell />
  </BackgroundProvider>
);

export default App;