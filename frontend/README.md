# Unified Donkey Betz - Frontend

This is the React web application for the Unified Donkey Betz platform, built with Vite, React, TypeScript, and Tailwind CSS.

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   Copy the example environment file and update it:
   ```bash
   cp .env.example .env
   ```
   
   Key environment variables:
   ```bash
   VITE_API_URL=http://localhost:8001/api
   VITE_MEDIA_URL=http://localhost:8001
   VITE_WS_URL=ws://localhost:8001
   VITE_DBAO_API_URL=http://localhost:8001/api
   VITE_DBAO_WS_URL=ws://localhost:8001
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173` (Vite default)

## Backend Dependencies

The frontend requires the unified backend to be running:

- **Main API**: `http://localhost:8001/api`
- **WebSocket**: `ws://localhost:8001`
- **Media/Static Files**: `http://localhost:8001`

Start the backend first using the unified project's start script:
```bash
# From the project root
./start_platform.sh
```

## Architecture

### Key Features
- **Content Generation**: AI-powered text, image, and video generation
- **Personal Knowledge**: Document management and semantic search
- **Agent Orchestra**: Multi-agent AI coordination system
- **Sports Analytics**: Betting insights and data analysis
- **Real-time Communication**: WebSocket-based live updates

### Tech Stack
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **WebSockets**: Native WebSocket API with UCWSF framework
- **Icons**: Lucide React

### Project Structure
```
src/
├── components/          # Reusable UI components
├── features/           # Feature-specific components and logic
├── pages/              # Main application pages
├── services/           # API services and configurations
├── store/              # Zustand state stores
├── types/              # TypeScript type definitions
└── assets/             # Static assets
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Configuration

The app uses environment variables for configuration:

- `VITE_API_URL` - Backend API base URL
- `VITE_MEDIA_URL` - Media server base URL
- `VITE_WS_URL` - WebSocket server URL
- `VITE_DBAO_API_URL` - DBAO (Agent Orchestra) API URL
- `VITE_DBAO_WS_URL` - DBAO WebSocket URL
- `VITE_AUTH_TOKEN` - Default authentication token
- `VITE_UCWSF_*` - UCWSF feature flags
- `VITE_DEBUG_MODE` - Enable debug logging

### API Integration

The frontend integrates with multiple backend services:

1. **Main API** (`/api/`) - Core application features
2. **DBAO API** (`/api/`) - Agent Orchestra functionality
3. **WebSocket** - Real-time updates and communication
4. **Media Server** - Static file serving

### WebSocket Features

Uses the UCWSF (Unified CORS WebSocket Framework) for:
- Real-time agent status updates
- Live sports data feeds
- Interactive AI conversations
- System health monitoring

## Production

### Build Process
```bash
npm run build
```

The build artifacts will be in the `dist/` directory, ready for deployment to any static hosting service.

### Deployment Considerations

- Update environment variables for production endpoints
- Configure CORS settings on the backend
- Set up proper SSL certificates for WebSocket connections
- Consider CDN for static assets

## Troubleshooting

### Common Issues

1. **Backend Connection Errors**
   - Ensure the unified backend is running on port 8001
   - Check that CORS is properly configured
   - Verify WebSocket endpoints are accessible

2. **Build Errors**
   - Clear node_modules and reinstall dependencies
   - Check TypeScript configuration
   - Verify all environment variables are set

3. **WebSocket Connection Issues**
   - Check browser console for connection errors
   - Ensure WebSocket URL matches backend configuration
   - Verify UCWSF feature flags are properly set

### Development Tips

- Use browser DevTools to monitor API calls
- Check the Network tab for failed requests
- Monitor WebSocket messages in the Console
- Use React DevTools for component debugging

## Integration with Mobile App

This frontend shares API endpoints with the React Native mobile app located at `../mobile/`. Both applications:

- Connect to the same unified backend
- Use similar authentication mechanisms
- Share common data structures and API contracts
- Support real-time features via WebSockets

For mobile app development, see `../mobile/README.md`.
