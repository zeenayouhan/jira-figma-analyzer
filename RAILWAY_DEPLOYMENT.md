# 🚀 Railway Deployment Guide

## Quick Deploy to Railway

### Step 1: Prepare Your Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect Python and use the configuration

### Step 3: Set Environment Variables
In your Railway project dashboard:
1. Go to "Variables" tab
2. Add these environment variables:
   - `OPENAI_API_KEY` = `your_openai_api_key_here`
   - `FIGMA_ACCESS_TOKEN` = `your_figma_token_here`

### Step 4: Deploy
1. Railway will automatically build and deploy
2. Your app will be available at the provided URL
3. Check logs if there are any issues

## Configuration Files Created

- `railway.json` - Railway-specific configuration
- `Procfile` - Process definition
- `nixpacks.toml` - Build configuration
- `start.py` - Startup script
- `requirements-railway.txt` - Optimized dependencies

## Troubleshooting

### If Build Fails:
1. Check the build logs in Railway dashboard
2. Ensure all dependencies are in requirements.txt
3. Verify Python version compatibility

### If App Doesn't Start:
1. Check the start command in railway.json
2. Verify environment variables are set
3. Check the logs for error messages

### Common Issues:
- **Port binding**: Railway uses $PORT environment variable
- **Dependencies**: Some packages might need system dependencies
- **Memory**: Streamlit can be memory-intensive

## Monitoring

- View logs in Railway dashboard
- Monitor resource usage
- Set up alerts for downtime

## Custom Domain (Optional)

1. Go to "Settings" in your Railway project
2. Add custom domain
3. Configure DNS records
4. Enable HTTPS

Your Jira-Figma Analyzer will be live at your custom domain!

## Cost

Railway offers:
- Free tier: $5 credit monthly
- Pro plan: $20/month for production use
- Pay-as-you-go for additional usage

Perfect for testing and small to medium production workloads!
