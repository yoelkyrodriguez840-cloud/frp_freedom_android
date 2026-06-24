#!/usr/bin/env python3
"""
FRP Freedom Android - Generador de Assets
Crea todos los archivos de recursos necesarios para la aplicación
"""

import os
import sys
from pathlib import Path
import base64
from PIL import Image, ImageDraw, ImageFont
import io

# Colores de la aplicación
COLORS = {
    'primary': (33, 150, 243),      # #2196F3
    'primary_dark': (25, 118, 210), # #1976D2
    'primary_light': (187, 222, 251), # #BBDEFB
    'accent': (0, 188, 212),        # #00BCD4
    'success': (76, 175, 80),       # #4CAF50
    'warning': (255, 152, 0),       # #FF9800
    'error': (244, 67, 54),         # #F44336
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'dark_gray': (33, 33, 33),
    'gray': (158, 158, 158),
}

def create_directory_structure():
    """Crear estructura de directorios para assets"""
    dirs = [
        'assets',
        'assets/icons',
        'assets/splash',
        'assets/images',
        'assets/sounds',
        'assets/fonts',
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio creado: {d}")
    
    return Path('assets')

def create_app_icon(size: int, output_path: Path):
    """Crear ícono de la aplicación"""
    # Crear imagen con fondo circular
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fondo circular
    margin = size // 10
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=COLORS['primary']
    )
    
    # "F" en el centro
    try:
        # Intentar usar una fuente del sistema
        font_size = size // 2
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
    except:
        # Fallback a fuente por defecto
        font = ImageFont.load_default()
    
    # Calcular posición del texto
    text = "F"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - 5
    
    # Dibujar texto
    draw.text((text_x, text_y), text, fill=COLORS['white'], font=font)
    
    # Guardar
    img.save(output_path)
    print(f"✅ Ícono creado: {output_path}")
    return img

