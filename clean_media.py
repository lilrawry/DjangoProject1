import os
import shutil
import django
from django.core.files import File
from django.conf import settings
import requests
from io import BytesIO
import stat
import errno

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject1.settings')
django.setup()

from rooms.models import Room

# Moroccan-themed room images (high-quality images from Pexels)
room_images = {
    'salle_atlas': 'https://images.pexels.com/photos/2079249/pexels-photo-2079249.jpeg',  # Moroccan style meeting room
    'espace_medina': 'https://images.pexels.com/photos/6267516/pexels-photo-6267516.jpeg',  # Traditional Moroccan riad
    'salle_hassan_ii': 'https://images.pexels.com/photos/6585764/pexels-photo-6585764.jpeg',  # Modern Moroccan room
    'cabine_marrakech': 'https://images.pexels.com/photos/6585598/pexels-photo-6585598.jpeg',  # Cozy Moroccan space
    'espace_casablanca': 'https://images.pexels.com/photos/6585755/pexels-photo-6585755.jpeg'  # Contemporary Moroccan design
}

def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        func(path)
    else:
        raise

def clean_media_folder():
    print("Starting media cleanup...")
    
    # Path to the media directory
    media_dir = os.path.join(settings.MEDIA_ROOT)
    room_images_dir = os.path.join(media_dir, 'room_images')
    
    # Remove old room_images directory completely
    if os.path.exists(room_images_dir):
        print("Removing old room_images directory...")
        try:
            # First, try to remove read-only attributes from all files
            for root, dirs, files in os.walk(room_images_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            
            # Then remove the directory
            shutil.rmtree(room_images_dir, onerror=handle_remove_readonly)
        except Exception as e:
            print(f"Error removing directory: {e}")
            return
    
    # Create fresh room_images directory
    print("Creating new room_images directory...")
    os.makedirs(room_images_dir, exist_ok=True)
    
    # Clear room image fields in database
    print("Clearing old image references from database...")
    Room.objects.all().update(image='')
    
    # Update room images
    print("Updating room images...")
    rooms = Room.objects.all()
    for room in rooms:
        room_name = room.name.lower().replace(' ', '_')
        if room_name in room_images:
            print(f"Processing {room.name}...")
            image_url = room_images[room_name]
            image_content = download_image(image_url)
            
            if image_content:
                image_name = f"{room_name}.jpg"
                image_path = os.path.join(room_images_dir, image_name)
                
                # Save the image file
                with open(image_path, 'wb') as f:
                    f.write(image_content.getvalue())
                
                # Update the room's image field
                with open(image_path, 'rb') as f:
                    room.image.save(image_name, File(f), save=True)
                
                print(f"✓ Successfully updated image for: {room.name}")
            else:
                print(f"✗ Failed to download image for: {room.name}")
        else:
            print(f"! No image URL defined for: {room.name}")
    
    print("\nMedia cleanup completed!")

if __name__ == '__main__':
    clean_media_folder() 