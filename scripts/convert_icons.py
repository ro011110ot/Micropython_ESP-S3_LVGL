#!/usr/bin/env python3
"""
Konvertiert OpenWeatherMap RGBA-PNGs zu RGB-PNGs für LVGL.
Transparenz wird auf schwarzen Hintergrund (0x0A0E27) geflattened.

Verwendung:
  python3 convert_icons.py /pfad/zu/icons_png/

Ausgabe: Überschreibt die originalen Dateien mit RGB-Versionen.
"""

import sys
import os
from PIL import Image

# Hintergrundfarbe passend zum Display-Design
BG_COLOR = (10, 14, 39)  # 0x0A0E27


def convert_rgba_to_rgb(input_path, output_path, bg_color=BG_COLOR):
    img = Image.open(input_path)

    if img.mode == "RGBA":
        # Neues RGB-Bild mit Hintergrundfarbe erstellen
        background = Image.new("RGB", img.size, bg_color)
        # RGBA über den Hintergrund legen (Alpha-Compositing)
        background.paste(img, mask=img.split()[3])
        background.save(output_path, "PNG", optimize=False)
        return True
    elif img.mode == "RGB":
        # Bereits RGB - nur kopieren falls nötig
        if input_path != output_path:
            img.save(output_path, "PNG", optimize=False)
        return False
    else:
        # Anderes Format - zu RGB konvertieren
        img.convert("RGB").save(output_path, "PNG", optimize=False)
        return True


def main():
    if len(sys.argv) < 2:
        print("Verwendung: python3 convert_icons.py /pfad/zu/icons_png/")
        print("Beispiel:   python3 convert_icons.py ./icons_png/")
        sys.exit(1)

    folder = sys.argv[1]

    if not os.path.isdir(folder):
        print(f"Fehler: Ordner '{folder}' nicht gefunden!")
        sys.exit(1)

    png_files = [f for f in os.listdir(folder) if f.endswith(".png")]

    if not png_files:
        print(f"Keine PNG-Dateien in '{folder}' gefunden!")
        sys.exit(1)

    print(f"Konvertiere {len(png_files)} PNG-Dateien in '{folder}'...")
    converted = 0

    for filename in sorted(png_files):
        path = os.path.join(folder, filename)
        was_converted = convert_rgba_to_rgb(path, path)
        status = "RGBA→RGB" if was_converted else "bereits RGB"
        print(f"  {filename}: {status}")
        if was_converted:
            converted += 1

    print(f"\nFertig! {converted}/{len(png_files)} Dateien konvertiert.")
    print("Jetzt die konvertierten PNGs auf den ESP32 hochladen.")


if __name__ == "__main__":
    main()
