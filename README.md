# Trading Research — Click-to-Run Desktop App

This repository now includes a **consumer-style packaged desktop version** of the trading research system.

## What changed
- No SSH workflow required
- No Docker required
- No manual database setup required
- Backend and UI are bundled for desktop use
- Local SQLite settings storage (for API keys + defaults)

## Desktop packaging architecture
- **Desktop shell:** Electron (`desktop/`)
- **Backend:** FastAPI (`backend/`), launched automatically by Electron on app start
- **UI:** Electron renderer (`desktop/renderer/`) displayed inside the app window
- **Local DB:** SQLite (`backend/app/local_state.db`) for app settings

## Zero-terminal end-user behavior
After packaging and installing:
1. User double-clicks app icon.
2. Electron auto-starts backend on localhost.
3. App opens desktop window with analysis + settings UI.
4. User configures API keys inside the app (no `.env` needed).

## Settings UI (inside app)
Included fields:
- Binance API key / secret
- Oanda API key
- CME API key
- Default market
- Default timeframe
- Default assets list

These are persisted locally in SQLite through:
- `GET /api/settings`
- `PUT /api/settings`

## Build in one command

### Desktop (cross-platform package)
```bash
./scripts/build_desktop.sh
```

### Windows installer (.exe / NSIS)
```bat
scripts\build_windows.bat
```

### macOS DMG (on macOS host)
```bash
cd desktop && npm run dist:mac
```

## Optional mobile wrapper (Capacitor)
A lightweight Android wrapper is included in `mobile-capacitor/`.

### Build Android APK (debug)
```bash
./scripts/build_android.sh
```

APK output:
- `mobile-capacitor/android/app/build/outputs/apk/debug/app-debug.apk`

> For signed production APK/AAB, open Android project and configure release signing.

## Run desktop app in dev mode
```bash
cd desktop
npm install
npm run start
```

## Notes
- App runs offline except for market data API calls.
- Forex/futures connectors still use synthetic fallback data unless real provider integrations are wired.
- PostgreSQL and Docker are no longer required for standalone local usage.
