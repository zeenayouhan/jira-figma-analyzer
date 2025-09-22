# 🚀 Jira-Figma Analyzer Hosting Guide

This guide covers multiple hosting options for your Jira-Figma Analyzer tool.

## 📋 Prerequisites

- Docker and Docker Compose installed
- API keys (OpenAI, Figma)
- Domain name (for production)

## 🐳 Option 1: Docker Deployment (Recommended)

### Local Testing
```bash
# 1. Clone your repository
git clone <your-repo-url>
cd jira-figma-analyzer

# 2. Set up environment variables
cp .env.production .env
# Edit .env with your API keys

# 3. Deploy
./deploy.sh
```

### Production Deployment
```bash
# 1. Set up your server (Ubuntu/CentOS)
sudo apt update
sudo apt install docker.io docker-compose git

# 2. Clone and deploy
git clone <your-repo-url>
cd jira-figma-analyzer
./deploy.sh
```

## ☁️ Option 2: Cloud Hosting

### AWS EC2
1. **Launch EC2 Instance**
   - Instance Type: t3.medium or larger
   - OS: Ubuntu 20.04 LTS
   - Security Group: Allow HTTP (80), HTTPS (443), SSH (22)

2. **Deploy Application**
   ```bash
   # Connect to your EC2 instance
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Install Docker
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo usermod -aG docker ubuntu
   
   # Deploy app
   git clone <your-repo-url>
   cd jira-figma-analyzer
   ./deploy.sh
   ```

3. **Set up Domain (Optional)**
   - Point your domain to EC2 IP
   - Update nginx.conf with your domain name
   - Add SSL certificates

### Google Cloud Platform
1. **Create VM Instance**
   - Machine Type: e2-medium
   - OS: Ubuntu 20.04 LTS
   - Firewall: Allow HTTP and HTTPS traffic

2. **Deploy with Cloud Run**
   ```bash
   # Build and push to Container Registry
   gcloud builds submit --tag gcr.io/PROJECT-ID/jira-figma-analyzer
   
   # Deploy to Cloud Run
   gcloud run deploy jira-figma-analyzer \
     --image gcr.io/PROJECT-ID/jira-figma-analyzer \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### DigitalOcean
1. **Create Droplet**
   - Image: Ubuntu 20.04 LTS
   - Size: 2GB RAM minimum
   - Add SSH key

2. **Deploy Application**
   ```bash
   # Connect to droplet
   ssh root@your-droplet-ip
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Deploy app
   git clone <your-repo-url>
   cd jira-figma-analyzer
   ./deploy.sh
   ```

## 🔧 Option 3: Platform-as-a-Service (PaaS)

### Heroku
1. **Create Heroku App**
   ```bash
   # Install Heroku CLI
   npm install -g heroku
   
   # Login and create app
   heroku login
   heroku create your-app-name
   ```

2. **Deploy with Heroku**
   ```bash
   # Add Heroku buildpack
   heroku buildpacks:add heroku/python
   
   # Set environment variables
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set FIGMA_ACCESS_TOKEN=your_token
   
   # Deploy
   git push heroku main
   ```

### Railway
1. **Connect GitHub Repository**
   - Go to railway.app
   - Connect your GitHub account
   - Select your repository

2. **Configure Environment**
   - Add environment variables in Railway dashboard
   - Set OPENAI_API_KEY and FIGMA_ACCESS_TOKEN

3. **Deploy**
   - Railway automatically builds and deploys
   - Get your app URL from dashboard

### Render
1. **Create Web Service**
   - Connect GitHub repository
   - Choose "Web Service"
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `streamlit run complete_streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`

2. **Configure Environment**
   - Add environment variables
   - Deploy automatically

## 🔒 Security Considerations

### SSL/HTTPS Setup
```bash
# Using Let's Encrypt (free SSL)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Environment Security
- Never commit .env files to git
- Use environment variables in production
- Rotate API keys regularly
- Enable firewall rules

### Database Security
- Use strong database passwords
- Enable database encryption
- Regular backups

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check application health
curl http://your-domain.com/health

# Check Docker containers
docker-compose ps
docker-compose logs -f
```

### Backup Strategy
```bash
# Backup database
cp ticket_storage.db backups/ticket_storage_$(date +%Y%m%d).db

# Backup analysis outputs
tar -czf backups/analysis_outputs_$(date +%Y%m%d).tar.gz analysis_outputs/
```

### Updates
```bash
# Update application
git pull origin main
docker-compose build
docker-compose up -d
```

## 💰 Cost Estimates

### AWS EC2 (t3.medium)
- **Monthly**: ~$30-50
- **Features**: Full control, scalable

### Google Cloud Run
- **Monthly**: ~$10-20
- **Features**: Serverless, pay-per-use

### DigitalOcean Droplet (2GB)
- **Monthly**: ~$12
- **Features**: Simple, predictable pricing

### Heroku (Basic)
- **Monthly**: ~$7
- **Features**: Easy deployment, limited resources

### Railway
- **Monthly**: ~$5-15
- **Features**: Modern platform, good for startups

## 🚀 Quick Start (Recommended)

For the fastest deployment, use **Railway** or **Render**:

1. **Push your code to GitHub**
2. **Connect to Railway/Render**
3. **Add environment variables**
4. **Deploy automatically**

Your app will be live in minutes!

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Ensure all dependencies are installed
4. Check firewall/security group settings

## 🎯 Next Steps

1. **Choose your hosting option**
2. **Set up your domain (optional)**
3. **Configure SSL certificates**
4. **Set up monitoring**
5. **Create backup strategy**

Happy hosting! 🚀
