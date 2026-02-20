@echo off
setlocal
cd /d %~dp0\..\desktop
call npm install
call npm run dist:win
