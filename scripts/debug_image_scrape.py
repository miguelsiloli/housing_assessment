"""
Debug script to inspect Idealista listing page HTML
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import time
from bs4 import BeautifulSoup
from src.idealista_scraper import IdealistaScraper

# Load data
df = pd.read_csv('data/apartments_with_ner.csv')
top_listing = df.iloc[0]
url = top_listing['url']

print(f"Testing URL: {url}")
print("="*80)

# Initialize Selenium
scraper = IdealistaScraper(headless=False)  # Run visible to see what's happening

try:
    print("Loading page...")
    scraper.driver.get(url)
    time.sleep(8)  # Wait longer for page to load

    print("\n=== PAGE TITLE ===")
    print(scraper.driver.title)

    soup = BeautifulSoup(scraper.driver.page_source, 'html.parser')

    # Save full HTML to file for inspection
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("\n✓ Saved full HTML to debug_page.html")

    # Check for Open Graph image
    print("\n=== CHECKING FOR OG:IMAGE ===")
    og_image = soup.find('meta', property='og:image')
    if og_image:
        print(f"Found: {og_image.get('content')}")
    else:
        print("Not found")

    # Check for common image classes
    print("\n=== CHECKING FOR IMAGE ELEMENTS ===")

    selectors = [
        ('detail-image', 'class'),
        ('detail-multimedia-gallery', 'class'),
        ('data-ondemand-img', 'attr'),
        ('gallery', 'class'),
        ('main-image', 'class'),
        ('property-image', 'class'),
    ]

    for selector, sel_type in selectors:
        if sel_type == 'class':
            elements = soup.find_all(class_=selector)
        else:
            elements = soup.find_all(attrs={selector: True})

        print(f"\n{selector}: {len(elements)} found")
        if elements:
            print(f"  First element: {str(elements[0])[:200]}")

    # Find all img tags
    print("\n=== ALL IMG TAGS ===")
    all_imgs = soup.find_all('img')
    print(f"Total img tags found: {len(all_imgs)}")

    for i, img in enumerate(all_imgs[:10], 1):  # Show first 10
        src = img.get('src') or img.get('data-src') or img.get('data-ondemand-img')
        classes = img.get('class', [])
        print(f"{i}. src={src[:80] if src else 'None'}")
        print(f"   classes={classes}")

    # Check for picture elements
    print("\n=== ALL PICTURE TAGS ===")
    all_pictures = soup.find_all('picture')
    print(f"Total picture tags found: {len(all_pictures)}")

    for i, pic in enumerate(all_pictures[:5], 1):
        print(f"{i}. {str(pic)[:200]}")

    print("\n" + "="*80)
    print("Inspect debug_page.html to see full page source")
    print("Look for image URLs manually in the HTML")

finally:
    input("\nPress Enter to close browser...")
    scraper.driver.quit()
