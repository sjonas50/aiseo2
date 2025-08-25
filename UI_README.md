# AISEO Multi-LLM Query Tool - Frontend UI

A modern, responsive web interface for the AISEO Multi-LLM Query Tool, inspired by BrandLight.ai's design. Compare responses from multiple AI providers (OpenAI, Anthropic, Google Gemini, Perplexity) and Google Search in real-time.

## Features

### Core Functionality
- **Multi-Provider Querying**: Send queries to multiple LLMs simultaneously
- **Real-time Streaming**: WebSocket-based live response updates
- **Provider Selection**: Choose which AI providers to query
- **Response Comparison**: Side-by-side comparison of all responses
- **AISEO Analysis**: AI-powered analysis of responses for SEO insights
- **Export Results**: Download results in JSON or CSV format
- **Query History**: View and re-run previous queries

### UI/UX Features
- **Modern Dark Theme**: Sleek, professional design inspired by BrandLight.ai
- **Animated Components**: Smooth transitions and engaging animations
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Typewriter Effect**: Live typing animation for responses
- **Gradient Animations**: Dynamic gradient backgrounds
- **Loading States**: Beautiful loading animations for each provider

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for blazing fast builds
- **TailwindCSS** for styling
- **Framer Motion** for animations
- **React Query** for API state management
- **Socket.io Client** for WebSocket connections
- **Lucide React** for icons

### Backend
- **Flask** REST API server
- **Flask-SocketIO** for WebSocket support
- **Flask-CORS** for cross-origin requests
- Integration with existing Python LLM query system

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- API keys for the providers you want to use

### Installation

1. **Clone the repository**:
```bash
cd aiseo-ui/aiseo
```

2. **Install all dependencies**:
```bash
# Install backend dependencies
cd backend
pip3 install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

3. **Configure API keys**:
Make sure your `.env` file in the root directory contains your API keys:
```env
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
PERPLEXITY_API_KEY=your-key-here
GOOGLE_SEARCH_API_KEY=your-key-here
GOOGLE_SEARCH_CX=your-cx-here
```

### Running the Application

#### Option 1: Run Backend and Frontend Separately

**Backend**:
```bash
cd backend
python3 app.py
# Server runs on http://localhost:5000
```

**Frontend**:
```bash
cd frontend
npm run dev
# UI runs on http://localhost:5173
```

#### Option 2: Run with Concurrently (Recommended)
```bash
# From root directory
npm install -g concurrently
npm run dev
# This starts both backend and frontend
```

#### Option 3: Docker Deployment
```bash
docker-compose up --build
# Access the UI at http://localhost:3000
```

## Project Structure

```
aiseo-ui/aiseo/
├── backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Backend dependencies
│   └── Dockerfile          # Backend container
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Header.tsx          # Navigation header
│   │   │   ├── QueryInput.tsx      # Animated query input
│   │   │   ├── ProviderCards.tsx   # Provider selection cards
│   │   │   └── ResponseDisplay.tsx # Response viewer
│   │   ├── services/       # API and WebSocket services
│   │   │   └── api.ts      # API client and WebSocket manager
│   │   ├── App.tsx         # Main application
│   │   └── index.css       # Tailwind styles
│   ├── package.json        # Frontend dependencies
│   ├── vite.config.ts      # Vite configuration
│   ├── tailwind.config.js  # Tailwind configuration
│   ├── Dockerfile          # Frontend container
│   └── nginx.conf          # Nginx configuration
├── docker-compose.yml      # Container orchestration
└── package.json           # Root package scripts
```

## API Endpoints

### REST API
- `GET /api/health` - Health check
- `GET /api/providers` - Get configured providers
- `POST /api/query` - Submit a query
- `GET /api/results/:id` - Get query results
- `GET /api/analysis/:id` - Get AISEO analysis
- `GET /api/history` - Get query history
- `GET /api/export/:id` - Export results (JSON/CSV)

### WebSocket Events
- `connect` - Client connection
- `join_query` - Join query room for updates
- `provider_start` - Provider processing started
- `provider_complete` - Provider response ready
- `analysis_complete` - AISEO analysis ready
- `query_complete` - All processing complete

## UI Components

### Header
- Fixed navigation with animated logo
- Links to Dashboard, Compare, Analytics, History
- Mobile-responsive hamburger menu

### QueryInput
- Animated placeholder text rotation
- Quick action buttons for common queries
- Real-time validation and submit button states

### ProviderCards
- Visual provider selection with gradient backgrounds
- Real-time status indicators (loading, success, error)
- Model information display

### ResponseDisplay
- Typewriter effect for streaming responses
- Copy to clipboard functionality
- Expand/collapse for long responses
- Special formatting for Google Search results

## Customization

### Theming
Edit `tailwind.config.js` to customize colors:
```javascript
colors: {
  primary: '#000000',
  accent: '#3B82F6',
  background: '#0a0a0a',
  card: '#1a1a1a',
  // Add your custom colors
}
```

### Animations
Modify animation settings in `tailwind.config.js`:
```javascript
animation: {
  'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
  'typing': 'typing 2s steps(20, end)',
  // Add custom animations
}
```

## Development

### Adding New Components
1. Create component in `frontend/src/components/`
2. Import and use in `App.tsx`
3. Add styles using Tailwind classes

### Adding New API Endpoints
1. Add endpoint in `backend/app.py`
2. Update API types in `frontend/src/services/api.ts`
3. Add API call function in `apiService`

### WebSocket Events
1. Add event handler in `backend/app.py`
2. Listen for event in `frontend/src/App.tsx`
3. Update UI state accordingly

## Production Deployment

### Environment Variables
Create `.env.production`:
```env
VITE_API_URL=https://your-api-domain.com
```

### Build for Production
```bash
cd frontend
npm run build
# Outputs to frontend/dist/
```

### Docker Deployment
```bash
docker-compose up --build -d
```

### Nginx Configuration
The included `nginx.conf` handles:
- SPA routing
- API proxy to backend
- WebSocket proxy
- Gzip compression

## Troubleshooting

### Backend Issues
- **Flask not starting**: Check Python version (3.9+) and dependencies
- **API key errors**: Verify `.env` file configuration
- **CORS errors**: Ensure Flask-CORS is installed and configured

### Frontend Issues
- **Blank page**: Check browser console for errors
- **API connection failed**: Verify backend is running on port 5000
- **WebSocket not connecting**: Check proxy configuration in `vite.config.ts`

### Docker Issues
- **Build failures**: Ensure Docker and docker-compose are installed
- **Port conflicts**: Change ports in `docker-compose.yml` if needed
- **Environment variables**: Verify `.env` file is in root directory

## Future Enhancements

- [ ] Comparison view for side-by-side analysis
- [ ] Full AISEO analytics dashboard with charts
- [ ] User authentication and saved queries
- [ ] Batch query processing
- [ ] Response caching and optimization
- [ ] Advanced filtering and search
- [ ] Export to PDF reports
- [ ] API rate limiting and quotas

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.