# Traffic Sign ML Backend - Render Deployment Guide

Your backend is fully prepared for a production cloud deployment. All dependencies, files, and environment variables are self-contained.

## How to Deploy (100% Free)

1. **Upload to GitHub:**
   - Create a new free repository on [GitHub](https://github.com/new).
   - Drag and drop **ONLY the contents of this `backend/` folder** into it.

2. **Deploy to Render:**
   - Go to [Render.com](https://render.com) and create a free account.
   - Click **New** -> **Web Service**.
   - Connect your GitHub account and select your new repository.

3. **Configure Render Settings:**
   - Name: `traffic-ai-backend` (or whatever you want)
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --workers 1 --threads 1 --timeout 120`

4. **Environment Variables:**
   - Scroll down to "Environment Variables" and click "Add from .env".
   - Simply copy and paste the contents of the `.env` file in this folder into the text box.

5. **Deploy!**
   - Click "Create Web Service". 
   - Render will build the environment and give you a public URL (e.g., `https://traffic-ai.onrender.com`).

## Final Step (Connecting the Frontend)
Once you have your Render URL, go back to your `frontend/.env` file and change `NEXT_PUBLIC_API_URL` to point to it:
```ini
NEXT_PUBLIC_API_URL=https://traffic-ai.onrender.com/predict
```
Then, deploy your Frontend to InsForge again, and your app will work on every phone on Earth!
