# Deployment Guide for Style Transfer App

## 🚀 Recommended Deployment Options

### Option 1: Streamlit Cloud (Recommended)
Streamlit Cloud is the best platform for deploying Streamlit applications.

**Steps:**
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Select your repository
5. Set the main file path to `app.py`
6. Deploy!

**Advantages:**
- Native Streamlit support
- Free tier available
- Automatic deployments from GitHub
- Built-in caching and performance optimizations

### Option 2: Heroku
Heroku supports Python applications well.

**Steps:**
1. Create a `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Install Heroku CLI
3. Run: `heroku create your-app-name`
4. Run: `git push heroku main`

### Option 3: Railway
Railway is a modern alternative to Heroku.

**Steps:**
1. Connect your GitHub repository
2. Set the start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
3. Deploy!

### Option 4: Google Cloud Run
For more control and scalability.

**Steps:**
1. Create a `Dockerfile`
2. Build and push to Google Container Registry
3. Deploy to Cloud Run

## ⚠️ Important Considerations

### Model Files
Your app uses pre-trained models in the `weights/` directory. Make sure these are included in your repository or downloaded during deployment.

### Dependencies
The `requirements.txt` file includes heavy ML libraries (PyTorch, OpenCV). Consider:
- Using CPU-only versions for faster deployment
- Optimizing model sizes
- Using model caching

### File Upload Limits
Your app handles video uploads. Be aware of:
- Platform file size limits
- Processing time limits
- Memory constraints

## 🔧 Configuration Files

### For Streamlit Cloud
No additional configuration needed - just deploy!

### For Heroku/Railway
Create a `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### For Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

## 🎯 Quick Start with Streamlit Cloud

1. **Prepare your repository:**
   - Ensure all files are committed to GitHub
   - Make sure `app.py` is in the root directory
   - Verify `requirements.txt` is up to date

2. **Deploy:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Click "Deploy"

3. **Monitor:**
   - Check the deployment logs for any issues
   - Test the application functionality
   - Monitor resource usage

## 💡 Optimization Tips

1. **Reduce model size:** Consider using smaller, optimized models
2. **Add caching:** Use `@st.cache_data` for expensive operations
3. **Optimize imports:** Only import what you need
4. **Use CPU-only PyTorch:** Faster deployment, smaller size
5. **Add error handling:** Graceful degradation for edge cases

## 🆘 Troubleshooting

### Common Issues:
- **Memory errors:** Reduce batch sizes or model complexity
- **Timeout errors:** Add progress indicators and optimize processing
- **Import errors:** Check all dependencies are in `requirements.txt`
- **File not found:** Ensure all assets are in the correct paths

### Getting Help:
- Check Streamlit documentation
- Review deployment platform logs
- Test locally first with `streamlit run app.py`
