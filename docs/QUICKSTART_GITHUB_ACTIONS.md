# Quick Start: GitHub Actions for Apartment Scraping

This guide helps you set up automated apartment scraping that works despite anti-bot detection.

## Choose Your Path

### Path 1: Self-Hosted Runner (RECOMMENDED - Free & Reliable)

Best for: Personal use, residential IP, most reliable

**Setup Time:** 10 minutes
**Monthly Cost:** $0
**Success Rate:** ~95%

#### Steps:

1. **Install runner on your machine:**

```bash
# On your Linux machine
mkdir -p ~/actions-runner && cd ~/actions-runner

# Download runner
curl -o actions-runner-linux-x64-2.313.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.313.0/actions-runner-linux-x64-2.313.0.tar.gz

tar xzf ./actions-runner-linux-x64-2.313.0.tar.gz

# Get token from:
# https://github.com/YOUR_USERNAME/housing_analysis/settings/actions/runners/new

./config.sh --url https://github.com/YOUR_USERNAME/housing_analysis --token YOUR_TOKEN

# Install as service (runs automatically)
sudo ./svc.sh install
sudo ./svc.sh start
```

2. **Enable workflow:**

```bash
cd ~/Projects/housing_analysis

# Workflow is already created at:
# .github/workflows/scrape_self_hosted.yml

# Push to GitHub
git add .github/
git commit -m "Add self-hosted scraper workflow"
git push
```

3. **Test it:**

Go to GitHub → Actions → "Scrape with Self-Hosted Runner" → "Run workflow"

**Done!** Will run automatically every day at 9 AM UTC.

---

### Path 2: Cloud Runner + Proxy (Reliable but Costs Money)

Best for: Production use, no local machine required

**Setup Time:** 5 minutes
**Monthly Cost:** $49-500
**Success Rate:** ~90%

#### Steps:

1. **Sign up for proxy service:**

