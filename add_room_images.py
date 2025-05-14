import os
import sys
import django
import requests
from io import BytesIO
from django.core.files.base import ContentFile

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject1.settings')
django.setup()

from rooms.models import Room

# Image URLs for different types of conference rooms
image_urls = [
    'https://images.unsplash.com/photo-1517502884422-41eaead166d4?q=80&w=1025&auto=format&fit=crop',  # Conference room A
    'https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=80&w=1169&auto=format&fit=crop',  # Meeting room B
    'https://images.unsplash.com/photo-1517502884422-41eaead166d4?q=80&w=1025&auto=format&fit=crop',  # Multipurpose room C
    'https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=1169&auto=format&fit=crop',  # Creative studio D
]

# Function to download and save image
def download_and_save_image(url, room, index):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Create a unique filename
            filename = f"room_{room.id}_image_{index}.jpg"
            
            # Save the image to the room
            room.image.save(filename, ContentFile(response.content), save=True)
            print(f"Successfully added image to {room.name}")
            return True
        else:
            print(f"Failed to download image: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

# Main function to add images to rooms
def add_images_to_rooms():
    rooms = Room.objects.all()
    
    if not rooms:
        print("No rooms found in the database.")
        return
    
    print(f"Found {rooms.count()} rooms. Adding images...")
    
    for i, room in enumerate(rooms):
        # Use modulo to cycle through available images if we have more rooms than images
        image_url = image_urls[i % len(image_urls)]
        download_and_save_image(image_url, room, i)

if __name__ == "__main__":
    add_images_to_rooms()
    print("Image addition process completed.")
