#!/bin/bash

# Name of your main Python file (entry point)
MAIN_SCRIPT="scheduler_app_drag_n_drop.py"
APP_NAME="Dance Scheduler"
# Path to the icon file (should be in the same directory as this script)
ICON_FILE="app_icon.icns"

# Ensure virtual environment is activated before running this script

echo "🔧 Cleaning previous builds..."
rm -rf build dist "$APP_NAME.spec"

# Install fresh dependencies
echo "📦 Installing Sequoia-optimized dependencies..."
pip install pyobjc==11.0 tkinterdnd2==0.4.3 pillow==10.3.0


echo "📦 Building macOS app with PyInstaller..."
pyinstaller \
    --windowed \
    --icon="$ICON_FILE" \
    --hidden-import=Foundation \
    --hidden-import=tkinterdnd2 \
    --add-data="app_icon.png:." \
    --name "$APP_NAME" \
    --osx-bundle-identifier "com.yourname.dancescheduler" \
    "$MAIN_SCRIPT"

# Add Info.plist customization for better display
echo "🖥  Customizing app display..."
cat > "dist/$APP_NAME.app/Contents/Info.plist" <<EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>Dance Scheduler</string>
    <key>CFBundleName</key>
    <string>Dance Scheduler</string>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIconFile</key>
    <string>app_icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.yourname.dancescheduler</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2023 Your Name. All rights reserved.</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
</dict>
</plist>
EOL

echo "✅ Done. App is at: dist/$APP_NAME.app"