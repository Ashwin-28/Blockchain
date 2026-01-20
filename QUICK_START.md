# 🚀 Quick Start Guide

## Option 1: Automatic Startup (Easiest)

**Double-click this file:**
```
START_SYSTEM.bat
```

This will automatically:
1. ✅ Start the backend server (Flask on port 5000)
2. ✅ Start the frontend server (React on port 3000)
3. ✅ Open your browser to http://localhost:3000

---

## Option 2: Manual Startup

### Terminal 1 - Backend
```bash
cd c:\Users\Ramanathan\Desktop\Kavin\Blockchain_AG\backend
python app.py
```

### Terminal 2 - Frontend
```bash
cd c:\Users\Ramanathan\Desktop\Kavin\Blockchain_AG\frontend
npm start
```

### Browser
Open: http://localhost:3000

---

## 🎯 What to Test

Once the system is running:

### 1. **Test Existing Facial Recognition** ✅
- Go to: http://localhost:3000/enroll
- Click "Capture Biometric"
- Allow camera permissions
- Your face will be detected and enrolled!

### 2. **Test New ZKP Authentication** 🆕
- Go to: http://localhost:3000/zkp-auth
- Enter a Subject ID
- Capture your biometric
- See Zero-Knowledge Proof generation!

### 3. **Test Multimodal Fusion** 🆕
- Go to: http://localhost:3000/multimodal
- Select multiple biometric types
- Capture each one
- See fusion score calculation!

### 4. **Test DAO Governance** 🆕
- Go to: http://localhost:3000/dao
- View active proposals
- Cast votes
- See treasury management!

---

## 🔧 Troubleshooting

### Backend won't start?
```bash
# Install dependencies
cd backend
pip install -r requirements.txt
```

### Frontend won't start?
```bash
# Install dependencies
cd frontend
npm install
```

### Camera not working?
- Allow camera permissions in browser
- Use Chrome or Edge (best compatibility)
- Check if another app is using the camera

---

## 📊 System Status

Check if servers are running:
- **Backend**: http://localhost:5000/api/health
- **Frontend**: http://localhost:3000

---

## 🎉 Features Available

| Feature | URL | Status |
|---------|-----|--------|
| Home | http://localhost:3000/ | ✅ Ready |
| Enroll | http://localhost:3000/enroll | ✅ Ready |
| Authenticate | http://localhost:3000/authenticate | ✅ Ready |
| **ZKP Auth** | http://localhost:3000/zkp-auth | 🆕 New |
| **Multimodal** | http://localhost:3000/multimodal | 🆕 New |
| Dashboard | http://localhost:3000/dashboard | ✅ Ready |
| **DAO** | http://localhost:3000/dao | 🆕 New |
| Blockchain | http://localhost:3000/blockchain | ✅ Ready |
| About | http://localhost:3000/about | ✅ Ready |

---

**Enjoy your enhanced biometric verification system!** 🚀
