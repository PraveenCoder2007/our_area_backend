# Deployment Guide: Vercel + Turso

## 1. Setup Turso Database

```bash
# Install Turso CLI
curl -sSfL https://get.tur.so/install.sh | bash

# Create database
turso db create our-area-db

# Get database URL
turso db show our-area-db --url

# Create auth token
turso db tokens create our-area-db

# Apply schema
turso db shell our-area-db < schema.sql
```

## 2. Deploy to Vercel

1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables in Vercel Dashboard:
   - `TURSO_DATABASE_URL`: Your Turso database URL
   - `TURSO_AUTH_TOKEN`: Your Turso auth token
   - `SECRET_KEY`: Strong random secret
   - `CORS_ORIGINS`: Your frontend domains

## 3. Test Deployment

Your API will be available at: `https://your-project.vercel.app/api/`

- Docs: `https://your-project.vercel.app/api/docs`
- Health: `https://your-project.vercel.app/api/`