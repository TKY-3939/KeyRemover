#!/bin/bash

# Build script for KeyRemover macOS app

# Exit on any error
set -e

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Pip is not installed. Please install pip first."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Generate the icon
echo "Generating application icon..."
python3 generate_icon.py

# Check if iconutil is available (macOS specific)
if command -v iconutil &> /dev/null; then
    echo "Creating .icns file with iconutil..."
    iconutil -c icns resources/icon.iconset
    ICON_FLAG="--icon=resources/icon.icns"
else
    echo "iconutil not found, using PNG icon..."
    ICON_FLAG="--window-icon=resources/icon.png"
fi

# Create app using PyInstaller
echo "Building application..."
pyinstaller --windowed \
            --name "KeyRemover" \
            $ICON_FLAG \
            --add-data "README.md:." \
            --add-data "LICENSE:." \
            --add-data "resources:resources" \
            --hidden-import="PyQt5.QtCore" \
            --hidden-import="PyQt5.QtGui" \
            --hidden-import="PyQt5.QtWidgets" \
            key_remover_gui.py

# Move to Applications folder if requested
echo
echo "KeyRemover has been built successfully!"
echo "The application is located at: $(pwd)/dist/KeyRemover/KeyRemover.app"
echo

read -p "Would you like to install KeyRemover to the Applications folder? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing to Applications folder..."
    cp -R "$(pwd)/dist/KeyRemover/KeyRemover.app" "/Applications/"
    echo "KeyRemover has been installed to the Applications folder."
fi

echo
echo "Build complete!" 