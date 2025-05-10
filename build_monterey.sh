#!/bin/bash

# Name of your main Python file (entry point)
MAIN_SCRIPT="scheduler_app_drag_n_drop.py"
APP_NAME="Dance_Scheduler"  # No spaces in .app name!
DISPLAY_NAME="Dance Scheduler"  # Human-readable name
ICON_FILE="app_icon.icns"

# Clean previous builds
echo "🔧 Cleaning previous builds..."
rm -rf build dist __pycache__ *.spec

# Install Monterey-compatible dependencies
echo "📦 Installing Monterey-compatible dependencies..."
pip install pyobjc==9.2 tkinterdnd2==0.3.0  # Downgrade for compatibility

# Build with PyInstaller
echo "🛠️ Building macOS app..."
pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_NAME" \
  --icon "$ICON_FILE" \
  --target-arch x86_64 \
  --osx-bundle-identifier "com.yourname.dancescheduler" \
  --add-binary '/System/Library/Frameworks/Tk.framework/Tk:tk' \
  --add-binary '/System/Library/Frameworks/Tcl.framework/Tcl:tcl' \
  --hidden-import tkinterdnd2 \
  --hidden-import pyobjc \
  --runtime-hook hooks/hook-tkinterdnd2.py \
  "$MAIN_SCRIPT"

# Create hooks directory if missing
mkdir -p hooks
cat > hooks/hook-tkinterdnd2.py <<'EOL'
from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('tkinterdnd2')
EOL

# Fix Info.plist (safer than overwriting)
echo "🖥  Customizing app display..."
plutil -replace CFBundleDisplayName -string "$DISPLAY_NAME" "dist/$APP_NAME.app/Contents/Info.plist"
plutil -replace CFBundleName -string "$DISPLAY_NAME" "dist/$APP_NAME.app/Contents/Info.plist"
plutil -replace LSMinimumSystemVersion -string "10.15" "dist/$APP_NAME.app/Contents/Info.plist"

# Remove macOS quarantine attributes
echo "🔓 Removing quarantine attributes..."
xattr -cr "dist/$APP_NAME.app"

# Ad-hoc sign (works without Developer ID)
echo "📝 Code signing..."
codesign --force --deep --sign - "dist/$APP_NAME.app"

echo "✅ Build successful! App is at: dist/$APP_NAME.app"