def create_app_icon_rounded(size: int, output_path: Path):
    """Crear ícono redondeado de la aplicación"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fondo redondeado
    radius = size // 5
    draw.rounded_rectangle(
        [0, 0, size, size],
        radius=radius,
        fill=COLORS['primary'],
        outline=None
    )
    
    # Sombra
    shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [0, 0, size, size],
        radius=radius,
        fill=(0, 0, 0, 30)
    )
    
    # "FRP" en el centro
    try:
        font_size = size // 6
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "FRP"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2
    
    draw.text((text_x, text_y), text, fill=COLORS['white'], font=font)
    
    # Guardar
    img.save(output_path)
    print(f"✅ Ícono redondeado creado: {output_path}")
    return img

def create_splash_screen(width: int, height: int, output_path: Path):
    """Crear pantalla de splash"""
    img = Image.new('RGB', (width, height), COLORS['primary'])
    draw = ImageDraw.Draw(img)
    
    # Gradiente simple
    for i in range(height):
        ratio = i / height
        r = int(COLORS['primary'][0] * (1 - ratio * 0.3))
        g = int(COLORS['primary'][1] * (1 - ratio * 0.3))
        b = int(COLORS['primary'][2] * (1 - ratio * 0.3))
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # Logo
    logo_size = min(width, height) // 4
    logo_margin = logo_size // 2
    draw.ellipse(
        [logo_margin, logo_margin, logo_margin + logo_size, logo_margin + logo_size],
        fill=COLORS['white']
    )
    
    # Texto
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", height // 12)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", height // 18)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
    
    # Título
    title = "FRP Freedom"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = bbox[2] - bbox[0]
    title_x = (width - title_width) // 2
    title_y = logo_margin + logo_size + (height // 20)
    draw.text((title_x, title_y), title, fill=COLORS['white'], font=font_title)
    
    # Subtítulo
    subtitle = "Android FRP Bypass Tool"
    bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_width = bbox[2] - bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + (height // 15)
    draw.text((subtitle_x, subtitle_y), subtitle, fill=COLORS['white'], font=font_subtitle)
    
    # Versión
    version = "v1.0.0"
    bbox = draw.textbbox((0, 0), version, font=font_subtitle)
    version_width = bbox[2] - bbox[0]
    version_x = (width - version_width) // 2
    version_y = height - (height // 15)
    draw.text((version_x, version_y), version, fill=COLORS['white'], font=font_subtitle)
    
    # Guardar
    img.save(output_path)
    print(f"✅ Splash screen creada: {output_path}")
    return img

def create_feature_icons(assets_dir: Path):
    """Crear íconos para características"""
    icons = {
        'device': '📱',
        'security': '🔒',
        'brain': '🧠',
        'history': '📊',
        'settings': '⚙️',
        'help': '❓',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
    }
    
    icon_dir = assets_dir / 'icons'
    
    for name, symbol in icons.items():
        # Crear imagen PNG del emoji
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), symbol, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2
        
        draw.text((text_x, text_y), symbol, fill=(0, 0, 0, 200), font=font)
        img.save(icon_dir / f'{name}.png')
        print(f"✅ Ícono creado: {icon_dir / f'{name}.png'}")

def create_social_images(assets_dir: Path):
    """Crear imágenes para redes sociales"""
    sizes = {
        'og_image': (1200, 630),
        'twitter_card': (1200, 600),
        'banner': (1500, 500),
    }
    
    for name, (width, height) in sizes.items():
        img = Image.new('RGB', (width, height), COLORS['primary'])
        draw = ImageDraw.Draw(img)
        
        # Gradiente
        for i in range(height):
            ratio = i / height
            r = int(COLORS['primary'][0] * (1 - ratio * 0.2))
            g = int(COLORS['primary'][1] * (1 - ratio * 0.2))
            b = int(COLORS['primary'][2] * (1 - ratio * 0.2))
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Logo
        logo_size = min(width, height) // 3
        logo_margin = min(width, height) // 8
        draw.ellipse(
            [logo_margin, logo_margin, logo_margin + logo_size, logo_margin + logo_size],
            fill=COLORS['white']
        )
        
        # Texto
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", height // 8)
            font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", height // 14)
        except:
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
        
        # Título
        title = "FRP Freedom"
        bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = bbox[2] - bbox[0]
        title_x = (width - title_width) // 2
        title_y = height // 2 - height // 10
        
        # Fondo para el texto
        text_padding = 20
        text_bg = (0, 0, 0, 100)
        text_box = [
            title_x - text_padding,
            title_y - text_padding,
            title_x + title_width + text_padding,
            title_y + text_padding + 10
        ]
        draw.rectangle(text_box, fill=text_bg)
        
        draw.text((title_x, title_y), title, fill=COLORS['white'], font=font_title)
        
        # Subtítulo
        subtitle = "Android FRP Bypass Tool"
        bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
        subtitle_width = bbox[2] - bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + height // 10 + 10
        draw.text((subtitle_x, subtitle_y), subtitle, fill=COLORS['white'], font=font_subtitle)
        
        # Guardar
        img_dir = assets_dir / 'images'
        img_dir.mkdir(exist_ok=True)
        img.save(img_dir / f'{name}.png')
        print(f"✅ Imagen social creada: {img_dir / f'{name}.png'}")

def create_readme_icons(assets_dir: Path):
    """Crear íconos para el README"""
    icons = {
        'logo_512': (512, 512),
        'logo_256': (256, 256),
        'logo_128': (128, 128),
        'logo_64': (64, 64),
    }
    
    for name, (size_x, size_y) in icons.items():
        img = Image.new('RGBA', (size_x, size_y), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        margin = size_x // 10
        draw.ellipse(
            [margin, margin, size_x - margin, size_y - margin],
            fill=COLORS['primary']
        )
        
        try:
            font_size = size_x // 2
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = "F"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size_x - text_width) // 2
        text_y = (size_y - text_height) // 2 - 5
        
        draw.text((text_x, text_y), text, fill=COLORS['white'], font=font)
        
        img_dir = assets_dir / 'images'
        img_dir.mkdir(exist_ok=True)
        img.save(img_dir / f'{name}.png')
        print(f"✅ Logo README creado: {img_dir / f'{name}.png'}")

def create_empty_files(assets_dir: Path):
    """Crear archivos vacíos necesarios"""
    # Favicon
    favicon_path = assets_dir / 'favicon.ico'
    if not favicon_path.exists():
        # Crear un favicon simple
        img = Image.new('RGB', (32, 32), COLORS['primary'])
        draw = ImageDraw.Draw(img)
        draw.text((8, 2), "F", fill=COLORS['white'])
        img.save(favicon_path)
        print(f"✅ Favicon creado: {favicon_path}")
    
    # Archivos de audio vacíos
    sounds_dir = assets_dir / 'sounds'
    for sound in ['click.wav', 'success.wav', 'error.wav']:
        sound_path = sounds_dir / sound
        if not sound_path.exists():
            sound_path.touch()
            print(f"✅ Archivo de sonido creado: {sound_path}")

def create_fonts(assets_dir: Path):
    """Crear archivos de fuentes"""
    fonts_dir = assets_dir / 'fonts'
    
    # Crear un archivo de fuente simple (placeholder)
    font_info = """
    FRP Freedom Fonts
    ==================
    
    Fuentes recomendadas:
    - Roboto (para Android)
    - Material Icons
    - Font Awesome
    
    Para usar fuentes personalizadas, coloca los archivos .ttf aquí.
    """
    
    readme_path = fonts_dir / 'README.txt'
    with open(readme_path, 'w') as f:
        f.write(font_info)
    print(f"✅ Archivo de fuentes creado: {readme_path}")

def generate_android_assets(assets_dir: Path):
    """Generar assets específicos para Android"""
    android_dir = assets_dir / 'android'
    android_dir.mkdir(exist_ok=True)
    
    # Tamaños de íconos para Android
    android_sizes = {
        'mdpi': 48,
        'hdpi': 72,
        'xhdpi': 96,
        'xxhdpi': 144,
        'xxxhdpi': 192,
    }
    
    for density, size in android_sizes.items():
        icon_path = android_dir / f'ic_launcher_{density}.png'
        create_app_icon(size, icon_path)
    
    # Round icon
    for density, size in android_sizes.items():
        icon_path = android_dir / f'ic_launcher_round_{density}.png'
        create_app_icon_rounded(size, icon_path)
    
    # Splash screen para Android
    splash_path = android_dir / 'splash.png'
    create_splash_screen(1080, 1920, splash_path)

def main():
    """Función principal"""
    print("=" * 60)
    print("FRP Freedom Android - Generador de Assets")
    print("=" * 60)
    print()
    
    # Crear estructura
    assets_dir = create_directory_structure()
    
    # Generar assets
    print("\n🔧 Generando assets...")
    create_app_icon(512, assets_dir / 'icon.png')
    create_app_icon_rounded(512, assets_dir / 'icon_rounded.png')
    
    # Splash screens
    create_splash_screen(1080, 1920, assets_dir / 'splash.png')
    create_splash_screen(800, 600, assets_dir / 'splash_small.png')
    
    # Íconos para características
    create_feature_icons(assets_dir)
    
    # Imágenes para redes sociales
    create_social_images(assets_dir)
    
    # Íconos para README
    create_readme_icons(assets_dir)
    
    # Archivos vacíos
    create_empty_files(assets_dir)
    
    # Fuentes
    create_fonts(assets_dir)
    
    # Assets para Android
    generate_android_assets(assets_dir)
    
    print("\n" + "=" * 60)
    print("✅ Todos los assets han sido generados exitosamente!")
    print(f"📁 Ubicación: {assets_dir.absolute()}")
    print("=" * 60)
    
    # Mostrar resumen
    print("\n📊 Resumen de assets:")
    for root, dirs, files in os.walk(assets_dir):
        level = root.replace(str(assets_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = Path(root) / file
            size = file_path.stat().st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            print(f"{sub_indent}{file} ({size_str})")

if __name__ == "__main__":
    main()
