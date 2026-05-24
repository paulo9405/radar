# Deployment Guide - Render

This guide covers deploying the Radar de Tendências Django application to Render.

## Prerequisites

- GitHub account with this repository pushed
- Render account (sign up at https://render.com)
- PostgreSQL database on Render (will be created during deployment)

## Step 1: Push Code to GitHub

Ensure all your code is committed and pushed to GitHub:

```bash
git add .
git commit -m "Configure for Render deployment"
git push origin main
```

## Step 2: Create PostgreSQL Database on Render

1. Log in to your Render dashboard
2. Click "New +" and select "PostgreSQL"
3. Configure your database:
   - **Name**: `radar-db` (or your preferred name)
   - **Database**: `radar_db`
   - **User**: (auto-generated)
   - **Region**: Choose closest to your target audience
   - **PostgreSQL Version**: 15 or latest
   - **Plan**: Free or paid plan
4. Click "Create Database"
5. **Important**: Copy the "Internal Database URL" - you'll need this for the web service

## Step 3: Create Web Service on Render

1. From your Render dashboard, click "New +" and select "Web Service"
2. Connect your GitHub repository
3. Configure the web service:

### Basic Settings
- **Name**: `radar-tendencias` (or your preferred name)
- **Region**: Same as your database
- **Branch**: `main`
- **Root Directory**: Leave empty (or specify if your Django project is in a subdirectory)
- **Runtime**: Python 3
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn radar_project.wsgi:application`

### Environment Variables

Click "Advanced" and add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.9.6` | Should match runtime.txt |
| `SECRET_KEY` | `<generate-random-key>` | See below for generation |
| `DEBUG` | `False` | MUST be False in production |
| `ALLOWED_HOSTS` | `your-app.onrender.com` | Replace with your actual Render URL |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.onrender.com` | Replace with your actual URL (include https://) |
| `DATABASE_URL` | `<your-internal-database-url>` | Paste from Step 2 |

#### Generating SECRET_KEY

Run this command locally to generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as your `SECRET_KEY` value.

### Auto-Deploy

- Enable "Auto-Deploy" if you want automatic deployments on git push

## Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies from `requirements.txt`
   - Run `collectstatic` to gather static files
   - Run database migrations
   - Start the application with Gunicorn

3. Monitor the deployment logs for any errors
4. Once deployed, your app will be available at `https://your-app.onrender.com`

## Step 5: Verify Deployment

1. Visit your Render URL
2. Test the landing page and form submission
3. Check that static files (CSS, images) load correctly
4. Verify form submissions are saved to the PostgreSQL database

## Step 6: Custom Domain (Optional)

To use a custom domain:

1. In your Render web service settings, go to "Custom Domain"
2. Add your domain (e.g., `www.radardetendencias.com`)
3. Follow Render's instructions to configure DNS records
4. Update environment variables:
   - Add your custom domain to `ALLOWED_HOSTS`
   - Add `https://www.yourdomain.com` to `CSRF_TRUSTED_ORIGINS`

Example:
```
ALLOWED_HOSTS=your-app.onrender.com,www.radardetendencias.com
CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com,https://www.radardetendencias.com
```

## Troubleshooting

### Static Files Not Loading

1. Check that `STATIC_ROOT` is set in `settings.py`
2. Verify Whitenoise is in `MIDDLEWARE`
3. Check build logs to ensure `collectstatic` ran successfully
4. Verify `STORAGES` setting includes Whitenoise backend

### Database Connection Errors

1. Verify `DATABASE_URL` environment variable is set correctly
2. Ensure PostgreSQL database is running on Render
3. Check database credentials haven't expired
4. Verify `psycopg2-binary` is in `requirements.txt`

### Application Crashes

1. Check Render logs for error messages
2. Verify all environment variables are set
3. Ensure `DEBUG=False` in production
4. Check that `SECRET_KEY` is set and not the default
5. Verify Python version matches `runtime.txt`

### CSRF Errors

1. Ensure `CSRF_TRUSTED_ORIGINS` includes your full URL with `https://`
2. Verify `ALLOWED_HOSTS` includes your domain
3. Check that SSL redirect is enabled (handled automatically by Render)

## Maintenance

### Updating the Application

1. Make changes locally
2. Commit and push to GitHub
3. If Auto-Deploy is enabled, Render will automatically deploy
4. Otherwise, manually trigger deployment from Render dashboard

### Viewing Logs

- In Render dashboard, go to your web service
- Click "Logs" to view real-time application logs
- Useful for debugging and monitoring

### Database Backups

- Render automatically backs up PostgreSQL databases on paid plans
- For free plans, manually export data periodically:
  - Connect to database via provided connection string
  - Use `pg_dump` to create backups

### Scaling

- Render free tier: 1 instance, sleeps after inactivity
- Upgrade to paid plan for:
  - Always-on instances
  - Multiple instances
  - More CPU/RAM
  - Better database performance

## Security Checklist

- [x] `DEBUG=False` in production
- [x] Strong `SECRET_KEY` set via environment variable
- [x] `ALLOWED_HOSTS` properly configured
- [x] `CSRF_TRUSTED_ORIGINS` properly configured
- [x] SSL/HTTPS enabled (automatic on Render)
- [x] HSTS headers enabled when `DEBUG=False`
- [x] Secure cookies enabled when `DEBUG=False`
- [x] PostgreSQL instead of SQLite
- [x] `.env` file in `.gitignore` (never commit secrets)

## Project Structure

```
radar_proj/radar/
├── build.sh                    # Build script for Render
├── runtime.txt                 # Python version specification
├── requirements.txt            # Production dependencies
├── .env.example               # Example environment variables
├── manage.py                  # Django management script
├── radar_project/
│   ├── settings.py            # Production-ready settings
│   ├── urls.py
│   └── wsgi.py                # WSGI application
└── landing/                   # Landing page app
    ├── models.py              # Lead model
    ├── forms.py               # Lead capture form
    ├── views.py               # Views
    ├── templates/             # HTML templates
    └── static/                # CSS, JS, images
```

## Support

For issues specific to:
- **Render Platform**: https://render.com/docs
- **Django**: https://docs.djangoproject.com/
- **This Project**: Check application logs and settings configuration

## Quick Reference

### Render Commands
- View logs: Render Dashboard → Your Service → Logs
- Manual deploy: Render Dashboard → Your Service → Manual Deploy
- Shell access: Render Dashboard → Your Service → Shell

### Django Commands (via Render Shell)
```bash
# Create superuser for admin access
python manage.py createsuperuser

# Check migrations
python manage.py showmigrations

# Run migrations manually
python manage.py migrate

# Collect static files manually
python manage.py collectstatic --noinput
```

## Environment Variables Summary

Copy this template and fill in your values:

```env
PYTHON_VERSION=3.9.6
SECRET_KEY=<your-generated-secret-key>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
DATABASE_URL=<your-postgresql-internal-url>
```

## Success!

Once deployed, your Radar de Tendências landing page will be live and ready to capture leads!

Remember to:
- Test all functionality after deployment
- Set up monitoring and alerts
- Configure custom domain if needed
- Regularly check logs for errors
- Keep dependencies updated
