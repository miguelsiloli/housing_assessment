"""
Idealista Scraper using Selenium for Lisbon/Oeiras T0/T1/T2 listings
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
from typing import List, Dict


class IdealistaScraper:
    """Scrape rental listings from Idealista using Selenium"""

    def __init__(self, headless=False):
        """
        Initialize Undetected Chrome WebDriver

        Args:
            headless: Run browser in headless mode (no GUI)
        """
        import os
        self.base_url = "https://www.idealista.pt"

        # Setup undetected Chrome options
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        # Initialize undetected driver
        # Don't pin version in CI environments - let it auto-detect
        try:
            if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
                print("Detected CI environment - using auto-detected Chrome version")
                self.driver = uc.Chrome(options=options, use_subprocess=False)
            else:
                print("Using Chrome version 143")
                self.driver = uc.Chrome(options=options, version_main=143)
        except Exception as e:
            print(f"Failed to initialize with version pinning, trying auto-detect: {e}")
            self.driver = uc.Chrome(options=options, use_subprocess=False)

        self.driver.implicitly_wait(10)

        # Visit homepage first to establish session and avoid bot detection
        print("Establishing session...")
        self.driver.get(self.base_url)
        time.sleep(3)

    def __del__(self):
        """Close browser when done"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def scrape_search_page(self, url: str) -> List[Dict]:
        """
        Scrape a single search results page

        Args:
            url: Full Idealista search URL

        Returns:
            List of property dictionaries
        """
        try:
            print(f"Loading: {url}")
            self.driver.get(url)

            # Wait for properties to load (give time for bot detection bypass)
            time.sleep(8)

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Find all property cards (update selectors based on actual HTML)
            properties = []

            # Find property articles (use broader class match)
            articles = soup.find_all('article', class_=lambda x: x and 'item' in x if x else False)

            print(f"Found {len(articles)} potential property cards")

            for article in articles:
                try:
                    property_data = self._extract_property_data(article)
                    if property_data and property_data.get('price'):
                        properties.append(property_data)
                except Exception as e:
                    print(f"Error parsing property: {e}")
                    continue

            return properties

        except Exception as e:
            print(f"Error scraping page: {e}")
            return []

    def _extract_property_data(self, element) -> Dict:
        """Extract data from a single property element"""
        data = {}

        # Price
        price_elem = element.find('span', class_='item-price')
        if price_elem:
            # Price format: "1.350€/mês" - remove dots and extract number
            price_text = price_elem.get_text(strip=True)
            price_nums = price_text.replace('.', '').replace('€', '').replace('/mês', '').replace(',', '').strip()
            price_nums = ''.join(filter(str.isdigit, price_nums))
            if price_nums:
                data['price'] = int(price_nums)

        # Title and URL - title contains typology and location
        title_elem = element.find('a', class_='item-link')
        if title_elem:
            title_text = title_elem.get('title', '') or title_elem.text.strip()
            data['title'] = title_text
            href = title_elem.get('href', '')
            if href and not href.startswith('http'):
                data['url'] = self.base_url + href
            else:
                data['url'] = href

            # Extract typology from title (e.g., "Apartamento T1 na...")
            import re
            typ_match = re.search(r'T[0-4]', title_text)
            if typ_match:
                data['typology'] = typ_match.group()

            # Extract location from title (text after "na")
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

    def scrape_lisboa(self, typology: str = None, max_pages: int = 2) -> pd.DataFrame:
        """
        Scrape Lisboa rental listings

        Args:
            typology: Filter by T0, T1, T2 (None for all)
            max_pages: Maximum pages to scrape
        """
        base_search_url = "https://www.idealista.pt/arrendar-casas/lisboa/"

        all_properties = []

        for page in range(1, max_pages + 1):
            print(f"\n--- Scraping Lisboa page {page} ---")
            url = f"{base_search_url}pagina-{page}" if page > 1 else base_search_url

            properties = self.scrape_search_page(url)
            print(f"Extracted {len(properties)} listings from page {page}")
            all_properties.extend(properties)

            # Longer delay between pages to avoid bot detection
            if page < max_pages:
                time.sleep(5)

        df = pd.DataFrame(all_properties)

        # Filter by typology if specified
        if typology and not df.empty and 'typology' in df.columns:
            df = df[df['typology'] == typology]
            print(f"\nFiltered to {len(df)} {typology} listings")

        return df

    def scrape_oeiras(self, typology: str = None, max_pages: int = 2) -> pd.DataFrame:
        """Scrape Oeiras rental listings"""
        base_search_url = "https://www.idealista.pt/arrendar-casas/oeiras/"

        all_properties = []

        for page in range(1, max_pages + 1):
            print(f"\n--- Scraping Oeiras page {page} ---")
            url = f"{base_search_url}pagina-{page}" if page > 1 else base_search_url

            properties = self.scrape_search_page(url)
            print(f"Extracted {len(properties)} listings from page {page}")
            all_properties.extend(properties)

            # Longer delay between pages to avoid bot detection
            if page < max_pages:
                time.sleep(5)

        df = pd.DataFrame(all_properties)

        if typology and not df.empty and 'typology' in df.columns:
            df = df[df['typology'] == typology]
            print(f"\nFiltered to {len(df)} {typology} listings")

        return df

    def scrape_neighborhood(self, city: str, neighborhood: str, typology: str = None, max_pages: int = 2) -> pd.DataFrame:
        """
        Scrape specific neighborhood rental listings

        Args:
            city: City name (e.g., 'lisboa', 'oeiras')
            neighborhood: Neighborhood name (e.g., 'ajuda', 'alcantara')
            typology: Filter by T0, T1, T2 (None for all)
            max_pages: Maximum pages to scrape
        """
        base_search_url = f"https://www.idealista.pt/arrendar-casas/{city}/{neighborhood}/"

        all_properties = []

        for page in range(1, max_pages + 1):
            print(f"\n--- Scraping {city.title()}, {neighborhood.title()} page {page} ---")
            url = f"{base_search_url}pagina-{page}" if page > 1 else base_search_url

            properties = self.scrape_search_page(url)
            print(f"Extracted {len(properties)} listings from page {page}")
            all_properties.extend(properties)

            # Longer delay between pages to avoid bot detection
            if page < max_pages:
                time.sleep(5)

        df = pd.DataFrame(all_properties)

        if typology and not df.empty and 'typology' in df.columns:
            df = df[df['typology'] == typology]
            print(f"\nFiltered to {len(df)} {typology} listings")

        return df

    def save_to_csv(self, df: pd.DataFrame, filename: str):
        """Save listings to CSV"""
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n✓ Saved {len(df)} listings to {filename}")

    def save_to_json(self, df: pd.DataFrame, filename: str):
        """Save listings to JSON"""
        df.to_json(filename, orient='records', force_ascii=False, indent=2)
        print(f"\n✓ Saved {len(df)} listings to {filename}")

    def scrape_listing_details(self, url: str) -> Dict:
        """
        Scrape detailed information from an individual listing page

        Args:
            url: Full URL to the listing page

        Returns:
            Dictionary with detailed property information
        """
        try:
            print(f"Loading details: {url}")
            self.driver.get(url)
            time.sleep(5)  # Wait for page to load

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            details = {'url': url}

            # Extract basic features
            details_list = soup.find_all('span', class_='detail-title')
            for detail in details_list:
                text = detail.get_text(strip=True).lower()

                if 'wc' in text or 'casa de banho' in text or 'bathroom' in text:
                    import re
                    match = re.search(r'(\d+)', text)
                    if match:
                        details['bathrooms'] = int(match.group(1))

                if 'andar' in text or 'piso' in text or 'floor' in text:
                    details['floor'] = text

                if 'elevador' in text or 'lift' in text or 'elevator' in text:
                    details['has_elevator'] = True

            # Look for amenities/features
            features_section = soup.find_all('li', class_='feature-item')
            amenities = []
            for feature in features_section:
                feature_text = feature.get_text(strip=True)
                amenities.append(feature_text)

                # Flag important amenities
                feature_lower = feature_text.lower()
                if 'estacionamento' in feature_lower or 'garagem' in feature_lower or 'parking' in feature_lower:
                    details['has_parking'] = True
                if 'terraço' in feature_lower or 'terrace' in feature_lower:
                    details['has_terrace'] = True
                if 'varanda' in feature_lower or 'balcony' in feature_lower:
                    details['has_balcony'] = True
                if 'ar condicionado' in feature_lower or 'a/c' in feature_lower or 'air conditioning' in feature_lower:
                    details['has_ac'] = True
                if 'mobilado' in feature_lower or 'furnished' in feature_lower:
                    details['is_furnished'] = True

            details['amenities'] = amenities

            # Energy certificate
            energy_elem = soup.find('span', class_='energy-certificate')
            if energy_elem:
                details['energy_rating'] = energy_elem.get_text(strip=True)

            # Description
            desc_elem = soup.find('div', class_='comment')
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)[:500]  # First 500 chars

            # Photo count
            photo_count_elem = soup.find('span', class_='pictures-count')
            if photo_count_elem:
                import re
                match = re.search(r'(\d+)', photo_count_elem.get_text())
                if match:
                    details['photo_count'] = int(match.group(1))

            # Condition/state
            state_elems = soup.find_all('span', class_='detail-title')
            for elem in state_elems:
                text = elem.get_text(strip=True).lower()
                if 'estado' in text or 'condition' in text:
                    details['condition'] = text

            return details

        except Exception as e:
            print(f"Error scraping details from {url}: {e}")
            return {'url': url, 'error': str(e)}


