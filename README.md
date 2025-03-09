# KeyRemover

A macOS application to completely remove applications and their trial-related data, allowing users to reset trial periods.

## Overview

KeyRemover helps you completely uninstall macOS applications along with all associated files, preferences, caches, and other data that might be used to track trial usage. After removing an application with KeyRemover, you can reinstall it and enjoy a fresh trial period as if you were using the application for the first time.

## Features

- Remove applications from the Applications folder
- Delete all associated preference files, caches, and settings
- Clean up application data from standard macOS directories
- Remove application entries from system defaults
- Simple GUI interface for easy use
- Command-line interface for advanced users

## Requirements

- macOS 10.13 or higher
- Python 3.6 or higher
- PyQt5 (for the GUI version)

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install PyQt5
```

## Usage

### GUI Application

To use the graphical user interface:

```bash
python key_remover_gui.py
```

1. Enter the name of the application you want to remove (e.g., "Final Cut Pro")
2. Or click the "Browse" button to select an application from your system
3. Click "Remove Application" to start the removal process
4. Review the results in the log area

### Command Line

For command-line usage:

```bash
python key_remover.py AppName
```

For example:

```bash
python key_remover.py "Final Cut Pro"
```

## How It Works

KeyRemover identifies and removes:

1. The application bundle from `/Applications`
2. Application data from common directories:
   - `~/Library/Application Support/`
   - `~/Library/Preferences/`
   - `~/Library/Caches/`
   - `~/Library/Logs/`
   - `~/Library/Containers/`
   - `~/Library/Application Scripts/`
   - `~/Library/Saved Application State/`
   - `/Library/Application Support/`
   - `/Library/Preferences/`
   - `/Library/Caches/`

3. System preferences related to the application using the `defaults` command

## Creating a Standalone Application

You can create a standalone macOS application using PyInstaller:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Create the application:
```bash
pyinstaller --windowed --name KeyRemover key_remover_gui.py
```

3. The standalone application will be created in the `dist/KeyRemover` directory

## Caution

- **Use at your own risk**: This tool deletes files from your system
- Always make backups before removing important applications
- The tool requires administrator privileges to remove some system files
- Some applications may use additional undocumented locations to store trial information

## License

MIT License

## Disclaimer

This tool is provided for educational purposes only. The authors are not responsible for any misuse or any damages caused by using this software. Always respect the license terms of the software you're using. 