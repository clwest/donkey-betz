# 🎯 QUICK REFERENCE - PORT 3000

## ✅ You Were Right!
Your frontend is configured to run on **port 3000**, not 5173!

## 📋 Correct URLs (Port 3000)

### Main Pages
- **Command Center**: http://localhost:3000/control-center
- **Agent Orchestra**: http://localhost:3000/agent-orchestra
- **Dashboard**: http://localhost:3000/dashboard
- **AI Settings**: http://localhost:3000/ai-settings
- **Opportunities**: http://localhost:3000/opportunities
- **Connectivity Test**: http://localhost:3000/connectivity-test

## 🔧 Why This Works

Your `vite.config.ts` has smart proxy settings:
```typescript
server: {
  port: 3000,  // ← Frontend runs here!
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // ← Forwards to Django
    },
    '/ws': {
      target: 'ws://localhost:8000',    // ← WebSocket proxy
    }
  }
}
```

This means:
- Frontend: **http://localhost:3000**
- Backend API: **http://localhost:8000**
- But from frontend, just use `/api/` (proxy handles it!)

## 🚀 Quick Start

```bash
# Option 1: Use the start script
chmod +x start-frontend.sh
./start-frontend.sh

# Option 2: Manual start
cd frontend
npm run dev
# Browser opens automatically at http://localhost:3000
```

## ✅ System Ports Summary

| Service | Port | URL |
|---------|------|-----|
| Frontend (Vite) | **3000** | http://localhost:3000 |
| Backend (Django) | **8000** | http://localhost:8000 |
| Database (PostgreSQL) | **5432** | localhost:5432 |
| Redis | **6379** | localhost:6379 |

## 🎊 All Set!

Your configuration is correct! The frontend runs on **port 3000** and all documentation has been updated to reflect this.

---
*Port configuration confirmed: Frontend on 3000, Backend on 8000*
