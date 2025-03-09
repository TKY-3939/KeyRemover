#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KeyRemover GUI - A macOS application to remove apps and their trial data
Styled with Apple Vision Pro inspired interface with white transparency
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QListWidget, 
                            QLineEdit, QMessageBox, QFileDialog, QProgressBar,
                            QTextEdit, QFrame, QGraphicsDropShadowEffect, QDesktopWidget,
                            QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QRectF
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QPalette, QLinearGradient, QBrush, QPainter, QPainterPath

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

# Corner radius for the main window
WINDOW_CORNER_RADIUS = 15

class PasswordDialog(QDialog):
    """Dialog to request administrator password"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Administrator Password")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(400)
        self.initUI()
        
    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create glass frame
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 70);
                border: 1px solid rgba(255, 255, 255, 80);
                border-radius: 15px;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 3)
        frame.setGraphicsEffect(shadow)
        
        # Frame layout
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Administrator Password Required")
        title_label.setFont(QFont("SF Pro Display", 14, QFont.Bold))
        title_label.setStyleSheet("color: rgba(0, 0, 0, 220);")
        title_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("This application requires administrator privileges to remove.")
        desc_label.setFont(QFont("SF Pro Display", 10))
        desc_label.setStyleSheet("color: rgba(0, 0, 0, 170);")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        frame_layout.addWidget(desc_label)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter administrator password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(30)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid rgba(0, 0, 0, 30);
                border-radius: 0px;
                background-color: rgba(255, 255, 255, 70);
                color: rgba(0, 0, 0, 220);
                padding-left: 12px;
                padding-right: 12px;
                selection-background-color: rgba(0, 0, 0, 10);
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 0, 0, 50);
                background-color: rgba(255, 255, 255, 80);
            }
        """)
        frame_layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(30)
        cancel_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid rgba(0, 0, 0, 30);
                border-radius: 0px;
                background-color: rgba(255, 255, 255, 70);
                color: rgba(0, 0, 0, 220);
                padding-left: 15px;
                padding-right: 15px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 90);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 60);
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("OK")
        ok_btn.setFixedHeight(30)
        ok_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid rgba(0, 0, 0, 30);
                border-radius: 0px;
                background-color: rgba(52, 152, 219, 180);
                color: white;
                padding-left: 15px;
                padding-right: 15px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 220);
            }
            QPushButton:pressed {
                background-color: rgba(52, 152, 219, 150);
            }
        """)
        ok_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        frame_layout.addLayout(button_layout)
        
        # Add frame to main layout
        main_layout.addWidget(frame)
        
        # Set focus to password input
        self.password_input.setFocus()
    
    def getPassword(self):
        """Return the entered password"""
        return self.password_input.text()
    
    def paintEvent(self, event):
        """Custom paint event to create a background blur effect with rounded corners"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create a rounded rectangle path for the window
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), WINDOW_CORNER_RADIUS, WINDOW_CORNER_RADIUS)
        
        # Set the clip path to ensure everything is drawn within the rounded rectangle
        painter.setClipPath(path)
        
        # Draw a semi-transparent white background
        painter.fillRect(self.rect(), QColor(255, 255, 255, 200))


class AvpStyleButton(QPushButton):
    """Button with Apple Vision Pro style"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(30)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("SF Pro Display", 10))
        
        # Apply stylesheet
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid rgba(0, 0, 0, 30);
                border-radius: 0px;
                background-color: rgba(255, 255, 255, 70);
                color: rgba(0, 0, 0, 220);
                padding-left: 15px;
                padding-right: 15px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 90);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 60);
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 1)
        self.setGraphicsEffect(shadow)


class AvpStyleLineEdit(QLineEdit):
    """Text input with Apple Vision Pro style"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setFont(QFont("SF Pro Display", 10))
        
        # Apply stylesheet
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid rgba(0, 0, 0, 30);
                border-radius: 0px;
                background-color: rgba(255, 255, 255, 70);
                color: rgba(0, 0, 0, 220);
                padding-left: 12px;
                padding-right: 12px;
                selection-background-color: rgba(0, 0, 0, 10);
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 0, 0, 50);
                background-color: rgba(255, 255, 255, 80);
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 1)
        self.setGraphicsEffect(shadow)


