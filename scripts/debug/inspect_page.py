"""
Quick script to inspect Idealista's HTML structure
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

url = "https://www.idealista.pt/arrendar-casas/lisboa/"
print(f"Loading: {url}")
driver.get(url)
time.sleep(5)

# Save page source
with open('page_source.html', 'w', encoding='utf-8') as f:
    f.write(driver.page_source)

print("Page source saved to: page_source.html")
print(f"Page title: {driver.title}")
print(f"Page length: {len(driver.page_source)} characters")

# Try to find property listings with various selectors
from bs4 import BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

print("\n--- Trying different selectors ---")
print(f"article tags: {len(soup.find_all('article'))}")
print(f"article.item: {len(soup.find_all('article', class_='item'))}")
print(f"div with 'item' class: {len(soup.find_all('div', class_=lambda x: x and 'item' in x if x else False))}")
print(f"elements with 'property' in class: {len(soup.find_all(class_=lambda x: x and 'property' in x.lower() if x else False))}")
print(f"elements with 'listing' in class: {len(soup.find_all(class_=lambda x: x and 'listing' in x.lower() if x else False))}")

# Find all unique class names to help identify patterns
all_classes = set()
for elem in soup.find_all(class_=True):
    if isinstance(elem.get('class'), list):
        all_classes.update(elem.get('class'))

print(f"\nTotal unique classes found: {len(all_classes)}")
print("\nClasses containing 'item':")
for cls in sorted(all_classes):
    if 'item' in cls.lower():
        print(f"  - {cls}")

driver.quit()
