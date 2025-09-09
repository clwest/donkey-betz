# Unified Donkey Betz - Mobile App

This is the React Native mobile application for the Unified Donkey Betz platform, built with Expo, React Native, and TypeScript.

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   The app uses environment variables for configuration. Check the `.env` file:
   ```bash
   EXPO_PUBLIC_API_URL=http://localhost:8001/api
   EXPO_PUBLIC_DONKEY_BETZ_API_URL=http://localhost:8001/api
   EXPO_PUBLIC_WS_URL=ws://localhost:8001
   EXPO_PUBLIC_DBAO_API_URL=http://localhost:8001
   EXPO_PUBLIC_DBAO_WS_URL=ws://localhost:8001
   EXPO_PUBLIC_AUTH_TOKEN=your-auth-token
   ```

3. **Start Development Server**
   ```bash
   npm start
   ```
   
   Then choose your platform:
   - Press `i` for iOS simulator
   - Press `a` for Android emulator
   - Press `w` for web browser
   - Scan QR code with Expo Go app on your device

## Backend Dependencies

The mobile app requires the unified backend to be running:

- **Main API**: `http://localhost:8001/api`
- **WebSocket**: `ws://localhost:8001`
- **Media/Static Files**: `http://localhost:8001`

Start the backend first using the unified project's start script:
```bash
# From the project root
./start_platform.sh
```

## Platform-Specific Setup

### iOS Development
1. **Requirements**:
   - macOS with Xcode installed
   - iOS Simulator or physical iOS device
   - Expo Development Build (for advanced features)

2. **Run on iOS**:
   ```bash
   npm run ios
   ```

### Android Development
1. **Requirements**:
   - Android Studio with Android SDK
   - Android emulator or physical Android device
   - Enable Developer Options and USB Debugging on device

2. **Run on Android**:
   ```bash
   npm run android
   ```

### Web Development
```bash
npm run web
```
The app will be available at `http://localhost:8081`

## Architecture

### Key Features
- **Content Generation**: AI-powered text, image, and video creation
- **Personal Knowledge**: Document management with semantic search
- **Agent Orchestra**: Multi-agent AI coordination system
- **Sports Analytics**: Real-time betting insights and data
- **Real-time Communication**: WebSocket-based live updates
- **Cross-Platform**: iOS, Android, and Web support

### Tech Stack
- **Framework**: React Native with Expo SDK
- **Language**: TypeScript
- **Navigation**: React Navigation 7
- **State Management**: Zustand
- **HTTP Client**: Axios
- **WebSockets**: Native WebSocket API
- **UI Components**: Custom components with React Native primitives
- **Animation**: React Native Reanimated & Skia

### Project Structure
```
src/
├── components/         # Reusable UI components
├── screens/           # Application screens
├── navigation/        # Navigation configuration
├── services/          # API services and configurations
├── store/            # Zustand state stores
├── types/            # TypeScript type definitions
├── utils/            # Utility functions
└── config/           # App configuration files
```

## Development

### Available Scripts

- `npm start` - Start Expo development server
- `npm run ios` - Run on iOS simulator/device
- `npm run android` - Run on Android emulator/device  
- `npm run web` - Run in web browser

### Environment Configuration

The app uses Expo's environment variable system:

- `EXPO_PUBLIC_API_URL` - Backend API base URL
- `EXPO_PUBLIC_DONKEY_BETZ_API_URL` - Main API URL (same as above)
- `EXPO_PUBLIC_WS_URL` - WebSocket server URL
- `EXPO_PUBLIC_DBAO_API_URL` - DBAO (Agent Orchestra) API URL
- `EXPO_PUBLIC_DBAO_WS_URL` - DBAO WebSocket URL
- `EXPO_PUBLIC_AUTH_TOKEN` - Default authentication token

### API Integration

The mobile app integrates with the same backend services as the web app:

1. **Main API** (`/api/`) - Core application features
2. **DBAO API** (`/api/`) - Agent Orchestra functionality  
3. **WebSocket** - Real-time updates and communication
4. **Media Server** - Static file serving

### Device-Specific Configuration

The app automatically adjusts API endpoints based on the platform:

- **iOS Simulator**: `http://localhost:8001/api`
- **Android Emulator**: `http://10.0.2.2:8001/api` 
- **Physical Device**: Use your computer's IP address
- **Web**: `http://localhost:8001/api`

## Building for Production

### Development Build
```bash
# Install EAS CLI
npm install -g @expo/eas-cli

# Configure EAS
eas build:configure

# Build for development
eas build --profile development
```

### Production Build
```bash
# Build for app stores
eas build --profile production

# Submit to app stores
eas submit --platform ios
eas submit --platform android
```

## Debugging

### Common Development Tools
- **Expo DevTools**: Access via browser when development server is running
- **React Native Debugger**: For Redux/state inspection
- **Flipper**: For iOS/Android native debugging
- **Reactotron**: For React Native specific debugging

### Common Issues

1. **Metro Bundler Issues**
   ```bash
   # Clear Metro cache
   npx expo start --clear
   ```

2. **iOS Build Issues**
   ```bash
   # Clean iOS build
   cd ios && xcodebuild clean
   ```

3. **Android Build Issues**
   ```bash
   # Clean Android build
   cd android && ./gradlew clean
   ```

4. **Network Connection Issues**
   - Ensure your device/emulator can reach `localhost:8001`
   - For physical devices, use your computer's IP address
   - Check firewall settings

### Network Configuration for Physical Devices

When testing on a physical device, update the API URLs in `.env`:

```bash
# Replace localhost with your computer's IP address
EXPO_PUBLIC_API_URL=http://192.168.1.100:8001/api
EXPO_PUBLIC_WS_URL=ws://192.168.1.100:8001
```

You can find your IP address with:
```bash
# macOS/Linux
ifconfig | grep inet

# Windows
ipconfig
```

## WebSocket Features

The mobile app includes real-time features via WebSockets:

- **Agent Status Updates**: Live agent orchestration monitoring
- **Sports Data Feeds**: Real-time betting odds and game updates  
- **AI Conversations**: Interactive chat with AI agents
- **System Health**: Backend service status monitoring

## Integration with Web App

This mobile app shares API endpoints and functionality with the React web app located at `../frontend/`. Both applications:

- Connect to the same unified backend
- Use identical authentication mechanisms
- Share common data structures and API contracts
- Support the same real-time WebSocket features
- Provide cross-platform user experiences

For web app development, see `../frontend/README.md`.

## Troubleshooting

### Development Server Won't Start
1. Clear Expo cache: `npx expo start --clear`
2. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
3. Restart Metro bundler: `npx expo start --reset-cache`

### Can't Connect to Backend
1. Verify backend is running on port 8001
2. Check IP address configuration for physical devices
3. Ensure firewall allows connections on port 8001
4. Test API endpoints with browser or curl

### Build Failures
1. Update Expo SDK: `npx expo install --fix`
2. Check for incompatible dependencies
3. Review build logs in EAS dashboard
4. Ensure all required certificates are configured

For additional help, check the [Expo documentation](https://docs.expo.dev/) and [React Native documentation](https://reactnative.dev/docs/getting-started).