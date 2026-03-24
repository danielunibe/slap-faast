// Kinect API Service

const API_BASE = import.meta.env.VITE_BACKEND_URL
  ? `${import.meta.env.VITE_BACKEND_URL}/api`
  : 'http://127.0.0.1:5001/api';

const STREAM_BASE = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:5001';

export const KinectService = {
  // Streams
  getVideoStreamUrl: () => `${STREAM_BASE}/video_feed`,
  getDepthStreamUrl: () => `${STREAM_BASE}/depth_feed`,

  // Hardware Controls
  setTilt: async (angle: number) => {
    try {
      await fetch(`${API_BASE}/tilt/${angle}`);
    } catch (e) {
      console.error("Kinect Tilt Error:", e);
    }
  },

  setLed: async (mode: string) => {
    // Map string modes to libfreenect int codes
    const modeMap: Record<string, number> = {
      'OFF': 0, 'GRN': 1, 'RED': 2, 'YEL': 3, 'BLINK': 4
    };
    const val = modeMap[mode] ?? 1;
    try {
      await fetch(`${API_BASE}/led/${val}`);
    } catch (e) {
      console.error("Kinect LED Error:", e);
    }
  },

  setVideoEnabled: async (enabled: boolean) => {
    try {
      await fetch(`${API_BASE}/video/${enabled ? 1 : 0}`);
    } catch (e) {
      console.error("Kinect Video Toggle Error:", e);
    }
  },

  setDepthEnabled: async (enabled: boolean) => {
    try {
      await fetch(`${API_BASE}/depth/${enabled ? 1 : 0}`);
    } catch (e) {
      console.error("Kinect Depth Toggle Error:", e);
    }
  },

  setDepthColormap: async (cmap: number) => {
    try {
      await fetch(`${API_BASE}/colormap/${cmap}`);
    } catch (e) {
      console.error("Kinect Colormap Error:", e);
    }
  },

  // Status check
  getStatus: async () => {
    try {
      const res = await fetch(`${API_BASE}/status`);
      return await res.json();
    } catch (e) {
      return null;
    }
  }
};
