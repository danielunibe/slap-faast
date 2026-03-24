import React from 'react';

export enum TileSize {
  Small = 'small',   // 1x1
  Medium = 'medium', // 2x1 or 1x2 depending on context
  Large = 'large',   // 2x2
  Wide = 'wide'      // 2x1 horizontal
}

export type KinectControlType = 
  | 'motor' 
  | 'led' 
  | 'video-settings' 
  | 'depth-settings' 
  | 'info' 
  | 'hand-monitor'   // Visualizer for Magic Hand
  | 'analytics'      // Stats for Dashboard
  | 'gesture-tune'   // Sliders for tuning
  | 'gesture-action' // Buttons for Rec/Test/Del
  | 'sensor-config' // New: Toggle between Kinect 1414 and Webcam
  | 'background-settings'
  | 'preferences'
  | 'tile-settings';

export interface TileData {
  id: string;
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  image?: string;
  color?: string; // Hex code or tailwind class
  size: TileSize;
  action?: () => void;
  isWebcam?: boolean;
  kinectControl?: KinectControlType;
  // Metadata for specific controls
  statValue?: string; 
  statLabel?: string;
}

export interface HubData {
  id: string;
  label: string;
  tiles: TileData[];
}

export enum HubId {
  Social = 'social',
  LiveTV = 'livetv',
  Video = 'video',
  Games = 'games',
  Music = 'music',
  Apps = 'apps',
  Settings = 'settings'
}