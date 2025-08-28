# Troubleshooting 404 Error on Vercel

## Common Causes and Solutions

### 1. **Vercel Configuration Issues**

**Problem**: Incorrect `vercel.json` configuration
**Solution**: Use the updated configuration:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

### 2. **File Structure Issues**

**Problem**: Missing or incorrect file structure
**Solution**: Ensure your project has this structure:

```
Realtime-Style-Transfer/
├── api/
│   ├── index.py          # Main serverless function
│   └── test.py           # Test endpoint
├── templates/
│   └── index.html        # Web interface
├── static/
│   └── styles/           # Style images
├── weights/              # Model files
├── vercel.json           # Vercel configuration
└── requirements_vercel.txt
```

### 3. **Python Runtime Issues**

**Problem**: Vercel can't find the Python runtime
**Solution**: 
- Ensure `requirements_vercel.txt` exists and contains all dependencies
- Check that the Python version is compatible (3.8+ recommended)

### 4. **Deployment Steps**

1. **Commit and push your changes**:
   ```bash
   git add .
   git commit -m "Fix Vercel deployment"
   git push origin main
   ```

2. **Redeploy on Vercel**:
   - Go to your Vercel dashboard
   - Find your project
   - Click "Redeploy" or trigger a new deployment

3. **Check deployment logs**:
   - In Vercel dashboard, go to your project
   - Click on the latest deployment
   - Check the "Functions" tab for any errors

### 5. **Test Your Deployment**

**Test the basic endpoint**:
- Visit: `https://your-app.vercel.app/api/test`
- Should return: `{"message": "Vercel deployment is working!", "status": "success"}`

**Test the main page**:
- Visit: `https://your-app.vercel.app/`
- Should show the web interface

### 6. **Alternative Solutions**

#### Option A: Use Streamlit Cloud (Recommended)
Since your original app is built with Streamlit, this is the best option:

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Deploy the original `app.py`

#### Option B: Simplify Vercel Deployment
If you want to stick with Vercel, use this simplified approach:

1. **Create a minimal `api/index.py`**:
```python
def handler(request):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Style Transfer App</h1><p>Deploy to Streamlit Cloud for full functionality.</p>'
    }
```

2. **Update `vercel.json`**:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ]
}
```

### 7. **Debugging Steps**

1. **Check Vercel logs**:
   - Go to your project in Vercel dashboard
   - Click on "Functions" tab
   - Look for error messages

2. **Test locally**:
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Test locally
   vercel dev
   ```

3. **Check file paths**:
   - Ensure all file paths in your code are correct
   - Use relative paths from the project root

### 8. **Common Error Messages**

- **"Function not found"**: Check `vercel.json` configuration
- **"Module not found"**: Check `requirements_vercel.txt`
- **"File not found"**: Check file paths and structure
- **"Timeout"**: Vercel has 10-second limits on free tier

### 9. **Performance Considerations**

**Vercel Limitations**:
- 10-second timeout on free tier
- Limited memory for ML models
- No persistent storage

**Recommendations**:
- Use Streamlit Cloud for ML applications
- Use Vercel for simple web interfaces
- Consider paid tiers for better performance

### 10. **Final Recommendation**

For your style transfer application, I strongly recommend:

1. **Streamlit Cloud** - Best for the original app with full functionality
2. **Vercel** - Good for a demo/landing page, but limited for ML processing

The 404 error you're experiencing is likely due to Vercel's serverless function structure requirements. The simplified version I've created should resolve this issue.
