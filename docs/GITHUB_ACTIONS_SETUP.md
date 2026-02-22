# GitHub Actions Setup for Idealista Scraper

## Problem: Bot Detection in Cloud Runners

GitHub's cloud runners face several anti-bot challenges:
- Datacenter IPs (easily flagged)
- Headless browser detection
- Container fingerprinting
- CAPTCHA challenges

## Solutions (Ranked by Reliability)

---

## Solution 1: Self-Hosted Runner (RECOMMENDED)

Run GitHub Actions on your own machine with residential IP.

### Advantages
✅ Uses your residential IP address
✅ Can run non-headless browser
✅ Bypasses datacenter IP blocks
✅ Free (no proxy costs)
✅ Most reliable for anti-bot

### Setup Steps

#### 1. Install Self-Hosted Runner on Your Machine

```bash
# Create a directory for the runner
mkdir -p ~/actions-runner && cd ~/actions-runner

# Download the latest runner (Linux x64)
curl -o actions-runner-linux-x64-2.313.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.313.0/actions-runner-linux-x64-2.313.0.tar.gz

# Extract the installer
tar xzf ./actions-runner-linux-x64-2.313.0.tar.gz

# Configure the runner (follow prompts)
./config.sh --url https://github.com/YOUR_USERNAME/housing_analysis --token YOUR_TOKEN

# Install as a service (runs on boot)
sudo ./svc.sh install
sudo ./svc.sh start
```

**Get your token from:**
`https://github.com/YOUR_USERNAME/housing_analysis/settings/actions/runners/new`

#### 2. Create GitHub Actions Workflow

Create `.github/workflows/scrape_daily.yml`:

```yaml
name: Daily Apartment Scraper

on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM UTC daily
  workflow_dispatch:  # Allow manual trigger

jobs:
  scrape-and-analyze:
    runs-on: self-hosted  # Use YOUR machine

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip3 install --break-system-packages -r requirements.txt

      - name: Run scraper (non-headless)
        run: python3 scripts/scrape_neighborhoods.py
        env:
          DISPLAY: :0  # Use your display for non-headless mode

      - name: Filter apartments
        run: python3 scripts/filter_and_analyze.py

      - name: Parse amenities
        run: python3 scripts/parse_descriptions.py

      - name: Calculate distances
        run: python3 scripts/rank_by_distance.py

      - name: Generate PDF report
        run: python3 scripts/generate_pdf_report.py

      - name: Commit updated data
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add data/*.csv reports/*.pdf reports/*.txt
          git diff --quiet && git diff --staged --quiet || \
            git commit -m "Auto-update apartment data $(date +'%Y-%m-%d')"
          git push
```

#### 3. Keep Runner Active

```bash
# Check runner status
sudo ~/actions-runner/svc.sh status

# View runner logs
journalctl -u actions.runner.* -f
```

**Power Management:**
If using a laptop/desktop, disable sleep:
```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

---

## Solution 2: Residential Proxy Service

Use a proxy with residential IPs in GitHub cloud runners.

### Recommended Services
- **Bright Data** (formerly Luminati) - $500/mo for 20GB
- **ScraperAPI** - $49/mo for 100k requests
- **Oxylabs** - $300/mo for residential proxies

### Implementation

Create `src/idealista_scraper_proxy.py`:

```python
import undetected_chromedriver as uc
from selenium.webdriver.common.proxy import Proxy, ProxyType
import os

