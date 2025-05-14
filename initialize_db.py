import os
import django
import sys
import requests
from io import BytesIO
from django.core.files.base import ContentFile

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject1.settings')
django.setup()

from rooms.models import Room

def download_image(url, room, index):
    """Download an image from URL and save it to the room"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Create a unique filename
            filename = f"room_{index}_image.jpg"
            # Save the image to the room
            room.image.save(filename, ContentFile(response.content), save=True)
            print(f"Downloaded image for {room.name}")
            return True
        else:
            print(f"Failed to download image: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

def create_sample_rooms():
    """Create sample rooms if none exist"""
    if Room.objects.count() == 0:
        print("Creating sample rooms...")
        
        # Image URLs for different types of conference rooms
        image_urls = [
            'https://images.unsplash.com/photo-1517502884422-41eaead166d4?q=80&w=1025&auto=format&fit=crop',  # Conference room A
            'https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=80&w=1169&auto=format&fit=crop',  # Meeting room B
            'https://images.unsplash.com/photo-1517502884422-41eaead166d4?q=80&w=1025&auto=format&fit=crop',  # Multipurpose room C
            'https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=1169&auto=format&fit=crop',  # Creative studio D
        ]
        
        # Create sample rooms
        rooms_data = [
            {
                'name': 'Salle de Conférence A',
                'capacity': 20,
                'description': 'Grande salle de conférence avec projecteur et système audio',
                'price_per_hour': 200.00,
                'is_available': True,
                'amenities': ['Projecteur', 'Système audio', 'WiFi', 'Climatisation']
            },
            {
                'name': 'Salle de Réunion B',
                'capacity': 10,
                'description': 'Salle de réunion moderne avec tableau blanc interactif',
                'price_per_hour': 150.00,
                'is_available': True,
                'amenities': ['Tableau blanc', 'WiFi', 'Prises électriques', 'Eau minérale']
            },
            {
                'name': 'Salle Polyvalente C',
                'capacity': 30,
                'description': 'Grande salle polyvalente pour événements et formations',
                'price_per_hour': 300.00,
                'is_available': True,
                'amenities': ['Projecteur', 'Système audio', 'WiFi', 'Climatisation', 'Configuration flexible']
            },
            {
                'name': 'Studio Créatif D',
                'capacity': 8,
                'description': 'Petit studio idéal pour brainstorming et travail créatif',
                'price_per_hour': 100.00,
                'is_available': True,
                'amenities': ['Tableau blanc', 'Fournitures créatives', 'WiFi', 'Machine à café']
            }
        ]
        
        created_rooms = []
        for i, room_data in enumerate(rooms_data):
            # Create the room
            room = Room.objects.create(**room_data)
            created_rooms.append(room)
            print(f"Created room: {room_data['name']}")
            
            # Try to download and attach image
            if i < len(image_urls):
                download_image(image_urls[i], room, i)
        
        print(f"Created {len(created_rooms)} sample rooms")
    else:
        print(f"Skipping room creation, {Room.objects.count()} rooms already exist")

if __name__ == '__main__':
    create_sample_rooms()
