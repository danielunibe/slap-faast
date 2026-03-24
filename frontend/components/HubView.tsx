import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HubData } from '../types';
import Tile from './Tile';

interface HubViewProps {
  activeHub: HubData;
  onTileClick: (data: any) => void;
  direction: number;
}

const containerVariants = {
  hidden: (direction: number) => ({
    x: direction > 0 ? 300 : -300,
    opacity: 0,
    rotateY: direction > 0 ? 15 : -15, // Perspective tilt
  }),
  visible: {
    x: 0,
    opacity: 1,
    rotateY: 0,
    transition: {
      type: "spring",
      stiffness: 50,
      damping: 20,
      staggerChildren: 0.05, // This creates the internal parallax/flow effect
      delayChildren: 0.1,
    },
  },
  exit: (direction: number) => ({
    x: direction < 0 ? 300 : -300,
    opacity: 0,
    scale: 0.9,
    rotateY: direction < 0 ? -15 : 15,
    transition: {
      duration: 0.3,
      ease: "easeInOut"
    }
  })
};

const tileVariants = {
  hidden: { x: 50, opacity: 0 },
  visible: { 
    x: 0, 
    opacity: 1,
    transition: { type: "spring", stiffness: 100, damping: 15 }
  },
  exit: { opacity: 0, scale: 0.9 }
};

const HubView: React.FC<HubViewProps> = ({ activeHub, onTileClick, direction }) => {
  return (
    <div className="w-full h-[65vh] min-h-[420px] max-h-[75vh] flex justify-center items-center perspective-1000 overflow-visible px-4 my-auto">
      <AnimatePresence mode="wait" custom={direction}>
        <motion.div
          key={activeHub.id}
          custom={direction}
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          className="grid gap-3 h-full mx-auto"
          // Centered Grid Configuration
          style={{ 
             display: 'grid',
             gridTemplateRows: 'repeat(3, 1fr)',
             gridAutoFlow: 'column dense',
             gridAutoColumns: '240px', 
             justifyContent: 'center', // Essential for centering the whole block
             alignContent: 'center',
          }}
        >
          {activeHub.tiles.map((tile) => (
            <motion.div key={tile.id} variants={tileVariants} className={`contents`}>
                <Tile data={tile} onClick={onTileClick} />
            </motion.div>
          ))}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default HubView;