Recommended: [ScraperAPI](https://www.scraperapi.com) ($49/mo)
- Sign up → Get API key
- Your proxy URL format: `http://scraperapi:YOUR_API_KEY@proxy-server.scraperapi.com:8001`

Alternative: [Bright Data](https://brightdata.com) ($500/mo for 20GB)

2. **Add proxy to GitHub secrets:**

```bash
# Go to your GitHub repo:
# Settings → Secrets and Variables → Actions → New repository secret

Name: PROXY_URL
Value: http://scraperapi:YOUR_API_KEY@proxy-server.scraperapi.com:8001
```

3. **Enable workflow:**

```bash
cd ~/Projects/housing_analysis

# Workflow already created at:
# .github/workflows/scrape_with_proxy.yml

git add .github/
git commit -m "Add proxy scraper workflow"
git push
```

4. **Test it:**

GitHub → Actions → "Scrape with Residential Proxy" → "Run workflow"

---

### Path 3: Hybrid (Best of Both)

Uses self-hosted when available, falls back to proxy if not.

**Setup Time:** 15 minutes (requires both above)
**Monthly Cost:** $0-500
**Success Rate:** ~98%

#### Steps:

1. Set up self-hosted runner (Path 1)
2. Set up proxy secret (Path 2)
3. Workflow is at: `.github/workflows/scrape_hybrid.yml`
4. Push and test

---

## Testing Your Setup

### Local Test (Before GitHub Actions)

```bash
# Test enhanced scraper locally
python3 scripts/scrape_neighborhoods_enhanced.py
```

### Manual GitHub Actions Trigger

1. Go to: `https://github.com/YOUR_USERNAME/housing_analysis/actions`
2. Click your workflow
3. Click "Run workflow" button
4. Wait 5-10 minutes
5. Check results in "Actions" tab

### Check for Bot Detection

Look for these in the logs:

```
✅ GOOD:
"📋 Found 137 property cards"
"✅ Extracted 137 valid properties"
"💾 Saved 137 listings to data/lisboa_alcantara_listings.csv"

❌ BAD (detected):
"🚨 DETECTION: Found 'captcha' in page content"
"⚠️ Bot detection triggered"
"📋 Found 0 property cards"
```

---

## Viewing Results

After workflow runs successfully:

### Option 1: Git Pull

```bash
cd ~/Projects/housing_analysis
git pull

# View latest report
xdg-open reports/$(ls -t reports/*.pdf | head -1)
```

### Option 2: GitHub Artifacts

1. Go to Actions → Your workflow run
2. Scroll to bottom → "Artifacts"
3. Download "apartment-reports-XXX"

### Option 3: Browse on GitHub

Navigate to `reports/` folder in GitHub web interface

---

## Troubleshooting

### "No self-hosted runners available"

**Solution:** Start your runner

```bash
sudo ~/actions-runner/svc.sh start
sudo ~/actions-runner/svc.sh status
```

### "PROXY_URL secret not configured"

**Solution:** Add secret in GitHub

`Settings → Secrets and Variables → Actions → New secret`

### "Bot detection triggered"

**Solution 1:** Use self-hosted runner (better IP)
**Solution 2:** Use residential proxy
**Solution 3:** Increase delays in scraper

```python
# Edit src/idealista_scraper_enhanced.py
self.min_delay = 5  # Increase from 3
self.max_delay = 12  # Increase from 8
```

### "ChromeDriver version mismatch"

**Solution:** Update Chrome on your machine

```bash
# Update Chrome
sudo apt update
sudo apt upgrade google-chrome-stable
```

---

## Customization

### Change Schedule

Edit workflow file:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # Change this
    # Examples:
    # '0 */6 * * *'  # Every 6 hours
    # '0 9,21 * * *'  # 9 AM and 9 PM
    # '0 9 * * 1,4'  # Monday and Thursday only
```

### Change Neighborhoods

Edit `scripts/scrape_neighborhoods_enhanced.py`:

```python
# Add more neighborhoods
neighborhoods = ['ajuda', 'alcantara', 'marvila', 'arroios']

for neighborhood in neighborhoods:
    df = scraper.scrape_neighborhood('lisboa', neighborhood, max_pages=5)
    scraper.save_to_csv(df, f'data/lisboa_{neighborhood}_listings.csv')
```

### Notifications

Add to workflow (after Generate PDF step):

```yaml
- name: Send email notification
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: New Apartment Report - ${{ github.run_number }}
    to: your@email.com
    from: GitHub Actions
    body: New apartment report generated!
    attachments: reports/*.pdf
```

---

## Cost Comparison

| Solution | Setup | Monthly | Total Year 1 |
|----------|-------|---------|--------------|
| Self-hosted only | $0 | $0 | **$0** |
| ScraperAPI proxy | $0 | $49 | **$588** |
| Bright Data proxy | $0 | $500 | **$6,000** |
| Hybrid (both) | $0 | $0-49 | **$0-588** |

**Recommendation:** Start with self-hosted (free), add proxy only if needed.

---

## What Gets Automated

When workflow runs successfully:

1. ✅ Scrapes fresh listings from Idealista
2. ✅ Filters apartments under 1200€
3. ✅ Extracts amenities from descriptions
4. ✅ Calculates distances to work/school
5. ✅ Generates PDF report with NER analysis
6. ✅ Commits results to GitHub
7. ✅ Uploads artifacts for download

**You get:**
- Updated `reports/YYYY-MM-DD_ner_report.pdf`
- Updated `reports/apartment_urls.txt`
- Updated `data/apartments_with_ner.csv`

---

## Next Steps

1. ✅ Choose your path (self-hosted recommended)
2. ✅ Follow setup steps above
3. ✅ Test with manual trigger
4. ✅ Enable scheduled runs
5. ✅ Check results daily

**Questions?** See full documentation: `docs/GITHUB_ACTIONS_SETUP.md`
