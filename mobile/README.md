# DonkeyBetz Mobile

Expo React Native app for the Donkey Betz platform.

## Setup

```bash
cd mobile
npm install
cp .env.example .env.local   # edit API URL if needed
npx expo start
```

## Build

```bash
# Development (simulator)
eas build --profile development

# Preview (internal distribution)
eas build --profile preview

# Production
eas build --profile production
```

## Deep Links

Scheme: `donkeybetz://`

| Link | Screen |
|------|--------|
| `donkeybetz://dashboard` | Dashboard |
| `donkeybetz://boardroom` | Boardroom Home |
| `donkeybetz://boardroom/attention/:id` | Attention Detail |
| `donkeybetz://boardroom/decision/:id` | Decision Detail |
| `donkeybetz://governance` | Governance Home |
| `donkeybetz://governance/classification/:id` | Classification Detail |

## Architecture

- **Auth:** DRF TokenAuth via `expo-secure-store` (see `docs/mobile/WEB_API_CONTRACTS.md`)
- **Navigation:** Manifest-driven from `GET /api/app/manifest/`
- **Chat:** Async PA chat with polling (`POST /api/pa/chat/` -> poll status)
- **State:** Zustand stores
