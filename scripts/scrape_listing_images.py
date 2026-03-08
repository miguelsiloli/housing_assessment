"""
Scrape images from top apartment listings
Downloads the first image from each listing page
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin
from src.idealista_scraper import IdealistaScraper

def scrape_listing_image_with_selenium(driver, url):
    """
    Scrape the first image from an Idealista listing using Selenium

    Args:
        driver: Selenium WebDriver instance
        url: Listing URL

    Returns:
        Image URL or None if failed
    """
    try:
        print(f"  Loading page...")
        driver.get(url)
        time.sleep(5)  # Wait for page to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Try multiple selectors for images
        img = None

        # Method 1: Open Graph image (most reliable)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']

        # Method 2: Main image in gallery
        img = soup.find('img', class_='detail-image')

        # Method 3: Gallery images
        if not img:
            img = soup.find('img', {'data-ondemand-img': True})

        # Method 4: Any image in main photo section
        if not img:
            photo_section = soup.find('div', class_='detail-multimedia-gallery')
            if photo_section:
                img = photo_section.find('img')

        # Method 5: Any large image
        if not img:
            imgs = soup.find_all('img')
            for candidate in imgs:
                src = candidate.get('src') or candidate.get('data-src')
                if src and ('idealista' in src or 'img' in src):
                    img = candidate
                    break

        if img:
            img_url = img.get('src') or img.get('data-ondemand-img') or img.get('data-src')
            if img_url:
                # Make absolute URL
                if not img_url.startswith('http'):
                    img_url = urljoin('https://www.idealista.pt', img_url)
                return img_url

        return None

    except Exception as e:
        print(f"  ⚠️ Error scraping {url}: {e}")
        return None

def download_image(image_url, save_path):
    """Download image from URL"""
    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            f.write(response.content)

        return True
    except Exception as e:
        print(f"  ⚠️ Error downloading image: {e}")
        return False

def main():
    print("=" * 80)
    print("LISTING IMAGE SCRAPER")
    print("=" * 80)

    # Load data with NER calculations
    data_file = 'data/apartments_with_ner.csv'

    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("Run generate_pdf_report.py first to create NER analysis")
        return

    df = pd.read_csv(data_file)
    print(f"\n📊 Loaded {len(df)} apartments")

    # Filter to minimum 40m² and sort by NER per m²
    df = df[df['area_m2'] >= 40].copy()
    df = df.sort_values('ner_per_m2')
    print(f"📏 Filtered to {len(df)} apartments (≥40m²)")

    # Create images directory
    images_dir = Path('data/listing_images')
    images_dir.mkdir(exist_ok=True)
    print(f"📁 Images will be saved to: {images_dir}")

    # Get top 30 by NER per m²
    top_30 = df.head(30)
    print(f"\n🎯 Scraping images for top 30 listings by NER per m²...")
    print("Using Selenium to bypass bot detection...")

    # Initialize Selenium scraper
    scraper = IdealistaScraper(headless=os.getenv('HEADLESS', '').lower() == 'true')

    # Add image URL column
    df['image_url'] = None
    df['image_path'] = None

    success_count = 0

    try:
        for idx, (i, row) in enumerate(top_30.iterrows(), 1):
            url = row['url']
            listing_id = url.split('/')[-2] if '/imovel/' in url else f'listing_{i}'

            print(f"\n[{idx}/30] Processing: {listing_id}")
            print(f"  URL: {url}")

            # Scrape image URL using Selenium
            image_url = scrape_listing_image_with_selenium(scraper.driver, url)

            if image_url:
                print(f"  ✓ Found image: {image_url[:80]}...")

                # Download image
                image_filename = f"{listing_id}.jpg"
                image_path = images_dir / image_filename

                if download_image(image_url, image_path):
                    print(f"  ✓ Downloaded to: {image_path}")
                    df.at[i, 'image_url'] = image_url
                    df.at[i, 'image_path'] = str(image_path)
                    success_count += 1
                else:
                    # Save URL even if download failed
                    df.at[i, 'image_url'] = image_url
            else:
                print(f"  ✗ No image found")

            # Be nice to the server
            time.sleep(2)

    finally:
        # Close browser
        scraper.driver.quit()
        print("\n✓ Browser closed")

    # Save updated dataframe
    output_file = 'data/apartments_with_images.csv'
    df.to_csv(output_file, index=False)

    print("\n" + "=" * 80)
    print("IMAGE SCRAPING COMPLETE")
    print("=" * 80)
    print(f"✓ Successfully downloaded: {success_count}/30 images")
    print(f"✓ Saved data to: {output_file}")
    print(f"✓ Images directory: {images_dir}")

    if success_count > 0:
        print(f"\n🎨 Ready to generate enhanced PDF report!")
        print(f"Run: python3 scripts/generate_image_report.py")
    else:
        print(f"\n⚠️ No images were downloaded. Enhanced report will be generated without photos.")

if __name__ == '__main__':
    main()
