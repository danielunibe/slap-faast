import math
import time

class OneEuroFilter:
    def __init__(self, min_cutoff=1.0, beta=0.0):
        self._min_cutoff = min_cutoff
        self._beta = beta
        self._x_filter = LowPassFilter()
        self._dx_filter = LowPassFilter()
        self._last_time = None

    def filter(self, x, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
            
        if self._last_time is None:
            self._last_time = timestamp
            return self._x_filter.filter(x)
            
        dt = timestamp - self._last_time
        self._last_time = timestamp
        
        # Avoid division by zero
        if dt <= 0: return self._x_filter.last_re
        
        dx = (x - self._x_filter.last_raw) / dt
        edx = self._dx_filter.filter(dx, self._alpha(dt, self._d_cutoff(edx if 'edx' in locals() else 0.0)))
        
        cutoff = self._min_cutoff + self._beta * abs(edx)
        return self._x_filter.filter(x, self._alpha(dt, cutoff))

    def _alpha(self, dt, cutoff):
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def _d_cutoff(self, dx):
        # 1Hz default for derivative cutoff
        return 1.0

class LowPassFilter:
    def __init__(self):
        self.last_raw = 0.0
        self.last_re = 0.0
        self.initialized = False
        
    def filter(self, x, alpha=1.0):
        if not self.initialized:
            self.last_raw = x
            self.last_re = x
            self.initialized = True
            return x
            
        self.last_re = alpha * x + (1.0 - alpha) * self.last_re
        self.last_raw = x
        return self.last_re

class PointFilter:
    """Filtra puntos 3D (x, y, z) usando One Euro Filter."""
    def __init__(self, min_cutoff=1.0, beta=0.007):
        self.fx = OneEuroFilter(min_cutoff, beta)
        self.fy = OneEuroFilter(min_cutoff, beta)
        self.fz = OneEuroFilter(min_cutoff, beta)
        
    def filter(self, x, y, z, timestamp=None):
        nx = self.fx.filter(x, timestamp)
        ny = self.fy.filter(y, timestamp)
        nz = self.fz.filter(z, timestamp)
        return nx, ny, nz
