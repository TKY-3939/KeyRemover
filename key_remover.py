#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KeyRemover - A tool to completely remove macOS applications and their trial data
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import plistlib
import getpass

class KeyRemover:
    """
    A class to handle the removal of applications and their associated data,
    allowing for clean reinstall of trial applications.
    """
    
    def __init__(self):
        """Initialize the KeyRemover with common directories to check"""
        self.home_dir = Path.home()
        self.applications_dir = Path("/Applications")
        
        # Common directories where apps store data
        self.data_dirs = [
            self.home_dir / "Library" / "Application Support",
            self.home_dir / "Library" / "Preferences",
            self.home_dir / "Library" / "Caches",
            self.home_dir / "Library" / "Logs",
            self.home_dir / "Library" / "Containers",
            self.home_dir / "Library" / "Application Scripts",
            self.home_dir / "Library" / "Saved Application State",
            Path("/Library") / "Application Support",
            Path("/Library") / "Preferences",
            Path("/Library") / "Caches",
        ]
        
        # App Store specific directories
        self.app_store_dirs = [
            Path("/private/var/db/receipts"),
            self.home_dir / "Library" / "Group Containers",
        ]
        
        # Add App Store directories to data_dirs
        self.data_dirs.extend(self.app_store_dirs)
        
        # Password for sudo operations
        self.sudo_password = None
    
    def get_app_info(self, app_path):
        """Get the application bundle identifier from Info.plist"""
        info_plist_path = app_path / "Contents" / "Info.plist"
        
        if not info_plist_path.exists():
            return None
            
        try:
            with open(info_plist_path, 'rb') as f:
                info = plistlib.load(f)
                return {
                    'bundle_id': info.get('CFBundleIdentifier'),
                    'name': info.get('CFBundleName', app_path.stem),
                    'display_name': info.get('CFBundleDisplayName', app_path.stem)
                }
        except Exception as e:
            print(f"Error reading Info.plist: {e}")
            return None
    
    def find_app_path(self, app_name):
        """Find the application path"""
        # Try direct match
        app_path = self.applications_dir / f"{app_name}.app"
        if app_path.exists():
            return app_path
            
        # Try case-insensitive search
        for item in self.applications_dir.glob("*.app"):
            if item.stem.lower() == app_name.lower():
                return item
                
        return None
    
    def run_with_sudo(self, cmd, password=None):
        """Run a command with sudo privileges"""
        if password is None and self.sudo_password is None:
            return None, "No password provided for sudo operation"
        
        password_to_use = password if password is not None else self.sudo_password
        
        # Create a sudo command that reads password from stdin
        sudo_cmd = ["sudo", "-S"] + cmd
        
        try:
            process = subprocess.Popen(
                sudo_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send the password to stdin
            stdout, stderr = process.communicate(input=password_to_use + "\n")
            
            if process.returncode != 0:
                if "incorrect password" in stderr.lower():
                    return None, "Incorrect password"
                return None, f"Command failed: {stderr}"
            
            return stdout, None
        except Exception as e:
            return None, f"Error executing sudo command: {e}"
    
    def is_app_store_app(self, app_info):
        """Check if the application is from the App Store"""
        if not app_info or not app_info.get('bundle_id'):
            return False
            
        bundle_id = app_info.get('bundle_id')
        
        # Check for receipt file which indicates App Store installation
        receipt_path = Path("/private/var/db/receipts") / f"{bundle_id}.plist"
        if receipt_path.exists():
            return True
            
        # Check for App Store metadata in the app bundle
        app_name = app_info.get('name')
        if app_name:
            app_path = self.find_app_path(app_name)
            if app_path and (app_path / "Contents" / "_MASReceipt").exists():
                return True
                
        return False
    
    def remove_app_files(self, app_info, password=None):
        """
        Remove all files associated with the application
        """
        if not app_info:
            return []
            
        bundle_id = app_info.get('bundle_id')
        app_name = app_info.get('name')
        display_name = app_info.get('display_name')
        
        removed_files = []
        
        # Search patterns based on app info
        patterns = [
            f"{bundle_id}*" if bundle_id else None,
            f"{app_name}*" if app_name else None,
            f"{display_name}*" if display_name else None,
            f"com.*.{app_name}*" if app_name else None,
        ]
        patterns = [p for p in patterns if p]
        
        # Check if this is an App Store app
        is_app_store = self.is_app_store_app(app_info)
        
        # Remove files from common directories
        for directory in self.data_dirs:
            if not directory.exists():
                continue
                
            for pattern in patterns:
                for item in directory.glob(pattern):
                    try:
                        # For system directories that need sudo
                        if str(item).startswith(('/Library', '/private')) or is_app_store:
                            if password or self.sudo_password:
                                cmd = ["rm", "-rf", str(item)]
                                output, error = self.run_with_sudo(cmd, password)
                                if error:
                                    print(f"Error removing {item} with sudo: {error}")
                                else:
                                    removed_files.append(f"{item} (sudo)")
                        else:
                            # Regular removal for user directories
                            if item.is_dir():
                                shutil.rmtree(item)
                            else:
                                item.unlink()
                            removed_files.append(str(item))
                    except Exception as e:
                        print(f"Error removing {item}: {e}")
        
        # Run defaults delete if we have a bundle_id
        if bundle_id:
            try:
                # Try without sudo first
                subprocess.run(['defaults', 'delete', bundle_id], 
                               capture_output=True, check=False)
                removed_files.append(f"defaults domain: {bundle_id}")
                
                # If it's an App Store app, also try with sudo
                if is_app_store and (password or self.sudo_password):
                    cmd = ["defaults", "delete", bundle_id]
                    output, error = self.run_with_sudo(cmd, password)
                    if not error:
                        removed_files.append(f"defaults domain (sudo): {bundle_id}")
            except Exception as e:
                print(f"Error deleting defaults for {bundle_id}: {e}")
        
        return removed_files
    
    def remove_application(self, app_name, password=None):
        """
        Main method to remove an application and all its associated data
        """
        # Store the password for future sudo operations
        if password:
            self.sudo_password = password
            
        app_path = self.find_app_path(app_name)
        
        if not app_path:
            return {
                'success': False,
                'message': f"Application '{app_name}' not found in /Applications",
                'removed_files': [],
                'needs_sudo': False
            }
        
        app_info = self.get_app_info(app_path)
        
        # Check if this is an App Store app
        is_app_store = self.is_app_store_app(app_info)
        
        # Remove associated files first
        removed_files = self.remove_app_files(app_info, password)
        
        # Now remove the application itself
        try:
            # For App Store apps or system apps, use sudo
            if is_app_store or not os.access(app_path, os.W_OK):
                if not password and not self.sudo_password:
                    return {
                        'success': False,
                        'message': f"This application requires administrator privileges to remove.",
                        'removed_files': removed_files,
                        'needs_sudo': True
                    }
                
                cmd = ["rm", "-rf", str(app_path)]
                output, error = self.run_with_sudo(cmd, password)
                
                if error:
                    return {
                        'success': False,
                        'message': f"Error removing application with sudo: {error}",
                        'removed_files': removed_files,
                        'needs_sudo': True
                    }
                
                removed_files.append(f"{app_path} (sudo)")
            else:
                # Regular removal for user-installed apps
                shutil.rmtree(app_path)
                removed_files.append(str(app_path))
            
            return {
                'success': True,
                'message': f"Successfully removed {app_name} and its associated files",
                'removed_files': removed_files,
                'needs_sudo': False
            }
        except Exception as e:
            # Check if it's a permission error
            if isinstance(e, PermissionError) or "Permission denied" in str(e):
                return {
                    'success': False,
                    'message': f"Permission denied. This application requires administrator privileges to remove.",
                    'removed_files': removed_files,
                    'needs_sudo': True
                }
            else:
                return {
                    'success': False,
                    'message': f"Error removing application: {e}",
                    'removed_files': removed_files,
                    'needs_sudo': False
                }


def main():
    """Command line interface for KeyRemover"""
    if len(sys.argv) < 2:
        print("Usage: python key_remover.py AppName [--sudo]")
        return
        
    app_name = sys.argv[1]
    remover = KeyRemover()
    
    # Check if sudo is requested
    use_sudo = "--sudo" in sys.argv
    password = None
    
    if use_sudo:
        password = getpass.getpass("Enter administrator password: ")
    
    print(f"Removing {app_name} and all associated files...")
    result = remover.remove_application(app_name, password)
    
    if not result['success'] and result['needs_sudo'] and not use_sudo:
        print("This application requires administrator privileges to remove.")
        use_sudo = input("Do you want to proceed with sudo? (y/n): ").lower() == 'y'
        
        if use_sudo:
            password = getpass.getpass("Enter administrator password: ")
            result = remover.remove_application(app_name, password)
    
    print(result['message'])
    
    if result['success'] and result['removed_files']:
        print("\nRemoved the following files/directories:")
        for f in result['removed_files']:
            print(f"- {f}")


if __name__ == "__main__":
    main() 