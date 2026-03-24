import React from 'react';
import { HubData } from '../types';
import { useBackground } from '../context/BackgroundContext';

interface TopMenuProps {
  hubs: HubData[];
  activeIndex: number;
  onSelect: (index: number) => void;
}

const ITEM_WIDTH = 200;

const TopMenu: React.FC<TopMenuProps> = ({ hubs, activeIndex, onSelect }) => {
  const { currentPalette, preferences } = useBackground();

  const t = (text: string) => {
    if (preferences.language === 'en') return text;
    const dict: Record<string, string> = {
      'dashboard': 'tablero',
      'gestures': 'gestos',
      'advanced controls': 'control avanzado',
      'magic hand': 'mano mágica',
      'kinect test': 'prueba kinect',
      'settings': 'ajustes'
    };
    return dict[text.toLowerCase()] || text;
  };

  return (
    <div className="w-full flex items-center overflow-hidden relative select-none" style={{ height: 56 }}>
      {/* Hub nav strip — no black backgrounds, just text */}
      <div
        className="flex items-center absolute left-0 transition-transform duration-500"
        style={{
          transitionTimingFunction: 'cubic-bezier(0.165,0.84,0.44,1)',
          transform: `translateX(calc(50vw - ${ITEM_WIDTH / 2}px - ${activeIndex * ITEM_WIDTH}px))`,
        }}
      >
        {hubs.map((hub, index) => {
          const isActive = index === activeIndex;
          const label = t(hub.label);
          return (
            <button
              key={hub.id}
              onClick={() => onSelect(index)}
              style={{ width: `${ITEM_WIDTH}px` }}
              className="flex justify-center items-center outline-none transition-all duration-500"
            >
              <span
                className="uppercase whitespace-nowrap font-display font-bold tracking-tight leading-none transition-all duration-500 ease-out"
                style={{
                  fontSize: isActive ? 24 : 14,
                  transform: isActive ? 'scale(1.08) translateY(10px)' : 'scale(1) translateY(0)',
                  opacity: isActive ? 1 : 0.5,
                  color: isActive ? currentPalette.tileText : currentPalette.tileSubtext,
                  textShadow: isActive 
                    ? `0 0 30px ${currentPalette.tileAccent}88, 0 4px 12px rgba(0,0,0,0.5)` 
                    : 'none',
                  letterSpacing: isActive ? '0.15em' : '0.05em',
                  display: 'inline-block'
                }}
              >
                {label}
              </span>
            </button>
          );
        })}
      </div>

    </div>
  );
};

export default TopMenu;