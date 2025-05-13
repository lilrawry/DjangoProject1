from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
import requests
from io import BytesIO
import os
from rooms.models import Room

class Command(BaseCommand):
    help = 'Adds sample rooms to the database'

    def handle(self, *args, **options):
        # Sample room data
        rooms_data = [
            {
                'name': 'Salle de Réunion Exécutive',
                'description': 'Une salle de réunion élégante et moderne, idéale pour les réunions d\'équipe et les présentations. Équipée d\'un grand écran et d\'un système audio de haute qualité.',
                'capacity': 12,
                'price_per_hour': 150,
                'image_url': 'https://images.unsplash.com/photo-1517502166878-35c93a0072f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
                'is_available': True,
                'amenities': ['Wi-Fi', 'Écran 65"', 'Système audio', 'Table de conférence', 'Café']
            },
            {
                'name': 'Espace de Créativité',
                'description': 'Un espace lumineux et inspirant, parfait pour les sessions de brainstorming et les ateliers créatifs. Les murs sont équipés de tableaux blancs et d\'espaces d\'affichage.',
                'capacity': 8,
                'price_per_hour': 100,
                'image_url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
                'is_available': True,
                'amenities': ['Wi-Fi', 'Tableaux blancs', 'Post-it', 'Espace de détente', 'Thé et café']
            },
            {
                'name': 'Salle de Formation',
                'description': 'Une salle spacieuse conçue pour les sessions de formation et les ateliers. Équipée de tables modulaires et d\'un système de projection professionnel.',
                'capacity': 20,
                'price_per_hour': 200,
                'image_url': 'https://images.unsplash.com/photo-1517502166878-35c93a0072f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
                'is_available': True,
                'amenities': ['Wi-Fi', 'Projecteur', 'Système audio', 'Tables modulaires', 'Climatisation']
            },
            {
                'name': 'Cabine de Téléconférence',
                'description': 'Une cabine insonorisée pour les appels vidéo et les réunions virtuelles. Équipée d\'un écran HD et d\'un système audio de qualité professionnelle.',
                'capacity': 4,
                'price_per_hour': 50,
                'image_url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
                'is_available': True,
                'amenities': ['Wi-Fi', 'Écran HD', 'Caméra HD', 'Microphone', 'Insonorisation']
            },
            {
                'name': 'Espace de Collaboration',
                'description': 'Un espace ouvert et flexible pour le travail collaboratif. Idéal pour les équipes qui ont besoin d\'un espace de travail partagé avec des zones de concentration.',
                'capacity': 15,
                'price_per_hour': 120,
                'image_url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
                'is_available': True,
                'amenities': ['Wi-Fi', 'Zones de concentration', 'Espace de détente', 'Imprimante', 'Café']
            },
            {
                'name': 'Salle de Présentation',
                'description': 'Une salle moderne et professionnelle pour les présentations importantes. Équipée d\'un grand écran 4K et d\'un système audio surround.',
                'capacity': 30,
                'price_per_hour': 250,
                'image_url': 'https://images.unsplash.com/photo-1517502166878-35c93a0072f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
                'is_available': True,
                'amenities': ['Wi-Fi', 'Écran 4K', 'Système audio surround', 'Scène', 'Climatisation']
            }
        ]

        # Create media directory if it doesn't exist
        media_dir = os.path.join(settings.MEDIA_ROOT, 'room_images')
        os.makedirs(media_dir, exist_ok=True)
        
        # Clear existing rooms
        Room.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Existing rooms deleted."))

        for room_data in rooms_data:
            try:
                # Create room object
                room = Room.objects.create(
                    name=room_data['name'],
                    description=room_data['description'],
                    capacity=room_data['capacity'],
                    price_per_hour=room_data['price_per_hour'],
                    is_available=room_data['is_available']
                )
                
                # Download and save image
                try:
                    response = requests.get(room_data['image_url'])
                    image_content = BytesIO(response.content)
                    
                    image_name = f"{room_data['name'].lower().replace(' ', '_')}.jpg"
                    image_path = os.path.join(media_dir, image_name)
                    
                    with open(image_path, 'wb') as f:
                        f.write(image_content.getvalue())
                    
                    with open(image_path, 'rb') as f:
                        room.image.save(image_name, File(f), save=True)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error downloading image for {room_data['name']}: {e}"))
                
                # Add amenities
                for amenity in room_data['amenities']:
                    room.amenities.append(amenity)
                room.save()
                
                self.stdout.write(self.style.SUCCESS(f"Added room: {room.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error adding room {room_data['name']}: {e}")) 