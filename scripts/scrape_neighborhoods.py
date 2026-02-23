import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
Scrape specific Lisbon neighborhoods: Ajuda and Alcantara
"""

from src.idealista_scraper import IdealistaScraper
import time
import os

print("=" * 60)
print("IDEALISTA NEIGHBORHOOD SCRAPER")
print("Target: Lisboa - Ajuda & Alcantara")
print("=" * 60)

# Auto-detect headless mode in CI environments
is_ci = bool(os.getenv('CI') or os.getenv('GITHUB_ACTIONS'))
headless_mode = is_ci or os.getenv('HEADLESS', '').lower() == 'true'

if headless_mode:
    print("🤖 Running in HEADLESS mode (CI detected)")
else:
    print("🖥️  Running with VISIBLE browser")

scraper = IdealistaScraper(headless=headless_mode)

try:
    # Scrape Ajuda
    print("\n\n🏠 SCRAPING LISBOA, AJUDA...")
    ajuda_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='ajuda',
        typology=None,  # Get all typologies
        max_pages=5
    )

    if not ajuda_df.empty:
        print(f"\n📊 AJUDA RESULTS ({len(ajuda_df)} listings):")
        print(ajuda_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(ajuda_df, 'data/lisboa_ajuda_listings.csv')
    else:
        print("⚠️ No Ajuda listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Alcantara
    print("\n\n🏠 SCRAPING LISBOA, ALCANTARA...")
    alcantara_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='alcantara',
        typology=None,  # Get all typologies
        max_pages=5
    )

    if not alcantara_df.empty:
        print(f"\n📊 ALCANTARA RESULTS ({len(alcantara_df)} listings):")
        print(alcantara_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(alcantara_df, 'data/lisboa_alcantara_listings.csv')
    else:
        print("⚠️ No Alcantara listings found")

    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE!")
    print("=" * 60)

    if not ajuda_df.empty:
        print(f"\n✓ Ajuda: {len(ajuda_df)} listings → data/lisboa_ajuda_listings.csv")
    if not alcantara_df.empty:
        print(f"✓ Alcantara: {len(alcantara_df)} listings → data/lisboa_alcantara_listings.csv")

finally:
    scraper.driver.quit()
    print("\n✓ Browser closed")
