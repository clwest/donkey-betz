# DonkeyOS Cockpit 📱

Mobile cockpit for the DonkeyOS AI Platform - Human-AI Co-Leadership on the go!

**Part of the Unified DonkeyOS Monorepo** 🏢
- Backend (Django): `/`
- Mobile (Flutter): `/mobile/` 👈 You are here
- Documentation: `/docs/`

## Features

- **Executive Boardroom Meetings** - Start meetings with your AI executive team
- **Co-Leadership Dashboard** - Track decisions, overrides, and outcomes
- **Project Browser** - Browse projects, sessions, and view all images/videos (Session 101) ⭐ NEW!
- **Asset Viewer** - Full-screen image/video viewing with swipe navigation
- **Leadership Stats** - See AI vs Human performance metrics

## Getting Started

### Prerequisites

- Flutter SDK 3.0 or higher
- Dart SDK 3.0 or higher
- DonkeyOS backend running on http://localhost:8000

### Installation

1. Navigate to the mobile directory:
   ```bash
   cd /Users/donkeyking/development/unified-donkey-betz/mobile
   ```

2. Install dependencies:
   ```bash
   flutter pub get
   ```

3. Generate code:
   ```bash
   flutter pub run build_runner build --delete-conflicting-outputs
   ```

4. Configure environment:
   - Copy `.env.example` to `.env`
   - Set `API_BASE_URL` to your backend URL

5. Run the app:
   ```bash
   flutter run
   ```

## Architecture

- **State Management:** Riverpod
- **Networking:** Dio + http
- **Models:** Freezed (immutable data classes)
- **Storage:** SharedPreferences + SecureStorage

## Project Structure

```
lib/
├── core/           # API client, config, theme
├── models/         # Data models
├── providers/      # Riverpod providers
├── services/       # API services
├── features/       # UI screens
│   ├── home/
│   ├── projects/
│   ├── boardroom/
│   ├── coleadership/
│   └── leadership/
├── app.dart        # App configuration
└── main.dart       # Entry point
```

## Development

### Code Generation

Run this after modifying models:
```bash
flutter pub run build_runner watch
```

### Testing

```bash
flutter test
```

## Backend Integration

Integrates with DonkeyOS Django backend:
- Session 99: Co-Leadership System
- Session 100 Part 11: Leadership Dashboard
- Session 100 Part 13: Flutter-Ready APIs
- Session 101: Project Browser with Asset Viewing ⭐ NEW!

## License

Private - Chris's AI Platform

## Created By

Claude Code + Chris Partnership 🤝
Session 100 Part 13 - November 15, 2025
