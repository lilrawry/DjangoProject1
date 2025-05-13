import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Add the project directory to the path
    project_dir = os.path.dirname(__file__)
    sys.path.append(project_dir)
    logger.info(f"Added {project_dir} to path")
    
    # Add parent directory to support imports
    parent_dir = os.path.dirname(project_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        logger.info(f"Added {parent_dir} to path")
    
    # List all files in the project directory for debugging
    logger.info(f"Files in {project_dir}: {os.listdir(project_dir)}")
    
    # Set the settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject1.settings")
    logger.info("Set DJANGO_SETTINGS_MODULE")
    
    # Get WSGI application
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
    logger.info("WSGI application initialized successfully")
    
except Exception as e:
    logger.error(f"Error in vercel_wsgi.py: {str(e)}")
    raise e
