import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject1.settings')
django.setup()

from rooms.models import Room

def create_sample_rooms():
    """Create sample rooms if none exist"""
    if Room.objects.count() == 0:
        print("Creating sample rooms...")
        
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
        
        for room_data in rooms_data:
            Room.objects.create(**room_data)
            print(f"Created room: {room_data['name']}")
        
        print(f"Created {len(rooms_data)} sample rooms")
    else:
        print(f"Skipping room creation, {Room.objects.count()} rooms already exist")

if __name__ == '__main__':
    create_sample_rooms()
