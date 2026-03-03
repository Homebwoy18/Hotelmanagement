@echo off
REM Build script for Nona Lodge Hotel Management System
REM Run this file from the project root after installing PyInstaller:
REM   pip install pyinstaller

echo [1/3] Installing dependencies...
pip install pyinstaller pillow tkcalendar

echo [2/3] Building executable...
pyinstaller hotel_management.spec --clean --noconfirm

echo [3/3] Done! Executable is at: dist\NonaLodge\NonaLodge.exe
pause
