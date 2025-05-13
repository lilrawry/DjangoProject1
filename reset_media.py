import os
import django
from django.core.files import File
from django.conf import settings
import requests
from io import BytesIO
import shutil

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject1.settings')
django.setup()

from rooms.models import Room

# Moroccan-themed room images (high-quality images from Pexels)
room_images = {
    'salle_atlas': 'https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg',  # Luxury Moroccan conference room
    'espace_medina': 'https://images.pexels.com/photos/1571468/pexels-photo-1571468.jpeg',  # Traditional Moroccan riad courtyard
    'salle_hassan_ii': 'https://images.pexels.com/photos/1571463/pexels-photo-1571463.jpeg',  # Modern Moroccan executive room
    'cabine_marrakech': 'https://images.pexels.com/photos/1571465/pexels-photo-1571465.jpeg',  # Intimate Moroccan meeting space
    'espace_casablanca': 'https://images.pexels.com/photos/1571467/pexels-photo-1571467.jpeg',  # Contemporary Moroccan business center
    'salle_rabat': 'https://images.pexels.com/photos/1571469/pexels-photo-1571469.jpeg'  # Modern Moroccan meeting room
}

def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def reset_media():
    print("Starting media reset...")
    
    # Path to the media directory
    media_dir = os.path.join(settings.MEDIA_ROOT)
    room_images_dir = os.path.join(media_dir, 'room_images')
    
    # Clear all room image fields in database first
    print("Clearing image fields in database...")
    Room.objects.all().update(image='')
    
    # Create a temporary directory for new images
    temp_dir = os.path.join(media_dir, 'temp_images')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Download and prepare new images
    print("Downloading new images...")
    success = True
    for room in Room.objects.all():
        room_name = room.name.lower().replace(' ', '_')
        if room_name in room_images:
            print(f"Processing {room.name}...")
            image_url = room_images[room_name]
            image_content = download_image(image_url)
            
            if image_content:
                image_name = f"{room_name}.jpg"
                image_path = os.path.join(temp_dir, image_name)
                
                with open(image_path, 'wb') as f:
                    f.write(image_content.getvalue())
                print(f"✓ Downloaded image for: {room.name}")
            else:
                print(f"✗ Failed to download image for: {room.name}")
                success = False
    
    if success:
        # Remove old room_images directory
        if os.path.exists(room_images_dir):
            print("Removing old images...")
            shutil.rmtree(room_images_dir, ignore_errors=True)
        
        # Move new images into place
        print("Installing new images...")
        os.rename(temp_dir, room_images_dir)
        
        # Update database records
        print("Updating database records...")
        for room in Room.objects.all():
            room_name = room.name.lower().replace(' ', '_')
            if room_name in room_images:
                image_name = f"{room_name}.jpg"
                image_path = os.path.join(room_images_dir, image_name)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        room.image.save(image_name, File(f), save=True)
                    print(f"✓ Updated database record for: {room.name}")
        
        print("\nMedia reset completed successfully!")
    else:
        # Clean up temp directory if something went wrong
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        print("\nMedia reset failed. No changes were made to existing files.")

if __name__ == '__main__':
    reset_media() 