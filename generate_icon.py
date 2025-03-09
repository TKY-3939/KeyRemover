#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate an icon for the KeyRemover application
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_key_remover_icon():
    """Create a simple icon for the KeyRemover application"""
    # Create a 1024x1024 image with a transparent background
    icon_size = 1024
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Define colors
    primary_color = (52, 152, 219)  # Blue
    secondary_color = (231, 76, 60)  # Red
    highlight_color = (255, 255, 255)  # White
    
    # Draw a circular background
    circle_radius = icon_size * 0.45
    circle_center = (icon_size // 2, icon_size // 2)
    draw.ellipse(
        (
            circle_center[0] - circle_radius,
            circle_center[1] - circle_radius,
            circle_center[0] + circle_radius,
            circle_center[1] + circle_radius
        ),
        fill=primary_color
    )
    
    # Draw a key shape
    key_width = icon_size * 0.5
    key_height = icon_size * 0.25
    key_top = icon_size // 2 - key_height // 2
    key_left = icon_size // 2 - key_width // 2
    
    # Key head (circle)
    head_radius = key_height * 0.4
    head_center = (key_left + head_radius, icon_size // 2)
    draw.ellipse(
        (
            head_center[0] - head_radius,
            head_center[1] - head_radius,
            head_center[0] + head_radius,
            head_center[1] + head_radius
        ),
        fill=highlight_color
    )
    
    # Key shaft
    shaft_width = key_width - head_radius * 2
    shaft_height = key_height * 0.4
    shaft_top = icon_size // 2 - shaft_height // 2
    shaft_left = head_center[0] + head_radius
    draw.rectangle(
        (
            shaft_left,
            shaft_top,
            shaft_left + shaft_width,
            shaft_top + shaft_height
        ),
        fill=highlight_color
    )
    
    # Key teeth
    teeth_height = shaft_height * 1.5
    teeth_width = shaft_width * 0.15
    teeth_gap = shaft_width * 0.10
    teeth_top = shaft_top - (teeth_height - shaft_height) // 2
    
    for i in range(3):
        teeth_left = shaft_left + teeth_gap + i * (teeth_width + teeth_gap)
        draw.rectangle(
            (
                teeth_left,
                teeth_top,
                teeth_left + teeth_width,
                teeth_top + teeth_height
            ),
            fill=highlight_color
        )
    
    # Add a red "X" over the key
    x_size = circle_radius * 1.4
    x_width = x_size * 0.15
    x_center = circle_center
    
    # Draw the "X" as two lines
    for angle in [45, -45]:
        draw.line(
            [
                (
                    x_center[0] - x_size * 0.5 * 0.7071,
                    x_center[1] - x_size * 0.5 * 0.7071 * (-1 if angle < 0 else 1)
                ),
                (
                    x_center[0] + x_size * 0.5 * 0.7071,
                    x_center[1] + x_size * 0.5 * 0.7071 * (-1 if angle < 0 else 1)
                )
            ],
            fill=secondary_color,
            width=int(x_width)
        )
    
    # Create the resources directory if it doesn't exist
    if not os.path.exists('resources'):
        os.makedirs('resources')
    
    # Save as PNG
    icon.save('resources/icon.png')
    
    # Save in multiple sizes for macOS icon set
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for size in sizes:
        resized_icon = icon.resize((size, size), Image.LANCZOS)
        if not os.path.exists(f'resources/icon.iconset'):
            os.makedirs(f'resources/icon.iconset')
        resized_icon.save(f'resources/icon.iconset/icon_{size}x{size}.png')
    
    print("Icons generated in resources/ directory")
    print("To create a macOS .icns file, run:")
    print("iconutil -c icns resources/icon.iconset")
    
    return 'resources/icon.png'

if __name__ == '__main__':
    try:
        icon_path = create_key_remover_icon()
        print(f"Icon created successfully at {icon_path}")
    except Exception as e:
        print(f"Error creating icon: {e}")
        print("Please make sure you have Pillow installed: pip install Pillow") 