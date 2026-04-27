# 🚀 Exam Portal - Deployment Guide

## 📋 Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   User Phone    │────────▶│  Vercel/Netlify │────────▶│  Render/Railway │
│   (WhatsApp)    │         │   (Frontend)    │         │   (Backend)     │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        │                                                        │
        │         Share Link: https://app.com/join/{token}        │
        └──────────────────────────────────────────────────────────┘
```

## 🎯 Deployment Requirements

- **Frontend**: Vercel or Netlify (Free Tier)
- **Backend**: Render or Railway (Free Tier)
- **Database**: SQLite (included) or PostgreSQL
- **Custom Domain**: Optional (Vercel/Netlify provide free SSL)

---

## 🚀 Quick Deploy (5 minutes)

### Step 1: Backend Deployment (Render)

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Production ready"
   git remote add origin https://github.com/YOUR_USERNAME/exam-portal.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to https://dashboard.render.com/
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - **Settings:**
     - Name: `exam-portal-api`
     - Runtime: Python 3
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60`
     - Plan: Free
   - **Environment Variables:**
     - `SECRET_KEY`: Generate with `openssl rand -hex 32`
     - `FRONTEND_URL`: `https://your-frontend.vercel.app`
     - `APP_URL`: `https://exam-portal-api.onrender.com`
   - Click **Create Web Service**

3. **Copy your backend URL** (e.g., `https://exam-portal-api.onrender.com`)

### Step 2: Frontend Deployment (Vercel)

1. **Prepare frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Deploy on Vercel:**
   - Go to https://vercel.com/
   - Import your GitHub repository
   - **Settings:**
     - Framework: Vite
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `dist`
   - **Environment Variables:**
     - `VITE_API_URL`: `https://exam-portal-api.onrender.com`
   - Click **Deploy**

3. **Copy your frontend URL** (e.g., `https://exam-portal.vercel.app`)

### Step 3: Configure Share Link

1. **Update backend environment variable:**
   - Go to Render Dashboard → Your Service → Environment
   - Add: `FRONTEND_URL` = `https://exam-portal.vercel.app`
   - Add: `APP_URL` = `https://exam-portal-api.onrender.com`

2. **Restart backend service** (Render auto-restarts on env change)

---

## 📱 Share Link Flow

```
User clicks link in WhatsApp
    │
    ▼
https://exam-portal-api.onrender.com/join/{token}
    │
    ▼
Backend validates token (30 days expiry)
    │
    ▼
Redirects to: https://exam-portal.vercel.app/login
    │
    ▼
User logs in or registers
    │
    ▼
Access granted to dashboard
```

---

## 🔧 Environment Variables

### Backend (.env)
```bash
# Required
SECRET_KEY=your-super-secret-key-here
FRONTEND_URL=https://your-frontend.vercel.app
APP_URL=https://your-backend.onrender.com

# Optional
FLASK_ENV=production
DATABASE_URL=sqlite:///exam_portal.db  # or PostgreSQL
```

### Frontend (.env)
```bash
# Required
VITE_API_URL=https://your-backend.onrender.com

# Optional
VITE_APP_NAME=Digital Quiz Tool
VITE_ENABLE_ANALYTICS=true
```

---

## 🔒 Security Features

- ✅ HTTPS enforced on all platforms
- ✅ CORS configured for allowed origins only
- ✅ 30-day share link expiration
- ✅ Secure token generation (32-byte random)
- ✅ Session-based authentication
- ✅ XSS protection headers
- ✅ Mobile-optimized responsive design

---

## 📊 Platform-Specific Configs

### Render (Backend)
- File: `render.yaml`
- Auto-deploy on git push
- Free tier: 512MB RAM, sleeps after 15min idle
- **Uptime fix:** Use UptimeRobot ping every 10 minutes

### Vercel (Frontend)
- File: `vercel.json`
- Edge network (fast global access)
- Auto HTTPS
- Perfect for WhatsApp links

### Railway (Alternative Backend)
- Similar to Render
- Better free tier limits
- Use if Render limits are hit

---

## 🔄 Auto-Restart Setup (24/7 Uptime)

Since free tiers sleep after inactivity:

1. **UptimeRobot:** https://uptimerobot.com/
   - Add monitor: `https://exam-portal-api.onrender.com/`
   - Interval: Every 5 minutes
   - Keeps backend awake

2. **Cron-job.org:** (Alternative)
   - Ping your backend every 10 minutes
   - Free and reliable

---

## 📱 Mobile Optimization

The frontend is optimized for mobile WhatsApp access:

- ✅ Responsive design (Tailwind CSS)
- ✅ Touch-friendly buttons (min 44px)
- ✅ Fast loading (lazy loading, code splitting)
- ✅ PWA ready (add to home screen)
- ✅ Works on 3G/4G networks

---

## 🧪 Testing the Deployment

1. **Generate share link:**
   - Login to admin dashboard
   - Click "Generate Shareable Link"
   - Copy the link

2. **Test on phone:**
   - Send link via WhatsApp
   - Open on mobile browser
   - Should redirect to login page

3. **Verify all features:**
   - Login/Register works
   - Exam taking works
   - Results display correctly
   - Share link tracking works

---

## 🆘 Troubleshooting

### CORS Errors
```
Access to XMLHttpRequest blocked by CORS policy
```
**Fix:** Update `FRONTEND_URL` in backend environment variables

### Share Link Not Working
```
This site can't be reached
```
**Fix:** 
1. Check tunnel is running: `cloudflared tunnel --url http://127.0.0.1:5000`
2. Or deploy to production (recommended)

### Backend Sleeping
```
Application Error
```
**Fix:** Setup UptimeRobot ping every 5 minutes

### Database Issues
**Fix:** Check database path in production. Use absolute path:
```python
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:////opt/render/project/src/exam_portal.db')
```

---

## 📞 Support

For issues:
1. Check Render logs: Dashboard → Logs
2. Check Vercel logs: Dashboard → Functions
3. Enable debug mode temporarily: `FLASK_ENV=development`

---

## ✨ Post-Deployment Checklist

- [ ] Frontend deployed on Vercel/Netlify
- [ ] Backend deployed on Render/Railway
- [ ] Environment variables configured
- [ ] CORS origins set correctly
- [ ] HTTPS working (no mixed content warnings)
- [ ] Share link generates with production URL
- [ ] Mobile responsive on phone
- [ ] Auto-restart configured (UptimeRobot)
- [ ] Admin account created
- [ ] Test share link via WhatsApp

---

**🎉 Your exam portal is now live and accessible 24/7!**
