# 🌐 Domain Buying Guide - Under 10€ Options

## 🏆 **Best Options for .de Domains Under 10€**

### **1. Namecheap (Recommended) 💯**
- **Price**: ~3-5€ first year for .de domains
- **Pros**: 
  ✅ Cheapest reliable option
  ✅ Free WHOIS privacy
  ✅ Great DNS management interface
  ✅ No hidden fees
- **Cons**: ❌ Renewal price higher (but you can transfer)
- **Link**: https://www.namecheap.com

### **2. Porkbun (Great Alternative) 🐷**
- **Price**: ~4-6€ first year 
- **Pros**:
  ✅ Very cheap renewals too
  ✅ Free SSL certificates
  ✅ Simple interface
  ✅ No upselling
- **Cons**: ❌ Less well-known
- **Link**: https://porkbun.com

### **3. Cloudflare Registrar (If Available) ☁️**
- **Price**: ~7-9€ (at-cost pricing)
- **Pros**:
  ✅ No markup - pure registry cost
  ✅ Best DNS performance globally
  ✅ Integrated with their services
- **Cons**: ❌ Invite-only (but getting more open)

### **4. AWS Route 53 (Not Recommended for Purchase) ⚠️**
- **Price**: ~12-15€ first year
- **Pros**: ✅ Integrated with AWS
- **Cons**: 
  ❌ More expensive
  ❌ Complex for simple use
  ❌ Over your budget

## 🎯 **Recommended: Namecheap Process**

### **Step 1: Buy Domain**
1. Go to https://namecheap.com
2. Search for "filter-ical.de"
3. Add to cart (~3-5€)
4. **IMPORTANT**: Enable WhoisGuard (free)
5. Complete purchase

### **Step 2: Configure DNS (Immediately After Purchase)**
1. Login to Namecheap dashboard
2. Go to "Domain List" → Click "Manage" next to filter-ical.de
3. Go to "Advanced DNS" tab
4. Delete all existing records
5. Add these records:

```
Type: A Record
Host: @
Value: 56.228.25.95
TTL: Automatic

Type: A Record  
Host: www
Value: 56.228.25.95
TTL: Automatic

Type: CNAME Record
Host: *
Value: filter-ical.de
TTL: Automatic
```

### **Step 3: Wait for Propagation**
- **Time**: 5-30 minutes usually
- **Test**: `ping filter-ical.de` should return 56.228.25.95

## 🔧 **Using Your Domain (Technical Setup)**

### **After DNS Propagation:**

#### **1. Test Domain Points to Your Server**
```bash
# Should return your EC2 IP
dig filter-ical.de +short

# Should show your current app
curl http://filter-ical.de
```

#### **2. Get SSL Certificate**
```bash
# SSH to your EC2
ssh ec2-user@56.228.25.95

# Install certbot if not already installed
sudo yum update
sudo yum install certbot python3-certbot-nginx

# Get certificate for your domain
sudo certbot --nginx -d filter-ical.de -d www.filter-ical.de
```

#### **3. Update Nginx Configuration**
I'll help you switch to the domain-based nginx config that's ready in your repo.

## 📋 **Complete Domain Setup Checklist**

### **Pre-Purchase:**
- [ ] Decide on domain name (filter-ical.de)
- [ ] Choose registrar (Namecheap recommended)
- [ ] Have payment method ready

### **Purchase Process:**
- [ ] Buy domain at Namecheap
- [ ] Enable WhoisGuard privacy
- [ ] Access DNS management

### **DNS Configuration:**
- [ ] Add A record: @ → 56.228.25.95
- [ ] Add A record: www → 56.228.25.95
- [ ] Test DNS propagation

### **Server Configuration:**
- [ ] Test domain points to server
- [ ] Get SSL certificate with certbot
- [ ] Switch to domain-based nginx config
- [ ] Test HTTPS works

### **Final Testing:**
- [ ] https://filter-ical.de loads your app
- [ ] https://www.filter-ical.de works
- [ ] SSL certificate shows as valid

## 🚫 **Avoid These Registrars:**

### **❌ GoDaddy**
- Expensive
- Aggressive upselling
- Complex cancellation

### **❌ 1&1/IONOS**
- Hidden fees
- Poor customer service
- Difficult DNS management

### **❌ Domain.com**
- Expensive renewals
- Pushy sales tactics

## 💡 **Pro Tips:**

### **1. Domain Name Strategy**
- **filter-ical.de** is perfect for your iCal app
- **Short & memorable** 
- **Matches your service** clearly

### **2. Renewal Strategy**
- Set calendar reminder before renewal
- Consider transferring after year 1 if renewal price jumps
- Many registrars offer lower renewal if you threaten to leave

### **3. DNS Management**
- Use the registrar's DNS initially (simple)
- Later you can switch to Cloudflare DNS (faster, free)
- Keep DNS simple - don't overcomplicate

## 🔄 **Migration Timeline**

### **Today:**
1. Buy filter-ical.de at Namecheap (~5€)
2. Set DNS records
3. Wait for propagation (30 minutes)

### **After Propagation:**
1. Test domain points to your server
2. Get SSL certificate
3. Switch nginx to domain config
4. Test everything works

### **Total Time**: 1-2 hours
### **Total Cost**: ~5€ for first year

---

**Ready to buy the domain? I recommend starting with Namecheap - it's the most straightforward and cheapest option!**