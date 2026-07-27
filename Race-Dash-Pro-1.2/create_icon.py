#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

# Создаём красную иконку с буквой R
size = 128
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Красный круг
draw.ellipse([10, 10, size-10, size-10], fill=(200, 0, 0, 255), outline=(255, 50, 50, 255))

# Буква R
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
except:
    font = ImageFont.load_default()

draw.text((size//2 - 35, size//2 - 35), "R", font=font, fill=(255, 255, 255, 255))

img.save("/home/pi/Race-Dash-Pro-1.1/rdp_icon.png")
print("✅ Иконка создана: rdp_icon.png")
