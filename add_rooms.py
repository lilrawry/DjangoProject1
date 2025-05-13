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
        'description': 'Une salle de conférence luxueuse avec une vue imprenable sur la ville. Décoration inspirée de l\'architecture marocaine traditionnelle, idéale pour les réunions d\'affaires importantes. Équipée des dernières technologies et d\'un service de restauration premium.',
        'capacity': 20,
        'price_per_hour': 800,
        'image_url': 'https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg',  # Grande salle de conférence luxueuse
        'is_available': True,
        'amenities': ['Wi-Fi haut débit', 'Écran 75" 4K', 'Système audio premium', 'Table de conférence en bois précieux', 'Service de restauration', 'Climatisation', 'Thé à la menthe', 'Pâtisseries marocaines']
    },
    {
        'name': 'Espace Medina',
        'description': 'Un espace créatif inspiré des riads marocains, avec une cour intérieure et une décoration traditionnelle. Parfait pour les sessions de brainstorming et les ateliers créatifs. L\'ambiance chaleureuse et l\'architecture authentique créent un cadre idéal pour l\'innovation.',
        'capacity': 12,
        'price_per_hour': 600,
        'image_url': 'https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg',  # Espace créatif style riad
        'is_available': True,
        'amenities': ['Wi-Fi', 'Tableaux blancs interactifs', 'Espace de détente', 'Thé à la menthe', 'Pâtisseries marocaines', 'Jardin intérieur', 'Fontaine traditionnelle', 'Climatisation']
    },
    {
        'name': 'Salle Hassan II',
        'description': 'Une salle de réunion moderne avec des touches de design marocain. Équipée des dernières technologies pour les présentations et les réunions virtuelles. L\'acoustique parfaite et l\'éclairage ajustable en font un espace idéal pour les réunions professionnelles.',
        'capacity': 16,
        'price_per_hour': 700,
        'image_url': 'https://images.pexels.com/photos/1181673/pexels-photo-1181673.jpeg',  # Salle de réunion moderne
        'is_available': True,
        'amenities': ['Wi-Fi', 'Écran 65"', 'Système de visioconférence', 'Table de réunion modulaire', 'Climatisation', 'Service de café', 'Éclairage ajustable', 'Insonorisation']
    },
    {
        'name': 'Cabine Marrakech',
        'description': 'Un espace de réunion intime avec une décoration authentique marocaine. Idéal pour les réunions confidentielles et les entretiens. L\'ambiance chaleureuse et le confort moderne se marient parfaitement.',
        'capacity': 6,
        'price_per_hour': 400,
        'image_url': 'https://images.pexels.com/photos/1181675/pexels-photo-1181675.jpeg',  # Petite salle de réunion intime
        'is_available': True,
        'amenities': ['Wi-Fi', 'Écran 55"', 'Système audio', 'Table de réunion', 'Climatisation', 'Thé à la menthe', 'Insonorisation', 'Éclairage d\'ambiance']
    },
    {
        'name': 'Espace Casablanca',
        'description': 'Un centre d\'affaires contemporain avec des influences architecturales marocaines. Espace polyvalent adapté aux réunions d\'équipe et aux événements professionnels. Design moderne et fonctionnel avec une touche marocaine distinctive.',
        'capacity': 24,
        'price_per_hour': 900,
        'image_url': 'https://images.pexels.com/photos/1181679/pexels-photo-1181679.jpeg',  # Centre d'affaires moderne
        'is_available': True,
        'amenities': ['Wi-Fi haut débit', 'Écran géant 85"', 'Système audio surround', 'Tables modulaires', 'Climatisation', 'Service de restauration', 'Espace de networking', 'Parking privé']
    },
    {
        'name': 'Salle Rabat',
        'description': 'Une salle de réunion moderne avec un design épuré et des éléments décoratifs marocains. Parfaite pour les réunions d\'équipe et les présentations. L\'espace est conçu pour favoriser la productivité tout en offrant un cadre agréable.',
        'capacity': 10,
        'price_per_hour': 500,
        'image_url': 'https://images.pexels.com/photos/1181681/pexels-photo-1181681.jpeg',  # Salle de réunion moderne et épurée
        'is_available': True,
        'amenities': ['Wi-Fi', 'Écran 60"', 'Système audio', 'Table de réunion', 'Climatisation', 'Service de café', 'Éclairage naturel', 'Vue sur la ville']
    }
]

def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
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