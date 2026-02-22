"""
Inspect Idealista's HTML structure with undetected-chromedriver
"""

import undetected_chromedriver as uc
import time

# Setup Chrome
options = uc.ChromeOptions()
options.add_argument('--headless=new')

driver = uc.Chrome(options=options, version_main=143)

url = "https://www.idealista.pt/arrendar-casas/lisboa/"
print(f"Loading: {url}")
driver.get(url)
time.sleep(8)  # Wait longer for page to fully load

# Save page source
with open('page_source_uc.html', 'w', encoding='utf-8') as f:
    f.write(driver.page_source)

print(f"Page source saved to: page_source_uc.html")
print(f"Page title: {driver.title}")
print(f"Page length: {len(driver.page_source)} characters")

# Check for specific text/patterns
page_text = driver.page_source.lower()
print(f"\nContains 'captcha': {'captcha' in page_text}")
print(f"Contains 'datadome': {'datadome' in page_text}")
print(f"Contains 'arrendar': {'arrendar' in page_text}")
print(f"Contains 'preço': {'preço' in page_text or 'preco' in page_text}")

# Try to find property listings with various selectors
from bs4 import BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

print("\n--- Searching for property elements ---")
print(f"article tags: {len(soup.find_all('article'))}")
print(f"div tags: {len(soup.find_all('div'))}")

# Look for common property listing patterns
for tag in ['article', 'div', 'section']:
    for keyword in ['item', 'property', 'listing', 'card', 'advert']:
        found = soup.find_all(tag, class_=lambda x: x and keyword in x.lower() if x else False)
        if found:
            print(f"{tag} with '{keyword}' in class: {len(found)}")

driver.quit()
print("\n✓ Done")
