# 🚀 Deployment Guide - AnalytixAI

## Overview
This guide covers deploying AnalytixAI to production environments.

---

## Prerequisites

- ✅ MongoDB Atlas account (already configured)
- ✅ Domain name (optional but recommended)
- ✅ SSL certificate (for HTTPS)

---

## Backend Deployment Options

### Option 1: Railway.app (Recommended - Free Tier Available)

1. **Prepare for deployment**
   ```bash
   # Create Procfile in backend/
   echo "web: uvicorn main:app --host 0.0.0.0 --port $PORT" > backend/Procfile
   ```

2. **Deploy to Railway**
   - Visit: https://railway.app
   - Connect your GitHub repository
   - Select backend folder
   - Add environment variables from `.env`
   - Deploy!

3. **Set Environment Variables**
   - MONGO_URL
   - SECRET_KEY
   - DB_NAME
   - ALLOWED_ORIGINS (add your frontend URL)

### Option 2: Render.com (Free Tier)

1. **Create `render.yaml` in backend/**
   ```yaml
   services:
     - type: web
       name: analytixai-backend
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Deploy**
   - Visit: https://render.com
   - Connect repository
   - Configure environment variables
   - Deploy

### Option 3: Heroku

1. **Create `Procfile` in backend/**
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Create `runtime.txt`**
   ```
   python-3.11.0
   ```

3. **Deploy**
   ```bash
   heroku login
   cd backend
   heroku create analytixai-backend
   heroku config:set MONGO_URL="your_mongo_url"
   heroku config:set SECRET_KEY="your_secret_key"
   git push heroku main
   ```

### Option 4: VPS (DigitalOcean, AWS, etc.)

1. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```

2. **Setup application**
   ```bash
   cd /var/www
   git clone your-repo
   cd Demo AutoDataAnalytics/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create systemd service**
   ```bash
   sudo nano /etc/systemd/system/analytixai.service
   ```
   
   Content:
   ```ini
   [Unit]
   Description=AnalytixAI Backend
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/Demo AutoDataAnalytics/backend
   Environment="PATH=/var/www/Demo AutoDataAnalytics/backend/venv/bin"
   ExecStart=/var/www/Demo AutoDataAnalytics/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service**
   ```bash
   sudo systemctl start analytixai
   sudo systemctl enable analytixai
   ```

5. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## Frontend Deployment Options

### Option 1: Netlify (Recommended - Free)

1. **Drag & Drop**
   - Visit: https://netlify.com
   - Drag `frontend` folder
   - Done!

2. **Update API URL**
   - Edit `frontend/script.js`
   - Change `API_BASE_URL` to your backend URL
   ```javascript
   const API_BASE_URL = "https://your-backend-url.com";
   ```

### Option 2: Vercel (Free)

1. **Deploy**
   ```bash
   cd frontend
   npx vercel deploy
   ```

2. **Configure**
   - Update API URL in `script.js`

### Option 3: GitHub Pages (Free)

1. **Create GitHub repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your-repo-url
   git push -u origin main
   ```

2. **Enable GitHub Pages**
   - Go to repository Settings → Pages
   - Select branch and `/frontend` folder
   - Save

3. **Update API URL**
   - Edit `script.js` with your backend URL

### Option 4: AWS S3 + CloudFront

1. **Create S3 bucket**
   - Enable static website hosting
   - Upload frontend files

2. **Configure CloudFront**
   - Create distribution
   - Point to S3 bucket
   - Enable HTTPS

3. **Update CORS**
   - Add CloudFront URL to backend `ALLOWED_ORIGINS`

---

## Production Checklist

### Security
- [ ] Change SECRET_KEY to a strong random value
- [ ] Use HTTPS (SSL/TLS)
- [ ] Update ALLOWED_ORIGINS to only your frontend URL
- [ ] Enable rate limiting
- [ ] Add request size limits
- [ ] Use environment variables for all secrets
- [ ] Enable database authentication

### Performance
- [ ] Enable gzip compression
- [ ] Use CDN for static files
- [ ] Optimize images
- [ ] Enable caching headers
- [ ] Monitor API response times
- [ ] Set up database indexes

### Monitoring
- [ ] Set up error logging (Sentry, LogRocket)
- [ ] Configure uptime monitoring
- [ ] Set up analytics
- [ ] Create backup strategy
- [ ] Monitor database performance

### Configuration
- [ ] Update CORS settings
- [ ] Configure file upload limits
- [ ] Set proper timeout values
- [ ] Configure email notifications (if added)
- [ ] Test all endpoints

---

## Environment Variables for Production

### Backend (.env)
```env
# Production MongoDB
MONGO_URL=mongodb+srv://prod_user:secure_password@cluster.mongodb.net/

# Strong Secret Key (generate new one!)
SECRET_KEY=use-openssl-rand-hex-32-to-generate-this

# JWT Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS (Your actual frontend URLs)
ALLOWED_ORIGINS=https://your-frontend.netlify.app,https://www.yourdomain.com

# Server
HOST=0.0.0.0
PORT=8000
```

### Generate Secure Secret Key
```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32
```

---

## Post-Deployment Testing

1. **Test Backend Health**
   ```bash
   curl https://your-backend-url.com/
   ```

2. **Test Registration**
   - Open frontend
   - Create test account
   - Verify in MongoDB

3. **Test Upload**
   - Login
   - Upload sample file
   - Verify analytics display

4. **Test Charts**
   - Check images load
   - Verify CORS is working

5. **Test Error Handling**
   - Try invalid file
   - Try large file
   - Try without login

---

## Monitoring & Maintenance

### Set Up Monitoring

**Backend:**
- Use Railway/Render built-in monitoring
- Or set up Sentry for error tracking
  ```bash
  pip install sentry-sdk
  ```

**Frontend:**
- Google Analytics
- LogRocket for session replay

### Regular Maintenance

**Weekly:**
- Check server logs
- Monitor disk space (for charts/)
- Review error reports

**Monthly:**
- Update dependencies
  ```bash
  pip install --upgrade -r requirements.txt
  ```
- Review MongoDB usage
- Check SSL certificate expiry
- Database backup

**Quarterly:**
- Security audit
- Performance optimization
- User feedback review

---

## Scaling Considerations

### When to Scale

- 🔴 Response time > 3 seconds
- 🔴 Memory usage > 80%
- 🔴 CPU usage sustained > 70%
- 🔴 Database queries slow
- 🔴 Many concurrent users

### Scaling Options

1. **Vertical Scaling**
   - Upgrade server instance
   - Add more RAM/CPU

2. **Horizontal Scaling**
   - Add more server instances
   - Use load balancer

3. **Database Scaling**
   - MongoDB Atlas auto-scaling
   - Add read replicas
   - Enable sharding

4. **Caching**
   - Add Redis for sessions
   - Cache frequent queries
   - Use CDN for static files

---

## Cost Optimization

### Free Tier Options
- **Backend**: Railway (Free), Render (Free)
- **Frontend**: Netlify (Free), Vercel (Free), GitHub Pages (Free)
- **Database**: MongoDB Atlas (Free 512MB)
- **Monitoring**: Sentry (Free tier)

### Estimated Monthly Costs (Paid Tiers)
| Service | Cost |
|---------|------|
| Backend Hosting | $5-20 |
| Frontend Hosting | $0-10 |
| MongoDB Atlas | $9-30 |
| Domain Name | $10-15/year |
| SSL Certificate | Free (Let's Encrypt) |

**Total**: ~$15-60/month for small-medium usage

---

## Rollback Strategy

If deployment fails:

1. **Keep previous version running**
2. **Test new version in staging first**
3. **Use environment-based deployment**
4. **Database migrations**: Keep backward compatible

---

## Support & Resources

- **Railway**: https://docs.railway.app
- **Render**: https://render.com/docs
- **Netlify**: https://docs.netlify.com
- **MongoDB Atlas**: https://docs.atlas.mongodb.com

---

**Ready to deploy? Start with Railway + Netlify for the easiest setup! 🚀**
