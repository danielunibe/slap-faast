import React from 'react';
import { Gamepad2, Users, Tv, Music, Settings, AppWindow, ShoppingBag, MessageSquare, Disc, Play, Trophy, User, MoveVertical, Zap, Info, Video, Eye, ScanLine, Hand, Activity, BarChart3, Target, RefreshCw, Trash2, PlusCircle, Sliders, Layers, Image as ImageIcon, Wand2, Crop, Aperture, Camera } from 'lucide-react';
import { HubData, HubId, TileSize } from './types';

export const HUBS: HubData[] = [
  {
    id: HubId.Social,
    label: 'dashboard',
    tiles: [
      { id: 'd1', title: 'Total Gestures', subtitle: 'Lifetime', icon: <Activity size={32} />, size: TileSize.Medium, color: 'bg-[#222222]', kinectControl: 'analytics', statValue: '8,432', statLabel: 'Detected' },
      { id: 'd2', title: 'Accuracy', subtitle: 'Session', icon: <Target size={32} />, size: TileSize.Small, color: 'bg-[#333333]', kinectControl: 'analytics', statValue: '98%', statLabel: 'Precision' },
      { id: 'd3', title: 'Active Time', subtitle: 'Today', icon: <ScanLine size={32} />, size: TileSize.Small, color: 'bg-[#1a1a1a]', kinectControl: 'analytics', statValue: '2h 14m', statLabel: 'Uptime' },
      { id: 'd4', title: 'Top Gesture', subtitle: 'Most Used', icon: <Hand size={32} />, size: TileSize.Large, color: 'bg-black', kinectControl: 'analytics', statValue: 'SWIPE_UP', statLabel: '450 times' },
      { id: 'd5', title: 'Errors', subtitle: 'Logs', icon: <Info size={32} />, size: TileSize.Wide, color: 'bg-[#2d2d2d]', kinectControl: 'analytics', statValue: '12', statLabel: 'Failures' },
    ]
  },
  {
    id: HubId.LiveTV,
    label: 'gestures',
    tiles: [
      { id: 'gt1', title: 'New Gesture', subtitle: 'Record', icon: <PlusCircle size={40} />, size: TileSize.Large, color: 'bg-[#111]', kinectControl: 'gesture-action' },
      { id: 'gt2', title: 'Sensitivity', subtitle: 'Fine Tune', icon: <Sliders size={32} />, size: TileSize.Medium, color: 'bg-[#333]', kinectControl: 'gesture-tune' },
      { id: 'gt3', title: 'Test Zone', subtitle: 'Sandbox', icon: <Play size={32} />, size: TileSize.Medium, color: 'bg-[#222]', kinectControl: 'gesture-action' },
      { id: 'gt4', title: 'Redo Last', icon: <RefreshCw size={24} />, size: TileSize.Small, color: 'bg-[#444]', kinectControl: 'gesture-action' },
      { id: 'gt5', title: 'Clear All', icon: <Trash2 size={24} />, size: TileSize.Small, color: 'bg-[#1a1a1a]', kinectControl: 'gesture-action' },
    ]
  },
  {
    id: HubId.Games,
    label: 'advanced controls',
    tiles: [
      { id: 'f1', title: 'Image Analyzer', subtitle: 'Process Stream', icon: <ImageIcon size={48} />, size: TileSize.Large, color: 'bg-[#333]' },
      { id: 'f2', title: 'Object Detect', subtitle: 'Bounding Box', icon: <ScanLine size={32} />, size: TileSize.Wide, color: 'bg-[#222]' },
      { id: 'f3', title: 'Smart Crop', subtitle: 'Auto-Frame', icon: <Crop size={32} />, size: TileSize.Small, color: 'bg-[#1a1a1a]' },
      { id: 'f4', title: 'Filters', subtitle: 'FX Library', icon: <Wand2 size={32} />, size: TileSize.Small, color: 'bg-[#444]' },
      { id: 'f5', title: 'Contrast', subtitle: 'Adjust', icon: <Aperture size={32} />, size: TileSize.Small, color: 'bg-[#2d2d2d]' },
      { id: 'f6', title: 'Depth Map', subtitle: 'Visualizer', icon: <Layers size={32} />, size: TileSize.Medium, color: 'bg-[#1a1a1a]' },
    ]
  },
  {
    id: HubId.Music,
    label: 'magic hand',
    tiles: [
      { id: 'mh1', title: 'Hand Monitor', subtitle: 'Detection Board', icon: <Hand size={40} />, size: TileSize.Large, color: 'bg-black', kinectControl: 'hand-monitor' },
      { id: 'mh2', title: 'Effect: Particle', subtitle: 'Visual FX', icon: <Wand2 size={32} />, size: TileSize.Wide, color: 'bg-[#333]' },
      { id: 'mh3', title: 'Physics', subtitle: 'Collision', icon: <Activity size={32} />, size: TileSize.Small, color: 'bg-[#222]' },
      { id: 'mh4', title: 'Show Skeleton', subtitle: 'Debug', icon: <Eye size={32} />, size: TileSize.Small, color: 'bg-[#1a1a1a]' },
    ]
  },
  {
    id: HubId.Apps,
    label: 'kinect test',
    tiles: [
      { id: 'ki1', title: 'Info', icon: <Info size={32} />, size: TileSize.Small, color: 'bg-[#0072c6]', kinectControl: 'info' },
      { id: 'ki2', title: 'LED', icon: <Zap size={32} />, size: TileSize.Small, color: 'bg-[#2d2d2d]', kinectControl: 'led' },
      { id: 'ki3', title: 'Motor', icon: <MoveVertical size={32} />, size: TileSize.Small, color: 'bg-[#444444]', kinectControl: 'motor' },
      { id: 'k1', title: 'RGB Stream', subtitle: '640x480 • 30FPS', icon: <Video size={32} />, size: TileSize.Large, color: 'bg-black', isWebcam: true },
      { id: 'ks1', title: 'Video', icon: <Settings size={32} />, size: TileSize.Wide, color: 'bg-[#662d91]', kinectControl: 'video-settings' },
      { id: 'k2', title: 'Depth Stream', subtitle: 'Colormap: Jet', icon: <Eye size={32} />, size: TileSize.Large, color: 'bg-[#1a1a1a]', isWebcam: true },
      { id: 'ks2', title: 'Depth', icon: <ScanLine size={32} />, size: TileSize.Wide, color: 'bg-[#662d91]', kinectControl: 'depth-settings' },
    ]
  },
  {
    id: HubId.Settings,
    label: 'settings',
    tiles: [
      { id: 'set-src', title: 'Input Source', subtitle: 'Sensor Config', icon: <Camera size={40} />, size: TileSize.Wide, color: 'bg-[#333]', kinectControl: 'sensor-config' },
      { id: 'set-bg', title: 'Background', subtitle: 'Visual Theme', icon: <Layers size={40} />, size: TileSize.Large, color: 'bg-[#111]', kinectControl: 'background-settings' },
      { id: 'set1', title: 'Tile Style', subtitle: 'Opacity & Blur', icon: <Settings size={40} />, size: TileSize.Large, kinectControl: 'tile-settings' },
      { id: 'set2', title: 'Profile', icon: <User size={32} />, size: TileSize.Wide, color: 'bg-[#666666]' },
      { id: 'set3', title: 'Preferences', subtitle: 'Language & Devices', icon: <Settings size={32} />, size: TileSize.Medium, color: 'bg-[#555555]', kinectControl: 'preferences' },
    ]
  },
];