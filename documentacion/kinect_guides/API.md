# Kinect Dashboard API Documentation

## Base URL
```
http://localhost:5001
```

---

## API Endpoints

### Status

#### `GET /api/status`
Get current Kinect device status

**Response:**
```json
{
  "connected": true,
  "tilt": 0,
  "led": 1,
  "video_enabled": true,
  "depth_enabled": true
}
```

**Fields:**
- `connected` (boolean): Kinect connection status
- `tilt` (integer): Current motor angle (-30 to 30)
- `led` (integer): LED mode (0=OFF, 1=GREEN, 2=RED, 3=YELLOW, 4=BLINK)
- `video_enabled` (boolean): RGB video stream status
- `depth_enabled` (boolean): Depth stream status

---

### Motor Control

#### `GET /api/tilt/<angle>`
Set Kinect motor tilt angle

**Parameters:**
- `angle` (integer): Tilt angle in degrees (-30 to 30)

**Example:**
```bash
curl http://localhost:5001/api/tilt/15
```

**Response:**
```json
{
  "success": true,
  "angle": 15
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Invalid angle"
}
```

---

### LED Control

#### `GET /api/led/<mode>`
Set Kinect LED status

**Parameters:**
- `mode` (integer): LED mode
  - `0` - OFF
  - `1` - GREEN
  - `2` - RED
  - `3` - YELLOW
  - `4` - BLINK

**Example:**
```bash
curl http://localhost:5001/api/led/1
```

**Response:**
```json
{
  "success": true,
  "mode": 1
}
```

---

### Video Stream Control

#### `GET /api/video/<enabled>`
Enable or disable RGB video stream

**Parameters:**
- `enabled` (integer): 1 to enable, 0 to disable

**Example:**
```bash
curl http://localhost:5001/api/video/1
```

**Response:**
```json
{
  "success": true,
  "enabled": true
}
```

---

### Depth Stream Control

#### `GET /api/depth/<enabled>`
Enable or disable depth stream

**Parameters:**
- `enabled` (integer): 1 to enable, 0 to disable

**Example:**
```bash
curl http://localhost:5001/api/depth/1
```

**Response:**
```json
{
  "success": true,
  "enabled": true
}
```

---

### Colormap Control

#### `GET /api/colormap/<cmap>`
Set depth visualization colormap

**Parameters:**
- `cmap` (integer): OpenCV colormap ID
  - `2` - JET (default)
  - `0` - AUTUMN
  - `1` - BONE
  - `3` - WINTER
  - `4` - RAINBOW
  - `11` - HOT
  - `12` - COOL

**Example:**
```bash
curl http://localhost:5001/api/colormap/2
```

**Response:**
```json
{
  "success": true,
  "colormap": 2
}
```

---

## Streaming Endpoints

### Video Feed

#### `GET /video_feed`
MJPEG stream of RGB video

**Response Type:** `multipart/x-mixed-replace; boundary=frame`

**Usage in HTML:**
```html
<img src="http://localhost:5001/video_feed" />
```

**Properties:**
- Resolution: 640x480
- Format: JPEG
- Quality: 80%
- Frame Rate: ~30 FPS

---

### Depth Feed

#### `GET /depth_feed`
MJPEG stream of depth data (colorized)

**Response Type:** `multipart/x-mixed-replace; boundary=frame`

**Usage in HTML:**
```html
<img src="http://localhost:5001/depth_feed" />
```

**Properties:**
- Resolution: 640x480
- Format: JPEG (colormap applied)
- Quality: 80%
- Frame Rate: ~30 FPS
- Colormap: Configurable via `/api/colormap`

---

## Error Codes

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 500 | Internal Server Error |

---

## CORS Configuration

The API has CORS enabled for all origins:
```python
CORS(app)
```

This allows frontend applications on different ports to access the API.

---

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider adding rate limiting middleware.

---

## WebSocket Support

Not currently implemented. All communication is via HTTP REST API and MJPEG streams.

---

## Example Usage (JavaScript)

### Fetch Status
```javascript
const response = await fetch('http://localhost:5001/api/status');
const status = await response.json();
console.log(status);
```

### Set Motor Angle
```javascript
const angle = 15;
await fetch(`http://localhost:5001/api/tilt/${angle}`);
```

### Set LED
```javascript
const mode = 1; // GREEN
await fetch(`http://localhost:5001/api/led/${mode}`);
```

### Display Video Stream
```javascript
const videoElement = document.querySelector('video');
videoElement.src = 'http://localhost:5001/video_feed';
```

---

## Notes

- All endpoints return JSON except streaming endpoints
- Motor angle is clamped to [-30, 30] range
- Streams use MJPEG format for browser compatibility
- Backend must be running for all endpoints to work

---

**Last Updated:** 2025-12-31
