#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KeyRemover GUI - A macOS application to remove apps and their trial data
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QListWidget, 
                            QLineEdit, QMessageBox, QFileDialog, QProgressBar,
                            QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPixmap

from key_remover import KeyRemover

# Import icon generator if the icon doesn't exist
icon_path = 'resources/icon.png'
if not os.path.exists(icon_path):
    try:
        # Try to import and run the icon generator
        from generate_icon import create_key_remover_icon
        icon_path = create_key_remover_icon()
    except ImportError:
        print("Icon generator not found, using default icon")
        icon_path = None
    except Exception as e:
        print(f"Error generating icon: {e}")
        icon_path = None

class RemoverThread(QThread):
    """Thread to handle app removal in the background"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, app_name):
        super().__init__()
        self.app_name = app_name
        
    def run(self):
        remover = KeyRemover()
        result = remover.remove_application(self.app_name)
        self.finished.emit(result)


class KeyRemoverApp(QMainWindow):
    """Main GUI for the KeyRemover application"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("KeyRemover - App Trial Reset Tool")
        self.setMinimumSize(600, 400)
        
        # Set application icon
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Add logo at the top if we have an icon
        if icon_path and os.path.exists(icon_path):
            logo_label = QLabel()
            pixmap = QPixmap(icon_path)
            logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("KeyRemover")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Remove applications and reset trial periods")
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)
        
        # App selection area
        input_layout = QHBoxLayout()
        
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("Enter application name (e.g., 'Final Cut Pro')")
        input_layout.addWidget(self.app_input)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_app)
        input_layout.addWidget(browse_button)
        
        main_layout.addLayout(input_layout)
        
        # Remove button
        remove_button = QPushButton("Remove Application")
        remove_button.clicked.connect(self.remove_app)
        main_layout.addWidget(remove_button)
        
        # Progress area
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        main_layout.addWidget(self.progress_text)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def browse_app(self):
        """Open file dialog to select an application"""
        app_path, _ = QFileDialog.getOpenFileName(
            self, "Select Application", "/Applications",
            "Applications (*.app);;All Files (*)"
        )
        
        if app_path:
            # Extract the app name from the path
            app_name = os.path.basename(app_path)
            if app_name.endswith('.app'):
                app_name = app_name[:-4]  # Remove .app extension
            self.app_input.setText(app_name)
            
    def add_log(self, message):
        """Add message to the progress text area"""
        self.progress_text.append(message)
        
    def remove_app(self):
        """Start the app removal process"""
        app_name = self.app_input.text().strip()
        
        if not app_name:
            QMessageBox.warning(self, "Warning", "Please enter an application name")
            return
            
        reply = QMessageBox.question(
            self, 
            'Confirm Removal',
            f'Are you sure you want to completely remove "{app_name}" and all associated files?\n\n'
            f'This will delete the application and any trial-related data.',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.statusBar().showMessage(f"Removing {app_name}...")
            self.add_log(f"Starting removal of {app_name}...")
            
            # Create and start the worker thread
            self.worker = RemoverThread(app_name)
            self.worker.finished.connect(self.on_removal_finished)
            self.worker.start()
    
    def on_removal_finished(self, result):
        """Handle the completion of the removal process"""
        self.add_log(result['message'])
        
        if result['success']:
            if result['removed_files']:
                self.add_log("\nRemoved files/directories:")
                for f in result['removed_files']:
                    self.add_log(f"- {f}")
                    
            self.statusBar().showMessage("Removal completed successfully")
            QMessageBox.information(
                self, 
                "Success", 
                f"Successfully removed the application and its trial data.\n\n"
                f"You can now reinstall the application for a fresh trial period."
            )
        else:
            self.statusBar().showMessage("Removal failed")
            QMessageBox.warning(self, "Error", result['message'])


def main():
    """Main entry point for the GUI application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a more modern look
    
    # Set the application icon
    if icon_path and os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = KeyRemoverApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 