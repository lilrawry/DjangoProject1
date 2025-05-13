import os
import django
from django.core.files import File
from django.conf import settings
import requests
from io import BytesIO

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject1.settings')
django.setup()

from rooms.models import Room

# Sample room data with Moroccan theme
rooms_data = [
    {
        'name': 'Salle Atlas',
        'description': 'Une salle de réunion élégante avec une vue imprenable sur la ville. Décoration inspirée de l\'architecture marocaine traditionnelle, idéale pour les réunions d\'affaires importantes.',
        'capacity': 12,
        'price_per_hour': 800,
        'image_url': 'https://images.unsplash.com/photo-1517502166878-35c93a0072f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'is_available': True,
        'amenities': ['Wi-Fi', 'Écran 65"', 'Système audio', 'Table de conférence', 'Thé à la menthe']
    },
    {
        'name': 'Espace Medina',
        'description': 'Un espace créatif inspiré des riads marocains, avec une cour intérieure et une décoration traditionnelle. Parfait pour les sessions de brainstorming et les ateliers créatifs.',
        'capacity': 8,
        'price_per_hour': 600,
        'image_url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'is_available': True,
        'amenities': ['Wi-Fi', 'Tableaux blancs', 'Espace de détente', 'Thé à la menthe', 'Pâtisseries marocaines']
    },
    {
        'name': 'Salle Hassan II',
        'description': 'Une salle spacieuse et moderne, nommée en l\'honneur du roi Hassan II. Équipée des dernières technologies pour les formations et les présentations professionnelles.',
        'capacity': 20,
        'price_per_hour': 1000,
        'image_url': 'https://images.unsplash.com/photo-1517502166878-35c93a0072f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'is_available': True,
        'amenities': ['Wi-Fi', 'Projecteur', 'Système audio', 'Tables modulaires', 'Climatisation']
    },
    {
        'name': 'Cabine Marrakech',
        'description': 'Une cabine insonorisée avec une ambiance marocaine authentique. Idéale pour les appels vidéo et les réunions virtuelles dans un cadre élégant.',
        'capacity': 4,
        'price_per_hour': 400,
        'image_url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'is_available': True,
        'amenities': ['Wi-Fi', 'Écran HD', 'Caméra HD', 'Microphone', 'Thé à la menthe']
    },
    {
        'name': 'Espace Casablanca',
        'description': 'Un espace moderne inspiré de l\'Art déco de Casablanca. Parfait pour le travail collaboratif avec une touche marocaine contemporaine.',
        'capacity': 15,
        'price_per_hour': 750,
        'image_url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'is_available': True,
        'amenities': ['Wi-Fi', 'Zones de concentration', 'Espace de détente', 'Imprimante', 'Café marocain']
    }
]

def download_image(url):
    try:
        response = requests.get(url)
        return BytesIO(response.content)
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def add_sample_rooms():
    # Create media directory if it doesn't exist
    media_dir = os.path.join(settings.MEDIA_ROOT, 'room_images')
    os.makedirs(media_dir, exist_ok=True)
    
    # Clear existing rooms
    Room.objects.all().delete()
    print("Existing rooms deleted.")

    for room_data in rooms_data:
        try:
            # Create room object with amenities
            room = Room.objects.create(
                name=room_data['name'],
                description=room_data['description'],
                capacity=room_data['capacity'],
                price_per_hour=room_data['price_per_hour'],
                is_available=room_data['is_available'],
                amenities=room_data['amenities']
            )
            
            # Download and save image
            image_content = download_image(room_data['image_url'])
            if image_content:
                image_name = f"{room_data['name'].lower().replace(' ', '_')}.jpg"
                image_path = os.path.join(media_dir, image_name)
                
                with open(image_path, 'wb') as f:
                    f.write(image_content.getvalue())
                
                with open(image_path, 'rb') as f:
                    room.image.save(image_name, File(f), save=True)
            
            print(f"Added room: {room.name}")
        except Exception as e:
            print(f"Error adding room {room_data['name']}: {e}")

if __name__ == '__main__':
    add_sample_rooms() 