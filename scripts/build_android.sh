#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../mobile-capacitor"

npm install
npm run build:web
if [ ! -d android ]; then
  npm run cap:add
fi
npm run cap:sync
npm run apk:debug

echo "APK output: mobile-capacitor/android/app/build/outputs/apk/debug/app-debug.apk"
