# 🚀 Quick Deploy - 3 Steps to Production

## ⚡ TL;DR - Deploy in 5 Minutes

### Step 1: Backend on Render
```bash
# Push to GitHub first
git init
git add .
git commit -m "Production ready"
git remote add origin https://github.com/YOUR_USERNAME/exam-portal.git
git push -u origin main

# Then go to https://dashboard.render.com/
# New Web Service → Connect GitHub → Use these settings:
```
**Render Settings:**
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
- Env vars: `SECRET_KEY` (generate random), `FRONTEND_URL` (your Vercel URL)

### Step 2: Frontend on Vercel
```bash
cd frontend
npm install
npm run build
```
**Vercel Settings:**
- Framework: Vite
- Root: `frontend`
- Build: `npm run build`
- Output: `dist`
- Env: `VITE_API_URL` (your Render URL)

### Step 3: Test & Share
1. Visit your Vercel URL
2. Login as admin
3. Generate share link
4. Share via WhatsApp
5. Done! 🎉

---

## 📱 Share Link Structure (24/7 Working)

```
User clicks in WhatsApp
    ↓
https://exam-portal.vercel.app/join/{token}
    ↓
Validates (30 days expiry)
    ↓
Redirects to login
    ↓
User logs in → Dashboard
```

**URL Format:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-api.onrender.com`
- Share Link: `https://your-app.vercel.app/join/{32-char-token}`

---

## 🔧 Files Created

### Backend (`/exam-portal/`)
| File | Purpose |
|------|---------|
| `app.py` | Flask app with CORS, API routes |
| `render.yaml` | Render deployment config |
| `requirements.txt` | Python dependencies |
| `DEPLOYMENT.md` | Full deployment guide |

### Frontend (`/exam-portal/frontend/`)
| File | Purpose |
|------|---------|
| `src/config/api.js` | Environment-based API URLs |
| `src/store/authStore.js` | Authentication state |
| `src/pages/Login.jsx` | Mobile-optimized login |
| `src/pages/ShareJoin.jsx` | Share link handler |
| `vercel.json` | Vercel deployment config |
| `vite.config.js` | Build configuration |

---

## ✨ Key Features

- ✅ **Public URL** - No more localhost
- ✅ **HTTPS Only** - Secure connections
- ✅ **CORS Enabled** - Frontend ↔ Backend communication
- ✅ **Mobile First** - Works perfectly on phones
- ✅ **24/7 Uptime** - No sleep mode (with UptimeRobot)
- ✅ **30-Day Links** - Share links valid for 30 days
- ✅ **Auto-Redirect** - Unauthenticated → Login page

---

## 🆘 Common Issues

**CORS Error?**
→ Update `FRONTEND_URL` in Render environment variables

**Backend Sleeping?**
→ Use UptimeRobot to ping every 5 minutes (free)

**Link Not Working?**
→ Make sure both frontend and backend are deployed

**Build Fails?**
→ Check `vite.config.js` has correct API URL

---

## 📞 Admin Credentials (Default)
- Username: `tulasi`
- Password: `tulasi@2005`

**Change in production!**

---

Your exam portal is now ready for real-world use! 🎓
