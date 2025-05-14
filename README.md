# Django Project Deployment Guide

This Django project has been configured for deployment on Railway. Follow these instructions to deploy your application.

## Prerequisites

- Railway account: [https://railway.app](https://railway.app)
- Git + GitHub account

## Project Configuration

This project has already been configured for Railway deployment with:

1. **WhiteNoise middleware** for static files
2. **Gunicorn WSGI configuration**
3. **Updated ALLOWED_HOSTS** for Railway domains
4. **Required dependencies** in requirements.txt
5. **Environment variables** configuration
6. **PostgreSQL database** support via dj-database-url

## Deployment Steps

### Method 1: Using Railway Dashboard

1. Push this project to a GitHub repository
2. Log in to [Railway Dashboard](https://railway.app/dashboard)
3. Click "New Project" and select "Deploy from GitHub repo"
4. Connect your GitHub repository
5. Railway will automatically detect your project configuration
6. Add the following environment variables in the Variables tab:
   - `SECRET_KEY`: Generate a secure random key
   - `DEBUG`: false
   - `DJANGO_SETTINGS_MODULE`: DjangoProject1.settings
   - `SITE_URL`: Your Railway URL (e.g., https://your-app.up.railway.app)
7. Click "Deploy"

### Method 2: Using Railway CLI (Alternative)

1. Install the Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link your project:
   ```bash
   railway link
   ```

4. Deploy your project:
   ```bash
   railway up
   ```

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

This project is configured to use SQLite locally and PostgreSQL on Railway. The database URL is automatically configured via the `DATABASE_URL` environment variable on Railway.

To set up a PostgreSQL database on Railway:

1. In your Railway project, click "New" and select "Database" → "PostgreSQL"
2. Once created, go to the Variables tab of your web service
3. Railway will automatically add the `DATABASE_URL` variable from your PostgreSQL instance

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
