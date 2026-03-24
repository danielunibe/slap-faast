# Slap!Faast - Kinect Dashboard Setup Guide

## Prerequisites

### Hardware Requirements
- **Kinect v1 (Model 1414)** - Xbox 360 Kinect sensor
- USB 2.0 or 3.0 port
- Windows 10/11 (64-bit)

### Software Requirements
- **Python 3.8+**
- **Node.js 18+** and npm
- **libfreenect drivers** (included in project)

---

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Slap!Faast"
```

### 2. Backend Setup (Python/Flask)

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Verify Kinect Connection
```bash
python scan_usb_devices.py
```
You should see the Kinect device listed.

### 3. Frontend Setup (React/Vite)

#### Navigate to Frontend Directory
```bash
cd frontend
```

#### Install Node Dependencies
```bash
npm install
```

#### Configure Environment Variables
```bash
# Copy the example file
copy .env.example .env.local

# Edit .env.local and set:
VITE_BACKEND_URL=http://localhost:5001
VITE_DEBUG_MODE=false
```

---

## Running the Application

### Start Backend Server
```bash
# From project root
python kinect_server.py
```

The backend will start on `http://localhost:5001`

### Start Frontend Development Server
```bash
# From frontend directory
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

---

## Kinect Driver Setup

### Option 1: Using Zadig (Recommended)
1. Run `zadig.exe` (included in project)
2. Select **Options → List All Devices**
3. Find **Xbox NUI Camera** or **Xbox NUI Motor**
4. Install **libusbK** driver
5. Repeat for all Kinect devices

See `ZADIG_GUIDE_KINECT.md` for detailed instructions.

### Option 2: Using Microsoft Kinect SDK
1. Run `KinectSDK-v1.8-Setup.exe` (included)
2. Follow installation wizard
3. Restart computer

See `KINECT_SDK_GUIDE.md` for more details.

---

## Troubleshooting

### Kinect Not Detected
- Check USB connection
- Verify drivers are installed correctly
- Try different USB port
- Check `system.log` for errors

### Backend Won't Start
```bash
# Check if Flask is installed
python -c "import flask; print(flask.__version__)"

# If not, install manually
pip install Flask flask-cors
```

### Frontend Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Video Stream Not Working
- Ensure backend is running on port 5001
- Check browser console for CORS errors
- Verify `VITE_BACKEND_URL` in `.env.local`

---

## Project Structure

```
Slap!Faast/
├── frontend/              # React/TypeScript frontend
│   ├── components/        # React components
│   ├── services/          # API services
│   ├── .env.example       # Environment template
│   └── package.json
├── kinect_server.py       # Flask backend server
├── requirements.txt       # Python dependencies
├── freenect.dll          # libfreenect library
└── README.md
```

---

## Development Workflow

### Making Changes

1. **Frontend changes**: Edit files in `frontend/`, hot reload is enabled
2. **Backend changes**: Restart `kinect_server.py`
3. **Test changes**: Check both terminal outputs for errors

### Building for Production

```bash
# Frontend
cd frontend
npm run build

# Output will be in frontend/dist/
```

---

## Additional Resources

- [API Documentation](API.md)
- [Hardware Guide](HARDWARE.md)
- [Kinect Quick Start](KINECT_QUICK_START.md)
- [Zadig Driver Guide](ZADIG_GUIDE_KINECT.md)

---

## Support

For issues or questions:
1. Check `system.log` for backend errors
2. Check browser console for frontend errors
3. Review troubleshooting section above
4. Check existing documentation files

---

**Last Updated:** 2025-12-31
