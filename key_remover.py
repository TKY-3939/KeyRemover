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
    
    def remove_app_files(self, app_info):
        """
        Remove all files associated with the application
        """
        if not app_info:
            return False
            
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
        
        # Remove files from common directories
        for directory in self.data_dirs:
            if not directory.exists():
                continue
                
            for pattern in patterns:
                for item in directory.glob(pattern):
                    try:
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
                subprocess.run(['defaults', 'delete', bundle_id], 
                               capture_output=True, check=False)
                removed_files.append(f"defaults domain: {bundle_id}")
            except Exception as e:
                print(f"Error deleting defaults for {bundle_id}: {e}")
        
        return removed_files
    
    def remove_application(self, app_name):
        """
        Main method to remove an application and all its associated data
        """
        app_path = self.find_app_path(app_name)
        
        if not app_path:
            return {
                'success': False,
                'message': f"Application '{app_name}' not found in /Applications",
                'removed_files': []
            }
        
        app_info = self.get_app_info(app_path)
        
        # Remove associated files first
        removed_files = self.remove_app_files(app_info)
        
        # Now remove the application itself
        try:
            shutil.rmtree(app_path)
            removed_files.append(str(app_path))
            
            return {
                'success': True,
                'message': f"Successfully removed {app_name} and its associated files",
                'removed_files': removed_files
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error removing application: {e}",
                'removed_files': removed_files
            }


def main():
    """Command line interface for KeyRemover"""
    if len(sys.argv) < 2:
        print("Usage: python key_remover.py AppName")
        return
        
    app_name = sys.argv[1]
    remover = KeyRemover()
    
    print(f"Removing {app_name} and all associated files...")
    result = remover.remove_application(app_name)
    
    print(result['message'])
    
    if result['success'] and result['removed_files']:
        print("\nRemoved the following files/directories:")
        for f in result['removed_files']:
            print(f"- {f}")


if __name__ == "__main__":
    main() 