PART 1: CREATE DATABASE (5 minutes)

  1. Click the blue "New +" button (top right of your screen)
  2. Select "PostgreSQL"
  3. Fill in:
    - Name: radar-db
    - Database: leave default
    - User: leave default
    - Region: Frankfurt
    - Plan: Free
  4. Click "Create Database" (blue button at bottom)
  5. WAIT for database to be created (1-2 minutes)
  6. When ready, you'll see a page with connection details
  7. Find the section called "Internal Database URL"
  8. Click the copy icon next to it
  9. Paste this URL somewhere safe (notepad/notes) - you'll need it in Part 2

  ---
  PART 2: CREATE WEB SERVICE (10 minutes)

  A) Connect Repository

  1. Click the blue "New +" button again
  2. Select "Web Service"
  3. Click "Build and deploy from a Git repository" → Next
  4. Find your repository: paulo9405/radar
    - If you don't see it, click "Configure account" to connect GitHub
  5. Click "Connect" next to paulo9405/radar

  B) Basic Settings

  You'll see a configuration form. Fill in:

  6. Name: radar-tendencias
  7. Region: Frankfurt
  8. Branch: main
  9. Root Directory: (leave empty)
  10. Runtime: Select "Python 3"
  11. Build Command: Type exactly: ./build.sh
  12. Start Command: Type exactly: gunicorn radar_project.wsgi:application

  C) Select Plan

  13. Plan: Select "Free"

  D) Add Environment Variables

  14. Click "Advanced" button (expands more options)
  15. Scroll down to "Environment Variables"
  16. Click "Add Environment Variable" button

  Add these 6 variables one by one (click "Add Environment Variable" for each):

  Variable 1:
  - Key: PYTHON_VERSION
  - Value: 3.9.6

  Variable 2:
  - Key: DEBUG
  - Value: False

  Variable 3:
  - Key: SECRET_KEY
  - Value: smpf_kb393$95u1ak=rj2y9-xkg+l#ht5koel&3p5)qu%@+$^8

  Variable 4:
  - Key: ALLOWED_HOSTS
  - Value: radar-tendencias.onrender.com

  Variable 5:
  - Key: CSRF_TRUSTED_ORIGINS
  - Value: https://radar-tendencias.onrender.com

  Variable 6:
  - Key: DATABASE_URL
  - Value: (paste the Internal Database URL you copied in step 9)

  E) Deploy

  17. Scroll down to the bottom
  18. Click the blue "Create Web Service" button
  19. WAIT while Render deploys (5-10 minutes)
    - You'll see logs scrolling
    - When finished, status will show "Live" (green dot)

  ---
  PART 3: TEST YOUR SITE

  20. Click the URL shown at the top (something like https://radar-tendencias.onrender.com)
  21. Check that your landing page loads
  22. Fill out the form and submit to test database connection

  ---
  SIMPLE CHECKLIST

  - Create PostgreSQL database
  - Copy Internal Database URL
  - Create new Web Service
  - Connect GitHub repository paulo9405/radar
  - Set build command: ./build.sh
  - Set start command: gunicorn radar_project.wsgi:application
  - Add 6 environment variables
  - Click "Create Web Service"
  - Wait for deployment to finish
  - Visit your site and test

  Start here: Click "New +" → "PostgreSQL"

  Need help with a specific step? Let me know which number you're stuck on!