if __name__ == '__main__':
    print("=" * 60)
    print("IDEALISTA SCRAPER - Lisbon & Oeiras")
    print("Using Selenium WebDriver")
    print("=" * 60)

    scraper = IdealistaScraper(headless=False)  # Visible browser helps bypass detection

    try:
        # Scrape Lisboa T1 apartments
        print("\n\n🏠 SCRAPING LISBOA T1 APARTMENTS...")
        lisboa_df = scraper.scrape_lisboa(typology='T1', max_pages=5)

        if not lisboa_df.empty:
            print(f"\n📊 LISBOA RESULTS:")
            print(lisboa_df[['title', 'price', 'typology', 'location']].head(10))
            scraper.save_to_csv(lisboa_df, 'data/lisboa_t1_listings.csv')
        else:
            print("⚠️ No Lisboa listings found")

        # Scrape Oeiras T1 apartments
        print("\n\n🏠 SCRAPING OEIRAS T1 APARTMENTS...")
        oeiras_df = scraper.scrape_oeiras(typology='T1', max_pages=5)

        if not oeiras_df.empty:
            print(f"\n📊 OEIRAS RESULTS:")
            print(oeiras_df[['title', 'price', 'typology', 'location']].head(10))
            scraper.save_to_csv(oeiras_df, 'data/oeiras_t1_listings.csv')
        else:
            print("⚠️ No Oeiras listings found")

    finally:
        scraper.driver.quit()
        print("\n✓ Browser closed")
