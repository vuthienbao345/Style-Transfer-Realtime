# Deployment Guide for Realtime Style Transfer

This guide provides multiple deployment options for your Realtime Style Transfer application.

## Option 1: Streamlit Cloud (Recommended for Streamlit Apps)

Since your original app is built with Streamlit, this is the most suitable platform.

### Steps:
1. **Push your code to GitHub** (if not already done)
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Sign in with GitHub**
4. **Connect your repository**
5. **Deploy**

### Advantages:
- ✅ Native Streamlit support
- ✅ Free tier available
- ✅ Easy deployment
- ✅ Automatic updates from GitHub

## Option 2: Vercel Deployment (Flask Version)

I've created a Flask version of your app that's compatible with Vercel.

### Prerequisites:
- GitHub account
- Vercel account (free at [vercel.com](https://vercel.com))

### Steps:

1. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

2. **Deploy via Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the Python project
   - Deploy

3. **Or deploy via CLI**:
   ```bash
   vercel
   ```

### Files Created for Vercel:
- `app_flask.py` - Flask version of your app
- `templates/index.html` - Modern web interface
- `vercel.json` - Vercel configuration
- `requirements_vercel.txt` - Python dependencies
- `static/` - Static assets (style images)

### Important Notes:
- The Flask version supports image processing only (no video)
- Model files must be in the `weights/` directory
- Static files are served from the `static/` directory

## Option 3: Heroku Deployment

### Steps:
1. **Install Heroku CLI**
2. **Create `Procfile`**:
   ```
   web: gunicorn app_flask:app
   ```
3. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## Option 4: Local Development

### Run Streamlit Version:
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Run Flask Version:
```bash
pip install -r requirements_vercel.txt
python app_flask.py
```

## File Structure After Conversion:

```
Realtime-Style-Transfer/
├── app.py                    # Original Streamlit app
├── app_flask.py             # Flask version for Vercel
├── templates/
│   └── index.html           # Web interface
├── static/
│   └── styles/              # Style images
├── weights/                 # Model files
├── resources/               # Original resources
├── vercel.json             # Vercel configuration
├── requirements.txt         # Original requirements
├── requirements_vercel.txt  # Vercel requirements
└── DEPLOYMENT_GUIDE.md     # This file
```

## Troubleshooting

### Common Issues:

1. **Model files not found**:
   - Ensure `weights/` directory contains all `.pth` files
   - Check file paths in the code

2. **Memory issues on Vercel**:
   - Vercel has memory limits for serverless functions
   - Consider using Streamlit Cloud for better performance

3. **Static files not loading**:
   - Verify files are in the `static/` directory
   - Check the static file route in `app_flask.py`

### Performance Considerations:

- **Vercel**: Limited by serverless function timeout (10s for hobby plan)
- **Streamlit Cloud**: Better for ML applications with longer processing times
- **Local**: Best performance for development and testing

## Recommendation

For your style transfer application, I recommend:

1. **Streamlit Cloud** - Best for the original Streamlit app
2. **Vercel** - Good for the web interface version (image processing only)
3. **Local** - Best for development and testing

Choose based on your specific needs and performance requirements!
