#!/bin/bash

# Configuration
APP_NAME="Dance Scheduler"  # No spaces in the app name!
DISPLAY_NAME="Dance Scheduler"
MAIN_SCRIPT="scheduler_app_drag_n_drop.py"
ICON_FILE="app_icon.icns"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist __pycache__ *.spec

# Install dependencies
echo "📦 Installing dependencies..."
pip install pyobjc==11.0 tkinterdnd2==0.4.3 pillow==10.3.0

# Build with PyInstaller
echo "🛠️ Building macOS app..."
pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_NAME" \
  --icon "$ICON_FILE" \
  --target-arch universal2 \
  --osx-bundle-identifier "com.yourname.dancescheduler" \
  --add-data "app_icon.png:." \
  --hidden-import tkinterdnd2 \
  --hidden-import pyobjc \
  "$MAIN_SCRIPT"

# Verify universal binary
echo "🔍 Verifying architecture support..."
lipo -archs "dist/$APP_NAME.app/Contents/MacOS/$APP_NAME"

# Post-build fixes
echo "🔓 Removing security quarantine..."
xattr -cr "dist/$APP_NAME.app"

echo "📝 Applying ad-hoc signature..."
codesign --force --deep --sign - "dist/$APP_NAME.app"

echo "✅ Universal build complete: dist/$APP_NAME.app"