"""
Inspect a listing page to find correct HTML structure
"""

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

# Use one of our URLs
url = "https://www.idealista.pt/imovel/34788477/"  # The T3 for 1100€

options = uc.ChromeOptions()
driver = uc.Chrome(options=options, version_main=143)

try:
    print(f"Loading: {url}")
    driver.get(url)
    time.sleep(8)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Save the full HTML for inspection
    with open('listing_page_source.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    print("✓ Saved HTML to listing_page_source.html")

    # Look for common class patterns
    print("\nSearching for key elements...")

    # Find all divs with 'detail' in class name
    detail_divs = soup.find_all('div', class_=lambda x: x and 'detail' in x.lower() if x else False)
    print(f"\nFound {len(detail_divs)} divs with 'detail' in class")
    for div in detail_divs[:5]:
        print(f"  - {div.get('class')}: {div.get_text(strip=True)[:100]}")

    # Find all spans with 'detail' in class
    detail_spans = soup.find_all('span', class_=lambda x: x and 'detail' in x.lower() if x else False)
    print(f"\nFound {len(detail_spans)} spans with 'detail' in class")
    for span in detail_spans[:10]:
        print(f"  - {span.get('class')}: {span.get_text(strip=True)[:100]}")

    # Look for feature/characteristic elements
    feature_elems = soup.find_all(class_=lambda x: x and ('feature' in x.lower() or 'characteristic' in x.lower()) if x else False)
    print(f"\nFound {len(feature_elems)} elements with 'feature' or 'characteristic' in class")
    for elem in feature_elems[:10]:
        print(f"  - {elem.name} {elem.get('class')}: {elem.get_text(strip=True)[:100]}")

    # Look for info-features
    info_elems = soup.find_all(class_=lambda x: x and 'info' in x.lower() if x else False)
    print(f"\nFound {len(info_elems)} elements with 'info' in class")
    for elem in info_elems[:10]:
        print(f"  - {elem.name} {elem.get('class')}: {elem.get_text(strip=True)[:100]}")

finally:
    driver.quit()
    print("\n✓ Browser closed")
