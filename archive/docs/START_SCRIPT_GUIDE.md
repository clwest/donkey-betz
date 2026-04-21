# 🚀 UNIFIED START SCRIPT - start_ws_quick.sh

## ✅ **Everything You Need in One Command!**

Your `start_ws_quick.sh` script has been **completely enhanced** with all the fixes and improvements we made today!

## 📋 **What the Script Does:**

### 1. **Pre-flight Checks** ✈️
- ✅ Stops any existing servers (clean slate)
- ✅ Activates Python virtual environment
- ✅ Verifies Redis is running
- ✅ Verifies PostgreSQL is running
- ✅ Runs database migrations
- ✅ Clears frontend cache

### 2. **Starts Backend** 🔧
- ✅ Uses Daphne for WebSocket support
- ✅ Correct API token configured: `<redacted-0fb2390d-2026-04-20>`
- ✅ Verifies backend is responding
- ✅ Counts and displays available agents (should show 150!)
- ✅ Logs output to `ai_core.log`

### 3. **Starts Frontend** ⚛️
- ✅ Installs dependencies if needed
- ✅ Clears Vite cache for fresh start
- ✅ Runs on port **3000** (not 5173)
- ✅ Uses enhanced Command Center with all 150 agents
- ✅ Logs output to `frontend.log`

### 4. **Monitoring & Cleanup** 📊
- ✅ Shows live status of all services
- ✅ Displays all important URLs
- ✅ Shows authentication credentials
- ✅ Gracefully stops everything on Ctrl+C
- ✅ Monitors services and alerts if they crash

## 🎯 **How to Use:**

### **First Time Setup:**
```bash
# Make the script executable (only needed once)
chmod +x start_ws_quick.sh
```

### **Start Everything:**
```bash
./start_ws_quick.sh
```

### **What You'll See:**
```
🚀 UNIFIED DONKEY BETZ - FULL PLATFORM START
=================================================
✅ Activating Python virtual environment
✅ Redis is running
✅ PostgreSQL is running
✅ Database ready
✅ Backend is running on port 8000
✅ API Connected: Found 150 AI Agents ready!
✅ Starting frontend on port 3000...

=================================================
🎉 PLATFORM STARTED SUCCESSFULLY!
=================================================

📊 System Status:
  Backend:   ✅ Running (PID: 12345)
  Frontend:  ✅ Running (PID: 12346)
  WebSocket: ✅ Available
  Agents:    150 AI Agents Available

🌐 Access URLs:
  Command Center:  http://localhost:3000/control-center
  Agent Library:   http://localhost:3000/control-center (Agents Tab)
  Dashboard:       http://localhost:3000/dashboard
  Backend API:     http://localhost:8000/api/v1/
  Admin Panel:     http://localhost:8000/admin/

🔑 Authentication:
  API Token: 0fb2390dedd5cc47ec7e...
  Username:  command_center
  Password:  donkeybetz123

🎯 Quick Actions:
  1. Open http://localhost:3000/control-center
  2. Go to 'Command' tab to execute agents
  3. Go to 'Agents' tab to browse all 150 agents
  4. Go to 'Test' tab to verify connectivity
```

## 📍 **Key Features Now Available:**

### **Command Center** (http://localhost:3000/control-center)
- **Command Tab**: Execute any of 150 agents with custom tasks
- **Agents Tab**: Browse all agents in a visual grid
- **Test Tab**: Live connectivity testing
- **Profile Tab**: User settings
- **AI Config Tab**: Model preferences
- **Revenue Tab**: Track earnings
- **Opportunities Tab**: Available tasks

### **What's Different from Before:**
| Old Version | New Enhanced Version |
|------------|---------------------|
| No agent list | **150 agents loaded** |
| Static UI | **Real-time WebSocket updates** |
| Manual API calls | **Agent dropdown selector** |
| No execution history | **Track all executed tasks** |
| No connectivity test | **Built-in API testing** |

## 🔧 **Troubleshooting:**

### If agents don't show up:
1. Check `ai_core.log` for errors
2. Verify token in script matches backend
3. Run `python quick-api-test.py` to verify

### If frontend doesn't update:
1. Hard refresh browser (Cmd/Ctrl + Shift + R)
2. Clear browser cache
3. Check `frontend.log` for compilation errors

### To view logs:
```bash
# Backend logs
tail -f ai_core.log

# Frontend logs  
tail -f frontend.log

# Both logs
tail -f *.log
```

### To stop everything:
Simply press **Ctrl+C** - the script will cleanly shut down all services.

## 🎉 **Success Checklist:**

After running `./start_ws_quick.sh`, verify:

- [ ] Script shows "Found **150 AI Agents** ready!"
- [ ] Browser opens to http://localhost:3000
- [ ] Command Center shows "**Enhanced Command Center**" title
- [ ] Total Agents card shows **150**
- [ ] Agent dropdown has agents listed
- [ ] Test tab shows all green checkmarks

## 🚀 **You're All Set!**

Your unified start script now includes:
- ✅ All API fixes
- ✅ Correct authentication token
- ✅ Enhanced UI components
- ✅ 150 agents ready to execute
- ✅ WebSocket support
- ✅ Automatic monitoring
- ✅ Clean shutdown

Just run `./start_ws_quick.sh` and your entire Multi-Agent AI Platform will be up and running with all 150 agents ready to execute your commands! 🤖⚡

---
*Updated: September 19, 2025 - All systems integrated and ready!*