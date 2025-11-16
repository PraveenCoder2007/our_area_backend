# Render Deployment Guide

## 🚀 Deploy Our Area API to Render

### Prerequisites
- GitHub account with the repository
- Render account (free tier available)
- Turso database setup

## Step 1: Prepare Repository

1. **Ensure files are ready**:
   - `main.py` - Main FastAPI application
   - `requirements.txt` - Python dependencies
   - `render.yaml` - Render configuration (optional)

2. **Check requirements.txt**:
   ```txt
   fastapi==0.104.1
   uvicorn==0.24.0
   python-jose[cryptography]==3.3.0
   passlib[bcrypt]==1.7.4
   requests==2.31.0
   pydantic==2.5.0
   ```

## Step 2: Create Turso Database

1. **Install Turso CLI**:
   ```bash
   # macOS/Linux
   curl -sSfL https://get.tur.so/install.sh | bash
   
   # Windows
   powershell -c "irm get.tur.so/install.ps1 | iex"
   ```

2. **Create database**:
   ```bash
   turso auth signup
   turso db create our-area-db
   turso db show our-area-db
   ```

3. **Get credentials**:
   ```bash
   turso db show our-area-db --url
   turso db tokens create our-area-db
   ```

## Step 3: Deploy to Render

### Option A: Web Dashboard

1. **Go to Render Dashboard**:
   - Visit https://render.com
   - Sign up/Login with GitHub

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. **Configure Service**:
   - **Name**: `our-area-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

4. **Set Environment Variables**:
   ```
   TURSO_DB_URL=libsql://your-database-name.turso.io
   TURSO_DB_TOKEN=your-turso-auth-token
   SECRET_KEY=your-secret-key-32-chars-minimum
   PORT=8000
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete

### Option B: render.yaml Configuration

1. **Create render.yaml**:
   ```yaml
   services:
     - type: web
       name: our-area-backend
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python main.py
       envVars:
         - key: TURSO_DB_URL
           value: libsql://your-database-name.turso.io
         - key: TURSO_DB_TOKEN
           value: your-turso-auth-token
         - key: SECRET_KEY
           generateValue: true
         - key: PORT
           value: 8000
   ```

2. **Deploy**:
   - Push render.yaml to repository
   - Render will auto-deploy

## Step 4: Configure Environment Variables

### Required Variables
```env
TURSO_DB_URL=libsql://your-database-name.turso.io
TURSO_DB_TOKEN=your-turso-auth-token
SECRET_KEY=your-secret-key-32-chars-minimum
PORT=8000
```

### Generate Secret Key
```python
import secrets
print(secrets.token_urlsafe(32))
```

## Step 5: Verify Deployment

1. **Check Service URL**:
   - Your API will be available at: `https://your-service-name.onrender.com`

2. **Test Endpoints**:
   ```bash
   # Health check
   curl https://your-service-name.onrender.com/
   
   # API docs
   curl https://your-service-name.onrender.com/docs
   
   # Database test
   curl https://your-service-name.onrender.com/test-db
   ```

## Step 6: Custom Domain (Optional)

1. **Add Custom Domain**:
   - Go to service settings
   - Add your domain name
   - Configure DNS records

2. **SSL Certificate**:
   - Render provides free SSL certificates
   - Automatically configured

## Troubleshooting

### Common Issues

**Build Failures**:
```bash
# Check requirements.txt format
# Ensure Python version compatibility
# Verify all dependencies are listed
```

**Environment Variables**:
```bash
# Check variable names match exactly
# Verify Turso credentials are correct
# Ensure SECRET_KEY is long enough
```

**Database Connection**:
```bash
# Test Turso connection locally
# Verify database URL format
# Check token permissions
```

### Debug Steps

1. **Check Build Logs**:
   - View build logs in Render dashboard
   - Look for dependency installation errors

2. **Check Runtime Logs**:
   - Monitor application logs
   - Check for startup errors

3. **Test Locally**:
   ```bash
   # Set environment variables
   export TURSO_DB_URL="your-url"
   export TURSO_DB_TOKEN="your-token"
   export SECRET_KEY="your-secret"
   
   # Run locally
   python main.py
   ```

## Performance Optimization

### Free Tier Limitations
- Service sleeps after 15 minutes of inactivity
- 750 hours/month free compute time
- 100GB bandwidth/month

### Optimization Tips
1. **Keep Service Warm**:
   - Use uptime monitoring services
   - Implement health check endpoints

2. **Database Optimization**:
   - Use indexes for frequent queries
   - Implement connection pooling
   - Cache frequently accessed data

3. **Response Optimization**:
   - Enable gzip compression
   - Minimize response payload size
   - Use pagination for large datasets

## Monitoring & Maintenance

### Health Monitoring
```python
# Add to main.py
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### Log Monitoring
- Use Render's built-in logging
- Monitor error rates and response times
- Set up alerts for critical issues

### Database Backup
```bash
# Backup Turso database
turso db dump our-area-db --output backup.sql

# Restore from backup
turso db shell our-area-db < backup.sql
```

## Scaling Options

### Upgrade Plans
- **Starter**: $7/month - No sleep, more resources
- **Standard**: $25/month - Autoscaling, more bandwidth
- **Pro**: $85/month - Priority support, advanced features

### Horizontal Scaling
- Multiple service instances
- Load balancing
- Database read replicas

## Security Best Practices

1. **Environment Variables**:
   - Never commit secrets to repository
   - Use Render's environment variable encryption
   - Rotate secrets regularly

2. **API Security**:
   - Implement rate limiting
   - Use HTTPS only
   - Validate all inputs

3. **Database Security**:
   - Use least privilege access
   - Enable audit logging
   - Regular security updates

## Continuous Deployment

### Auto-Deploy Setup
1. **Connect GitHub**:
   - Link repository to Render service
   - Enable auto-deploy on push

2. **Branch Configuration**:
   - Deploy from `main` branch
   - Use staging branches for testing

3. **Deploy Hooks**:
   ```bash
   # Pre-deploy script
   pip install -r requirements.txt
   python -m pytest tests/
   
   # Post-deploy script
   curl https://your-service.onrender.com/health
   ```

---

**Deployment Complete!** 🎉

Your API is now live at: `https://your-service-name.onrender.com`

- **API Docs**: `/docs`
- **Health Check**: `/health`
- **Database Test**: `/test-db`