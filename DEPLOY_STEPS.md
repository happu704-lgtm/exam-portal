# 🚀 Step-by-Step Deployment Guide

## 📋 Prerequisites
- GitHub account (free)
- Render account (free)
- Vercel account (free)

---

## PART 1: Deploy Backend to Render (24/7 API)

### Step 1: Push Code to GitHub

```bash
# Open terminal in exam-portal folder
cd exam-portal

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Exam portal ready for deployment"

# Create GitHub repo (go to github.com/new, name: exam-portal)
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/exam-portal.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render

1. Go to **https://dashboard.render.com/**
2. Click **"New +"** → **"Web Service"**
3. Connect your **GitHub** account
4. Select **exam-portal** repository
5. Configure:

| Setting | Value |
|---------|-------|
| **Name** | exam-portal-api |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2` |
| **Plan** | Free |

6. Click **"Advanced"** and add Environment Variables:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | `exam-portal-secret-key-2026` (or random string) |
| `FRONTEND_URL` | `https://exam-portal.vercel.app` (we'll update this after Vercel deploy) |
| `APP_URL` | `https://exam-portal-api.onrender.com` |
| `FLASK_ENV` | `production` |

7. Click **"Create Web Service"**

8. Wait 2-3 minutes for deployment

9. **Copy your Render URL** (e.g., `https://exam-portal-api.onrender.com`)

---

## PART 2: Deploy Frontend to Vercel

### Step 3: Deploy Frontend

1. Go to **https://vercel.com/**
2. Click **"Add New Project"**
3. Import your **exam-portal** GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

5. Click **"Environment Variables"** and add:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://exam-portal-api.onrender.com` (your Render URL) |

6. Click **"Deploy"**

7. Wait 1-2 minutes for deployment

8. **Copy your Vercel URL** (e.g., `https://exam-portal.vercel.app`)

---

## PART 3: Connect Backend & Frontend

### Step 4: Update Render with Frontend URL

1. Go back to **https://dashboard.render.com/**
2. Click on **exam-portal-api** service
3. Click **"Environment"** tab
4. Update `FRONTEND_URL` to your actual Vercel URL:
   - Value: `https://exam-portal.vercel.app`
5. Click **"Save Changes"**
6. Service will auto-redeploy

---

## ✅ Testing Your Deployment

### Test Backend:
Open: `https://exam-portal-api.onrender.com`

Should show: "Digital Quiz Tool API is running"

### Test Frontend:
Open: `https://exam-portal.vercel.app`

Should show: Login page

### Test Share Link:
1. Login as admin (tulasi / tulasi@2005)
2. Generate share link
3. Copy link (should be: `https://exam-portal.vercel.app/join/...`)
4. Open in new tab/private window
5. Should redirect to login
6. Login as student → Should see dashboard

---

## 🆘 Troubleshooting

**Backend shows "Application Error"?**
→ Check Render logs (Dashboard → exam-portal-api → Logs)

**Frontend shows "Cannot connect to backend"?**
→ Check `VITE_API_URL` matches your Render URL exactly

**CORS errors in browser console?**
→ Update `FRONTEND_URL` in Render to match your Vercel URL exactly

**Database not saving data?**
→ Free tier restarts daily - data persists but app sleeps after 15 min inactivity. Use UptimeRobot (below) to keep it awake.

---

## 🔔 Keep Backend Awake (24/7)

Free Render tier sleeps after 15 min inactivity. To keep it awake:

1. Go to **https://uptimerobot.com/**
2. Sign up for free account
3. Click **"Add New Monitor"**
4. Configure:
   - Type: HTTP(s)
   - URL: `https://exam-portal-api.onrender.com`
   - Interval: 5 minutes
5. Click **"Create Monitor"**

Now your backend stays awake 24/7!

---

## 📱 Share Link Format

After deployment:
- **Local testing**: `http://localhost:5000/join/{token}`
- **Production**: `https://exam-portal.vercel.app/join/{token}`

Share via WhatsApp - works on mobile & desktop!

---

## 🎓 Admin Credentials
- Username: `tulasi`
- Password: `tulasi@2005`

**Change in production by logging in and updating password!**

---

## ✨ Summary

| Component | URL | Platform |
|-----------|-----|----------|
| Frontend | `https://exam-portal.vercel.app` | Vercel |
| Backend API | `https://exam-portal-api.onrender.com` | Render |
| Share Links | `https://exam-portal.vercel.app/join/{token}` | Vercel |

**Your app is now live 24/7!** 🎉
