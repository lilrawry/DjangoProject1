import os
import cairosvg
from PIL import Image
from io import BytesIO

# Chemin vers les fichiers
base_dir = os.path.dirname(os.path.abspath(__file__))
svg_path = os.path.join(base_dir, 'static', 'img', 'easyroom-logo.svg')
png_path = os.path.join(base_dir, 'static', 'img', 'easyroom-logo.png')
small_svg_path = os.path.join(base_dir, 'static', 'img', 'easyroom-logo-small.svg')
small_png_path = os.path.join(base_dir, 'static', 'img', 'easyroom-logo-small.png')

# Conversion du logo principal
try:
    print(f"Conversion de {svg_path} vers {png_path}")
    png_data = cairosvg.svg2png(url=svg_path, output_width=400, output_height=400)
    with open(png_path, 'wb') as f:
        f.write(png_data)
    print(f"Logo principal converti avec succès!")
except Exception as e:
    print(f"Erreur lors de la conversion du logo principal: {e}")

# Conversion du petit logo
try:
    print(f"Conversion de {small_svg_path} vers {small_png_path}")
    png_data = cairosvg.svg2png(url=small_svg_path, output_width=200, output_height=200)
    with open(small_png_path, 'wb') as f:
        f.write(png_data)
    print(f"Petit logo converti avec succès!")
except Exception as e:
    print(f"Erreur lors de la conversion du petit logo: {e}")

print("Conversion terminée!")
