# How to Run AISEO Multi-LLM Query Tool

## ✅ Current Status
The application is **FULLY FUNCTIONAL** and ready to use!

## 🚀 Quick Start

### Option 1: Simple Launch (Recommended)
```bash
# Make sure you're in the project directory
cd /Users/sjonas/aiseo-ui/aiseo

# Run the launch script
./launch.sh
```

This will:
- Start the backend API server on port 5555
- Start the frontend server on port 8080
- Open http://localhost:8080/index-simple.html in your browser

### Option 2: Manual Start

#### 1. Start Backend
```bash
cd backend
python3 app.py
# Backend runs on http://localhost:5555
```

#### 2. Start Frontend (in new terminal)
```bash
cd frontend
python3 -m http.server 8080
# Frontend runs on http://localhost:8080
```

#### 3. Open Browser
Navigate to: http://localhost:8080/index-simple.html

## 🔍 Testing the Application

### 1. Check Backend Health
```bash
curl http://localhost:5555/api/health
```

### 2. Check Available Providers
```bash
curl http://localhost:5555/api/providers
```

### 3. Use the Web Interface
1. Open http://localhost:8080/index-simple.html
2. Enter a query in the input field
3. Click the submit button
4. Watch responses stream in real-time

## 📝 Current Configuration

### Working Components:
- ✅ Backend Flask API (Port 5555)
- ✅ WebSocket support for real-time streaming
- ✅ Simple HTML frontend (No Node.js required)
- ✅ API endpoints (health, providers, query)
- ✅ Provider: Anthropic (Claude) is configured

### API Keys Configured:
- ✅ Anthropic API key is active
- ⚠️ Other providers need API keys in .env file

## 🛠 Troubleshooting

### Port Already in Use
If you see "Port 5555 is in use":
```bash
# Kill the process using the port
lsof -ti:5555 | xargs kill -9
```

### Backend Not Starting
Check the logs:
```bash
cat backend/backend.log
```

### Frontend Not Loading
Make sure you're accessing the correct URL:
- Use: http://localhost:8080/index-simple.html
- NOT: http://localhost:8080/

## 📁 File Structure
```
aiseo/
├── backend/
│   └── app.py           # Flask API server (running on 5555)
├── frontend/
│   └── index-simple.html # Simple HTML UI (no build required)
├── launch.sh            # One-command launcher
└── .env                 # API keys configuration
```

## 🎯 What's Working Now

1. **Backend API** - Fully functional Flask server
2. **WebSocket** - Real-time response streaming
3. **Simple UI** - Clean, responsive interface
4. **Anthropic Claude** - Configured and ready
5. **Query Processing** - Submit queries and get responses

## 🔥 Ready to Use!

The application is fully functional. Just run `./launch.sh` and start querying!

### Test Query Examples:
- "What are the best practices for SEO in 2024?"
- "How do I optimize my website for AI search engines?"
- "Compare different LLM providers"
- "What is AISEO and why is it important?"

## 📊 Live Endpoints

With the servers running, these endpoints are available:

- **Frontend UI**: http://localhost:8080/index-simple.html
- **API Health**: http://localhost:5555/api/health
- **API Providers**: http://localhost:5555/api/providers
- **API Query**: POST http://localhost:5555/api/query

## 🎉 Success!

Your AISEO Multi-LLM Query Tool is now fully operational!