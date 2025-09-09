# Domain Setup Notes

## ✅ Completed Setup

### Domain: filter-ical.de
- **Purchased at:** Namecheap
- **DNS:** A records pointing to 56.228.25.95
- **SSL Certificate:** Let's Encrypt (auto-renewal enabled)
- **Status:** Live at https://filter-ical.de

### Security Group Configuration
- **Port 22:** SSH access
- **Port 80:** HTTP (redirects to HTTPS)
- **Port 443:** HTTPS with SSL certificate
- **Port 3000:** Application container (internal)

### Production Architecture
- **Location:** `/opt/websites/` on EC2
- **Nginx:** Single reverse proxy handling all domains
- **SSL:** Mounted from host `/etc/letsencrypt/` directory
- **Auto-renewal:** Configured with cron job

## 🚀 Future Additions

### Adding gabs-massage.de
1. Buy domain at Namecheap
2. Set DNS A records to 56.228.25.95
3. Uncomment gabs-massage sections in:
   - `infrastructure/production-docker-compose.yml`
   - `infrastructure/production-nginx.conf`
4. Deploy new image to ECR
5. SSL will be obtained automatically

### Commands for Future Domains
```bash
# Get SSL for new domain
sudo certbot certonly --standalone -d newdomain.com -d www.newdomain.com

# Update nginx and restart
docker-compose restart nginx
```

## 🔧 Troubleshooting

### SSL Issues
- Certificates are in `/etc/letsencrypt/live/`
- Must be mounted into nginx container
- Check with: `docker logs websites-nginx`

### Port Issues
- Check security group allows ports 80, 443
- Test with: `telnet filter-ical.de 80`

### Container Issues
- Check status: `docker-compose ps`
- View logs: `docker logs container-name`
- Health checks use root path `/` not `/health`