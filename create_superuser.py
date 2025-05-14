import os
import django
from django.contrib.auth import get_user_model

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject1.settings')
django.setup()

User = get_user_model()

# Define superuser credentials - these will be used if environment variables are not set
DEFAULT_SUPERUSER_USERNAME = 'admin'
DEFAULT_SUPERUSER_EMAIL = 'admin@example.com'
DEFAULT_SUPERUSER_PASSWORD = 'admin123'  # This is just a fallback, use environment variables in production!

def create_superuser():
    # Get credentials from environment variables or use defaults
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', DEFAULT_SUPERUSER_USERNAME)
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', DEFAULT_SUPERUSER_EMAIL)
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', DEFAULT_SUPERUSER_PASSWORD)
    
    # Check if the superuser already exists
    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists")
        return
    
    # Create superuser
    try:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully")
    except Exception as e:
        print(f"Error creating superuser: {e}")

if __name__ == '__main__':
    create_superuser()
