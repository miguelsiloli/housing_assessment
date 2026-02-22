"""
Enhanced Idealista Scraper with Advanced Anti-Detection
Supports proxies, better fingerprinting, and stealth mode
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
import random
import os
from typing import List, Dict, Optional


class EnhancedIdealistaScraper:
    """
    Enhanced scraper with anti-bot detection features:
    - Proxy support
    - User agent rotation
    - Random delays
    - Human-like scrolling
    - Detection monitoring
    """

    def __init__(self, headless: bool = False, proxy_url: Optional[str] = None):
        """
        Initialize Enhanced Scraper

        Args:
            headless: Run in headless mode
            proxy_url: Proxy URL (format: http://user:pass@host:port or from env PROXY_URL)
        """
        self.base_url = "https://www.idealista.pt"

        # Get proxy from parameter or environment
        self.proxy_url = proxy_url or os.getenv('PROXY_URL')

        # Setup Chrome options
        options = uc.ChromeOptions()

        # Proxy configuration
        if self.proxy_url:
            print(f"🔒 Using proxy: {self.proxy_url.split('@')[-1] if '@' in self.proxy_url else self.proxy_url}")
            options.add_argument(f'--proxy-server={self.proxy_url}')

        # Headless mode
        if headless:
            options.add_argument('--headless=new')
            print("👻 Running in headless mode")

        # Anti-detection arguments
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')

        # Randomize window size
        window_sizes = [
            (1366, 768),
            (1920, 1080),
            (1440, 900),
            (1536, 864),
            (1280, 720)
        ]
        width, height = random.choice(window_sizes)
        options.add_argument(f'--window-size={width},{height}')
        print(f"🖥️  Window size: {width}x{height}")

        # Randomize user agent
        user_agents = [
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        selected_ua = random.choice(user_agents)
        options.add_argument(f'user-agent={selected_ua}')
        print(f"🎭 User agent: {selected_ua[:50]}...")

        # Language preferences (Portuguese + English)
        options.add_argument('--lang=pt-PT,pt,en-US,en')

        # Initialize driver
        print("🚀 Initializing Chrome driver...")
        try:
            self.driver = uc.Chrome(options=options, version_main=143, use_subprocess=True)
            self.driver.implicitly_wait(10)

            # Override navigator properties to hide automation
            try:
                self.driver.execute_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
            except Exception:
                pass  # Some versions don't support this

        except Exception as e:
            print(f"❌ Failed to initialize driver: {e}")
            raise

        # Random delay ranges (in seconds)
        self.min_delay = 3
        self.max_delay = 8
        self.min_scroll_delay = 0.2
        self.max_scroll_delay = 0.7

        # Visit homepage first to establish session
        print("🏠 Establishing session...")
        self.driver.get(self.base_url)
        self._random_sleep(3, 5)

        # Check if blocked on homepage
        if self._check_if_detected():
            print("⚠️ WARNING: Possible detection on homepage!")

    def _random_sleep(self, min_sec: float = None, max_sec: float = None):
        """Sleep for random duration"""
        min_sec = min_sec or self.min_delay
        max_sec = max_sec or self.max_delay
        duration = random.uniform(min_sec, max_sec)
        time.sleep(duration)

    def _human_like_scroll(self):
        """Simulate human-like scrolling behavior"""
        try:
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            current_position = 0

            # Scroll in random chunks
            while current_position < scroll_height:
                # Random scroll amount (100-400px)
                scroll_by = random.randint(100, 400)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_by});")
                current_position += scroll_by

                # Random pause between scrolls
                time.sleep(random.uniform(self.min_scroll_delay, self.max_scroll_delay))

                # Sometimes scroll back up a bit (like humans do)
                if random.random() < 0.1:  # 10% chance
                    self.driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 150)});")
                    time.sleep(random.uniform(0.1, 0.3))
        except Exception as e:
            print(f"⚠️ Scroll error: {e}")

    def _check_if_detected(self) -> bool:
        """Check if we've been detected/blocked by anti-bot"""
        try:
            page_source = self.driver.page_source.lower()

            # Check for common blocking patterns
            blocked_keywords = [
                'captcha',
                'recaptcha',
                'blocked',
                'access denied',
                'robot',
                'automated access',
                'unusual traffic',
                'verificação',
                'bloqueado'
            ]

            for keyword in blocked_keywords:
                if keyword in page_source:
                    print(f"🚨 DETECTION: Found '{keyword}' in page content")
                    return True

            # Check if page is suspiciously empty
            if len(page_source) < 1000:
                print("🚨 DETECTION: Page content suspiciously short")
                return True

            return False

        except Exception as e:
            print(f"⚠️ Detection check error: {e}")
            return False

    def _mouse_movement_simulation(self):
        """Simulate random mouse movement (helps with some anti-bot systems)"""
        try:
            # Move to random element on page
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a, button, div")
            if elements:
                random_element = random.choice(elements[:20])  # Only first 20 to avoid hidden elements
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.move_to_element(random_element).perform()
                time.sleep(random.uniform(0.1, 0.3))
        except Exception:
            pass  # Silently fail - not critical

    def scrape_search_page(self, url: str) -> List[Dict]:
        """
        Scrape a single search results page with anti-detection measures

        Args:
            url: Full Idealista search URL

        Returns:
            List of property dictionaries
        """
        try:
            print(f"🔍 Loading: {url}")
            self.driver.get(url)

            # Random wait for page load
            self._random_sleep(5, 10)

            # Human-like behavior
            self._human_like_scroll()
            self._mouse_movement_simulation()

            # Check for detection
            if self._check_if_detected():
                print("⚠️ Bot detection triggered - results may be incomplete")

            # Get page source and parse
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Find all property cards
            properties = []
            articles = soup.find_all('article', class_=lambda x: x and 'item' in x if x else False)

            print(f"📋 Found {len(articles)} property cards")

            for article in articles:
                try:
                    property_data = self._extract_property_data(article)
                    if property_data and property_data.get('price'):
                        properties.append(property_data)
                except Exception as e:
                    print(f"⚠️ Error parsing property: {e}")
                    continue

            print(f"✅ Extracted {len(properties)} valid properties")
            return properties

        except Exception as e:
            print(f"❌ Error scraping page: {e}")
            return []

    def _extract_property_data(self, element) -> Dict:
        """Extract data from a single property element"""
        data = {}

        # Price
        price_elem = element.find('span', class_='item-price')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_nums = price_text.replace('.', '').replace('€', '').replace('/mês', '').replace(',', '').strip()
            price_nums = ''.join(filter(str.isdigit, price_nums))
            if price_nums:
                data['price'] = int(price_nums)

        # Title and URL
        title_elem = element.find('a', class_='item-link')
        if title_elem:
            title_text = title_elem.get('title', '') or title_elem.text.strip()
            data['title'] = title_text
            href = title_elem.get('href', '')
            if href and not href.startswith('http'):
                data['url'] = self.base_url + href
            else:
                data['url'] = href

            # Extract typology
            import re
            typ_match = re.search(r'T[0-4]', title_text)
            if typ_match:
                data['typology'] = typ_match.group()

            # Extract location
            loc_match = re.search(r'na (.+)', title_text)
            if loc_match:
                data['location'] = loc_match.group(1)

        # Area (m²)
        text_content = element.get_text()
        if 'm²' in text_content or 'm2' in text_content:
            import re
            area_match = re.search(r'(\d+)\s*m[²2]', text_content)
            if area_match:
                data['area_m2'] = int(area_match.group(1))

        return data if data else None

    def scrape_neighborhood(self, city: str, neighborhood: str,
                          typology: str = None, max_pages: int = 2) -> pd.DataFrame:
        """
        Scrape specific neighborhood with enhanced anti-detection

        Args:
            city: City name (e.g., 'lisboa', 'oeiras')
            neighborhood: Neighborhood name (e.g., 'ajuda', 'alcantara')
            typology: Filter by T0, T1, T2 (None for all)
            max_pages: Maximum pages to scrape
        """
        base_search_url = f"https://www.idealista.pt/arrendar-casas/{city}/{neighborhood}/"
        all_properties = []

        for page in range(1, max_pages + 1):
            print(f"\n{'='*60}")
            print(f"📍 Scraping {city.title()}, {neighborhood.title()} - Page {page}/{max_pages}")
            print(f"{'='*60}")

            url = f"{base_search_url}pagina-{page}" if page > 1 else base_search_url
            properties = self.scrape_search_page(url)

            if properties:
                all_properties.extend(properties)
                print(f"✅ Total properties so far: {len(all_properties)}")
            else:
                print(f"⚠️ No properties found on page {page}")

            # Longer delay between pages
            if page < max_pages:
                delay = random.uniform(8, 15)
                print(f"⏳ Waiting {delay:.1f}s before next page...")
                time.sleep(delay)

        df = pd.DataFrame(all_properties)

        # Filter by typology if specified
        if typology and not df.empty and 'typology' in df.columns:
            df = df[df['typology'] == typology]
            print(f"\n🔽 Filtered to {len(df)} {typology} listings")

        return df

    def save_to_csv(self, df: pd.DataFrame, filename: str):
        """Save listings to CSV"""
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n💾 Saved {len(df)} listings to {filename}")

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
                print("\n👋 Browser closed")
            except:
                pass


if __name__ == '__main__':
    # Test the enhanced scraper
    print("="*60)
    print("ENHANCED IDEALISTA SCRAPER - TEST MODE")
    print("="*60)

    # Check for proxy in environment
    proxy = os.getenv('PROXY_URL')
    if proxy:
        print(f"✅ Proxy detected in environment")
    else:
        print("ℹ️  No proxy configured (using direct connection)")

    # Initialize with environment proxy (if available)
    scraper = EnhancedIdealistaScraper(headless=False)

    try:
        # Test scrape
        print("\n🧪 Testing scrape on Ajuda...")
        df = scraper.scrape_neighborhood(
            city='lisboa',
            neighborhood='ajuda',
            max_pages=1
        )

        if not df.empty:
            print(f"\n✅ SUCCESS: Found {len(df)} listings")
            print(df[['title', 'price', 'typology']].head())
        else:
            print("\n⚠️ No results - possible bot detection")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        del scraper
