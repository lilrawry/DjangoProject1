# Django Project Deployment Guide

This Django project has been configured for deployment on Render. Follow these instructions to deploy your application.

## Prerequisites

- Render account: [https://render.com](https://render.com)
- Git + GitHub account

## Project Configuration

This project has already been configured for Render deployment with:

1. **WhiteNoise middleware** for static files
2. **Gunicorn WSGI configuration**
3. **Updated ALLOWED_HOSTS** for Render domains
4. **Required dependencies** in requirements.txt
5. **Environment variables** configuration
6. **PostgreSQL database** support via dj-database-url

## Deployment Steps

### Method 1: Using Render Dashboard

1. Push this project to a GitHub repository
2. Log in to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" and select "Web Service"
4. Connect your GitHub repository
5. Configure your web service:
   - Name: Choose a name for your service
   - Environment: Python
   - Region: Choose the closest to your users
   - Branch: main (or your default branch)
   - Build Command: `./build.sh`
   - Start Command: `gunicorn DjangoProject1.wsgi:application`
6. Add the following environment variables:
   - `SECRET_KEY`: Generate a secure random key
   - `DEBUG`: false
   - `DJANGO_SETTINGS_MODULE`: DjangoProject1.settings
   - `SITE_URL`: Your Render URL (e.g., https://your-app.onrender.com)
7. Click "Create Web Service"

### Method 2: Using render.yaml (Recommended)

1. Push this project to a GitHub repository
2. Log in to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" and select "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect the render.yaml file and set up your services
6. Review the configuration and click "Apply"

## Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Database Configuration

This project is configured to use SQLite locally and PostgreSQL on Render. The database URL is automatically configured via the `DATABASE_URL` environment variable on Render.

## Environment Variables

If your project uses environment variables, make sure to configure them in the Vercel dashboard:

1. Go to your project in the Vercel dashboard
2. Navigate to "Settings" > "Environment Variables"
3. Add your environment variables (e.g., SECRET_KEY, DATABASE_URL)

## Database Configuration

This project is currently using SQLite. For production, consider using a PostgreSQL database:

1. Add to settings.py:
   ```python
   import dj_database_url
   
   DATABASES = {
       'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
   }
   ```

2. Add your database URL as an environment variable in Vercel.

## Static Files

Before deploying, it's good practice to collect static files:

```bash
python manage.py collectstatic --noinput
```

## Troubleshooting

- Make sure Vercel is using Python 3.10+ (set via settings)
- If your app crashes, check logs with:
  ```bash
  vercel logs <deployment-url>
  ```
- Use `.env` file locally, and set secrets via Vercel Dashboard
