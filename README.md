# Django Project Vercel Deployment Guide

This Django project has been configured for deployment on Vercel. Follow these instructions to deploy your application.

## Prerequisites

- Vercel account: [https://vercel.com](https://vercel.com)
- Git + GitHub account
- Node.js installed (for Vercel CLI)

## Project Configuration

This project has already been configured for Vercel deployment with:

1. **WhiteNoise middleware** for static files
2. **Vercel-compatible WSGI configuration**
3. **Updated ALLOWED_HOSTS**
4. **Required dependencies** in requirements.txt

## Deployment Steps

### Method 1: Using Vercel CLI

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Run the deployment command in the project root:
   ```bash
   vercel
   ```

3. Follow the CLI prompts:
   - Select the correct scope
   - Select current directory
   - Choose `vercel_wsgi.py` as the entry file
   - Confirm deployment settings

### Method 2: Connect GitHub to Vercel

1. Push this project to a GitHub repository
2. Go to [https://vercel.com/dashboard](https://vercel.com/dashboard)
3. Click "Add New Project"
4. Import your Django repository
5. Set the Framework as "Other"
6. Set `vercel_wsgi.py` as the entry file
7. Set Build Command: leave blank or use `pip install -r requirements.txt`
8. Set Output Directory: leave it blank
9. Deploy

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