class AvpStyleTextEdit(QTextEdit):
    """Text display with Apple Vision Pro style"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("SF Pro Display", 10))
        
        # Apply stylesheet
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid rgba(0, 0, 0, 30);
                border-radius: 0px;
                background-color: rgba(255, 255, 255, 70);
                color: rgba(0, 0, 0, 220);
                padding: 12px;
                selection-background-color: rgba(0, 0, 0, 10);
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 1)
        self.setGraphicsEffect(shadow)


class GlassTitleBar(QFrame):
    """Custom title bar with glass morphism style"""
    
    def __init__(self, parent, title="KeyRemover"):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.title = title
        self.initUI()
        
        # Enable mouse tracking for window movement
        self.pressing = False
        self.start_point = None
        
    def initUI(self):
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        
        # Window controls (macOS style)
        control_layout = QHBoxLayout()
        
        # Close button
        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(12, 12)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5f57;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff4b47;
            }
        """)
        self.close_btn.clicked.connect(self.parent.close)
        
        # Minimize button
        self.min_btn = QPushButton()
        self.min_btn.setFixedSize(12, 12)
        self.min_btn.setStyleSheet("""
            QPushButton {
                background-color: #febc2e;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #feb519;
            }
        """)
        self.min_btn.clicked.connect(self.parent.showMinimized)
        
        # Maximize button (green)
        self.max_btn = QPushButton()
        self.max_btn.setFixedSize(12, 12)
        self.max_btn.setStyleSheet("""
            QPushButton {
                background-color: #28c840;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #24b539;
            }
        """)
        
        # Add window controls to layout
        control_layout.addWidget(self.close_btn)
        control_layout.addWidget(self.min_btn)
        control_layout.addWidget(self.max_btn)
        control_layout.addStretch(1)
        
        # Title label
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("SF Pro Display", 11))
        title_label.setStyleSheet("color: rgba(0, 0, 0, 180);")
        
        # Add all elements to main layout
        layout.addLayout(control_layout)
        layout.addWidget(title_label)
        layout.addStretch(1)
        
        # Set frame style
        self.setStyleSheet("""
            GlassTitleBar {
                background-color: rgba(255, 255, 255, 70);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 80);
                border-bottom: none;
            }
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressing = True
            self.start_point = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self.pressing:
            self.parent.move(self.parent.pos() + (event.globalPos() - self.start_point))
            self.start_point = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        self.pressing = False


class GlassFrame(QFrame):
    """Frame with glass morphism effect"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassFrame")
        
        # Apply glass effect with stylesheet
        self.setStyleSheet("""
            #glassFrame {
                background-color: rgba(255, 255, 255, 70);
                border: 1px solid rgba(255, 255, 255, 80);
                border-radius: 0px;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)


class RemoverThread(QThread):
    """Thread to handle app removal in the background"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, app_name, password=None):
        super().__init__()
        self.app_name = app_name
        self.password = password
        
    def run(self):
        remover = KeyRemover()
        result = remover.remove_application(self.app_name, self.password)
        self.finished.emit(result)


class KeyRemoverApp(QMainWindow):
    """Main GUI for the KeyRemover application with Vision Pro styling"""
    
    def __init__(self):
        super().__init__()
        
        # Remove default window frame and make background transparent
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("KeyRemover - App Trial Reset Tool")
        self.resize(600, 500)
        
        # Center the window
        self.center()
        
        # Set application icon
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create a glass outer frame
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)  # Remove spacing between title bar and content
        
        # Create title bar
        self.title_bar = GlassTitleBar(self, "KeyRemover - App Trial Reset Tool")
        
        # Create content frame with glass effect
        content_frame = GlassFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add title bar and content frame to main layout
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(content_frame)
        
        # Add logo at the top if we have an icon
        if icon_path and os.path.exists(icon_path):
            logo_label = QLabel()
            pixmap = QPixmap(icon_path)
            logo_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("KeyRemover")
        title_label.setFont(QFont("SF Pro Display", 22, QFont.Bold))
        title_label.setStyleSheet("color: rgba(0, 0, 0, 220);")
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Remove applications and reset trial periods")
        desc_label.setFont(QFont("SF Pro Display", 12))
        desc_label.setStyleSheet("color: rgba(0, 0, 0, 170);")
        desc_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(desc_label)
        
        # Spacer
        content_layout.addSpacing(5)
        
        # App selection area
        input_frame = QFrame()
        input_frame.setStyleSheet("background: transparent; border: none;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        
        self.app_input = AvpStyleLineEdit()
        self.app_input.setPlaceholderText("Enter application name (e.g., 'Final Cut Pro')")
        input_layout.addWidget(self.app_input, 1)
        
        browse_button = AvpStyleButton("Browse")
        browse_button.setFixedWidth(80)
        browse_button.clicked.connect(self.browse_app)
        input_layout.addWidget(browse_button)
        
        content_layout.addWidget(input_frame)
        
        # Remove button
        remove_button = AvpStyleButton("Remove Application")
        remove_button.setFont(QFont("SF Pro Display", 11, QFont.Medium))
        remove_button.setFixedHeight(36)
        remove_button.clicked.connect(self.remove_app)
        content_layout.addWidget(remove_button)
        
        # Progress area
        content_layout.addSpacing(5)
        progress_label = QLabel("Application Removal Log")
        progress_label.setFont(QFont("SF Pro Display", 11, QFont.Medium))
        progress_label.setStyleSheet("color: rgba(0, 0, 0, 200);")
        content_layout.addWidget(progress_label)
        
        self.progress_text = AvpStyleTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMinimumHeight(150)
        content_layout.addWidget(self.progress_text)
        
        # Status bar with glass effect
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: rgba(255, 255, 255, 70);
                color: rgba(0, 0, 0, 150);
                border-top: 1px solid rgba(255, 255, 255, 80);
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;
                font-family: 'SF Pro Display';
                font-size: 10px;
                padding: 3px 12px;
            }
        """)
        self.statusBar().showMessage("Ready")
        
    def center(self):
        """Center the window on the screen"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
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
            
            # Start removal without password first
            self.start_removal(app_name)
    
    def start_removal(self, app_name, password=None):
        """Start the removal process with optional password"""
        # Create and start the worker thread
        self.worker = RemoverThread(app_name, password)
        self.worker.finished.connect(self.on_removal_finished)
        self.worker.start()
    
    def on_removal_finished(self, result):
        """Handle the completion of the removal process"""
        self.add_log(result['message'])
        
        # Check if sudo is needed
        if not result['success'] and result['needs_sudo']:
            self.add_log("Administrator privileges required. Prompting for password...")
            self.request_password(self.app_input.text().strip())
            return
        
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
    
    def request_password(self, app_name):
        """Show password dialog and retry removal with sudo"""
        dialog = PasswordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            password = dialog.getPassword()
            if password:
                self.add_log("Retrying removal with administrator privileges...")
                self.start_removal(app_name, password)
            else:
                self.add_log("No password provided. Removal aborted.")
                self.statusBar().showMessage("Removal aborted")
        else:
            self.add_log("Password dialog cancelled. Removal aborted.")
            self.statusBar().showMessage("Removal aborted")
    
    def paintEvent(self, event):
        """Custom paint event to create a background blur effect with rounded corners"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create a rounded rectangle path for the window
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), WINDOW_CORNER_RADIUS, WINDOW_CORNER_RADIUS)
        
        # Set the clip path to ensure everything is drawn within the rounded rectangle
        painter.setClipPath(path)
        
        # Draw a semi-transparent white background
        painter.fillRect(self.rect(), QColor(255, 255, 255, 200))
        
        # Draw a subtle border around the window
        painter.setPen(QColor(255, 255, 255, 100))
        painter.drawPath(path)


def main():
    """Main entry point for the GUI application"""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Set app style and font
    app.setStyle('Fusion')
    font_db = app.font()
    font_db.setFamily("SF Pro Display")
    app.setFont(font_db)
    
    # Set the application icon
    if icon_path and os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = KeyRemoverApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 