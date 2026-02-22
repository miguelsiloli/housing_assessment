"""
Test with visible browser and realistic behavior
"""

import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup

# Setup Chrome - VISIBLE browser
options = uc.ChromeOptions()
# Don't use headless mode

driver = uc.Chrome(options=options, version_main=143)

try:
    # First visit homepage to establish session
    print("Step 1: Visiting homepage...")
    driver.get("https://www.idealista.pt/")
    time.sleep(3)

    # Then navigate to Lisboa rentals
    print("Step 2: Navigating to Lisboa rentals...")
    driver.get("https://www.idealista.pt/arrendar-casas/lisboa/")

    # Wait longer for page to load
    print("Step 3: Waiting for page to load...")
    time.sleep(10)

    # Check what we got
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    print(f"\nPage title: {driver.title}")
    print(f"Page length: {len(driver.page_source)} characters")

    page_text = driver.page_source.lower()
    print(f"Contains DataDome: {'datadome' in page_text}")
    print(f"Contains property data: {'apartamento' in page_text or 'imóvel' in page_text}")

    # Look for articles
    articles = soup.find_all('article')
    print(f"\nFound {len(articles)} article elements")

    if len(articles) > 0:
        print("\nSample article HTML:")
        print(str(articles[0])[:500])

    # Save page for manual inspection
    with open('page_visible.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)

    print("\n✓ Page saved to: page_visible.html")
    print("Press Ctrl+C to close browser...")
    time.sleep(30)  # Keep browser open to inspect manually

except KeyboardInterrupt:
    print("\nClosing...")
finally:
    driver.quit()
