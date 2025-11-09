# Deploy to Railway (Better FastAPI Support)

Railway handles FastAPI much better than Vercel for POST requests.

## Steps:

1. **Go to [railway.app](https://railway.app)**
2. **Connect your GitHub repository**
3. **Add environment variables:**
   - `TURSO_DATABASE_URL`: libsql://ourarea-praveencoder2007.aws-ap-south-1.turso.io
   - `TURSO_AUTH_TOKEN`: your-turso-token
   - `SECRET_KEY`: your-secret-key

4. **Railway will auto-detect FastAPI and deploy**

## Test URLs:
- Base: `https://your-app.railway.app/`
- Login: `POST https://your-app.railway.app/login`
- Areas: `GET https://your-app.railway.app/areas`
- Posts: `POST https://your-app.railway.app/posts`

Railway provides better FastAPI support with proper POST handling! 🚀