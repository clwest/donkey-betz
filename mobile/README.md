# DonkeyOS Cockpit 📱

Mobile cockpit for the DonkeyOS AI Platform - Human-AI Co-Leadership on the go!

**Part of the Unified DonkeyOS Monorepo** 🏢
- Backend (Django): `/`
- Mobile (Flutter): `/mobile/` 👈 You are here
- Documentation: `/docs/`

## Features

- **📊 Donkey Cockpit** - Unified command center home screen surfacing leadership decisions, projects/sessions, and video renders in one place (Session 107) ⭐ NEW!
- **🎬 Video Studio** - Create and monitor DaVinci Resolve render jobs with real-time status updates (Session 105-106)
- **🏢 Project Browser** - Browse projects, sessions, and view all images/videos with full-screen asset viewer (Session 101)
- **👔 Executive Boardroom** - Start meetings with your AI executive team (Session 100)
- **📈 Leadership Dashboard** - Track AI vs Human decisions, overrides, and performance (Session 104)
- **⚙️ Settings & Auth** - Configure API connections with secure credential storage (Session 102)

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
│   ├── cockpit/    # Unified home screen (Session 107)
│   ├── render/     # Video Studio (Sessions 105-106)
│   ├── projects/   # Project Browser (Session 101)
│   ├── settings/   # Settings (Session 102)
│   ├── leadership/ # Leadership Dashboard (Session 104)
│   ├── boardroom/  # Boardroom (Session 100)
│   └── coleadership/
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
- Session 99: Co-Leadership System (AI-Human decision tracking)
- Session 100: Executive Boardroom + Flutter-Ready APIs
- Session 101: Project Browser with Asset Viewing
- Session 102: Auth & Connection Settings with X-API-Key
- Session 103: DaVinci Resolve Render Node Service
- Session 104: Leadership Dashboard (stats and recent decisions)
- Session 105: Render Pipeline Backend (create/poll/list jobs)
- Session 106: Video Studio Frontend (render management)
- Session 107: Donkey Cockpit (unified home screen) ⭐ NEW!

## License

Private - Chris's AI Platform

## Created By

Claude Code + Chris Partnership 🤝
**Latest:** Session 107 - Donkey Cockpit v1 (November 15, 2025)
