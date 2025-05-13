import os
import sys
import traceback

def wsgi_app(environ, start_response):
    try:
        # Add the project directory to the path
        project_dir = os.path.dirname(__file__)
        sys.path.insert(0, project_dir)
        
        # Set the Django settings module
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject1.settings")
        
        # Set DEBUG to True for development
        os.environ["DEBUG"] = "True"
        
        # Import Django WSGI application only when needed
        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        
        # Let Django handle the request
        return application(environ, start_response)
        
    except Exception as e:
        # Handle exceptions and provide useful error information
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        
        error_message = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}\n\n"
        error_message += f"Python version: {sys.version}\n"
        error_message += f"Path: {sys.path}\n"
        error_message += f"Working directory: {os.getcwd()}\n"
        error_message += f"Environment: {os.environ}\n"
        
        return [error_message.encode()]

# This will be imported by Vercel
app = wsgi_app