class IdealistaScraperWithProxy:
    def __init__(self, headless=True):
        # Get proxy from environment variable
        proxy_url = os.getenv('PROXY_URL')  # format: "http://user:pass@proxy:port"

        options = uc.ChromeOptions()

        if proxy_url:
            # Configure proxy
            options.add_argument(f'--proxy-server={proxy_url}')

        if headless:
            options.add_argument('--headless=new')

        # Anti-detection arguments
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')

        # Randomize user agent
        user_agents = [
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        import random
        options.add_argument(f'user-agent={random.choice(user_agents)}')

        self.driver = uc.Chrome(options=options, version_main=143)
        self.driver.implicitly_wait(10)
```

**GitHub Actions with Proxy:**

```yaml
jobs:
  scrape-with-proxy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Chrome
        uses: browser-actions/setup-chrome@latest

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run scraper with proxy
        env:
          PROXY_URL: ${{ secrets.PROXY_URL }}  # Add to repo secrets
        run: python3 scripts/scrape_neighborhoods.py
```

**Add to GitHub Secrets:**
- Go to: `Settings → Secrets and Variables → Actions`
- Add: `PROXY_URL` = `http://username:password@proxy.brightdata.com:22225`

---

## Solution 3: Advanced Anti-Detection (No Proxy)

Enhance the scraper with maximum stealth - may still fail occasionally.

### Enhanced Configuration

```python
import undetected_chromedriver as uc
from selenium_stealth import stealth
import random
import time

class StealthScraper:
    def __init__(self, headless=True):
        options = uc.ChromeOptions()

        # Headless mode
        if headless:
            options.add_argument('--headless=new')

        # Anti-detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-extensions')

        # Randomize window size
        widths = [1366, 1920, 1440, 1536]
        heights = [768, 1080, 900, 864]
        options.add_argument(f'--window-size={random.choice(widths)},{random.choice(heights)}')

        # Randomize user agent
        user_agents = [
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')

        # Initialize driver
        self.driver = uc.Chrome(options=options, use_subprocess=True)

        # Apply stealth techniques
        stealth(self.driver,
                languages=["en-US", "en", "pt-PT", "pt"],
                vendor="Google Inc.",
                platform="Linux",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)

        # Random delays
        self.min_delay = 3
        self.max_delay = 8

    def random_sleep(self):
        time.sleep(random.uniform(self.min_delay, self.max_delay))

    def human_like_scroll(self):
        """Simulate human scrolling behavior"""
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = 0

        while current_position < scroll_height:
            # Random scroll amount
            scroll_by = random.randint(100, 300)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_by});")
            current_position += scroll_by

            # Random pause
            time.sleep(random.uniform(0.1, 0.5))
```

**Install selenium-stealth:**
```bash
pip install selenium-stealth
```

**Update requirements.txt:**
```
selenium-stealth==1.0.6
```

---

## Solution 4: Hybrid Approach (Best Balance)

Combine self-hosted runner with fallback to proxy.

```yaml
name: Smart Scraper

on:
  schedule:
    - cron: '0 9 * * *'
  workflow_dispatch:

jobs:
  # Try self-hosted first
  scrape-self-hosted:
    runs-on: self-hosted
    continue-on-error: true
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v3
      - run: python3 scripts/scrape_neighborhoods.py

  # Fallback to proxy if self-hosted fails
  scrape-with-proxy:
    runs-on: ubuntu-latest
    needs: scrape-self-hosted
    if: failure()

    steps:
      - uses: actions/checkout@v3
      - name: Run with proxy
        env:
          PROXY_URL: ${{ secrets.PROXY_URL }}
        run: python3 scripts/scrape_neighborhoods.py
```

---

## Comparison Table

| Solution | Reliability | Cost | Setup Complexity | Maintenance |
|----------|------------|------|------------------|-------------|
| Self-hosted runner | ⭐⭐⭐⭐⭐ | Free | Medium | Low |
| Residential proxy | ⭐⭐⭐⭐ | $50-500/mo | Low | Very Low |
| Advanced anti-detection | ⭐⭐ | Free | High | High |
| Hybrid | ⭐⭐⭐⭐⭐ | $0-500/mo | Medium | Low |

---

## Recommendations

1. **For personal use:** Self-hosted runner (most cost-effective)
2. **For production:** Residential proxy service (most reliable)
3. **For testing:** Advanced anti-detection (free but unreliable)
4. **For critical operations:** Hybrid approach (best of both worlds)

---

## Monitoring & Debugging

### Check if Scraper is Detected

Add detection check to scraper:

```python
def check_if_detected(self):
    """Check if we're blocked by anti-bot"""
    page_source = self.driver.page_source.lower()

    # Check for common blocking patterns
    blocked_keywords = [
        'captcha',
        'blocked',
        'access denied',
        'robot',
        'automated access',
        'unusual traffic'
    ]

    for keyword in blocked_keywords:
        if keyword in page_source:
            print(f"⚠️ DETECTION WARNING: Found '{keyword}' in page")
            return True

    return False
```

### GitHub Actions Notifications

Get notified when scraper fails:

```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Scraper failed - possible bot detection'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Next Steps

1. Choose solution based on your budget and requirements
2. Set up self-hosted runner (recommended for personal use)
3. Test with manual workflow trigger
4. Monitor for detection and adjust as needed
5. Consider adding proxy as fallback

---

## Additional Resources

- [GitHub Self-Hosted Runners Docs](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Bright Data Residential Proxies](https://brightdata.com/products/residential-proxies)
- [ScraperAPI Documentation](https://www.scraperapi.com/documentation/)
