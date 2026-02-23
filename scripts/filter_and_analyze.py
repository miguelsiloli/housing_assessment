"""
Filter apartments under 1200€ and prepare for detailed scraping
"""

import pandas as pd
import glob
import os

# Load only the fresh scraper output files
csv_files = [
    'data/lisboa_ajuda_listings.csv',
    'data/lisboa_alcantara_listings.csv'
]

# Filter to only existing files
csv_files = [f for f in csv_files if os.path.exists(f)]

if not csv_files:
    print("⚠️ No fresh scraper data found. Looking for any listing files...")
    csv_files = glob.glob('data/*listings.csv')

all_listings = []
for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)
        df['source_file'] = csv_file
        all_listings.append(df)
        print(f"✓ Loaded {len(df)} listings from {csv_file}")
    except Exception as e:
        print(f"⚠️ Skipping {csv_file}: {e}")

if not all_listings:
    print("❌ No valid listing data found!")
    exit(1)

# Combine all data
df_all = pd.concat(all_listings, ignore_index=True)

# Clean and convert price column to numeric
df_all['price'] = pd.to_numeric(df_all['price'], errors='coerce')
df_all = df_all[df_all['price'].notna()]  # Remove rows with invalid prices

print(f"\nTotal listings: {len(df_all)}")
if len(df_all) > 0:
    print(f"Price range: {int(df_all['price'].min())}€ - {int(df_all['price'].max())}€")

# Filter under 1200
df_under_1200 = df_all[df_all['price'] < 1200].copy()

print(f"\nListings under 1200€: {len(df_under_1200)}")

if len(df_under_1200) == 0:
    print("⚠️ No listings found under 1200€")
    exit(0)

# Calculate price per m2 where we have area data
if 'area_m2' in df_under_1200.columns:
    df_under_1200['area_m2'] = pd.to_numeric(df_under_1200['area_m2'], errors='coerce')
    df_under_1200['price_per_m2'] = df_under_1200.apply(
        lambda row: row['price'] / row['area_m2'] if pd.notna(row['area_m2']) and row['area_m2'] > 0 else None,
        axis=1
    )

    # Sort by price per m2 (best value first)
    df_with_area = df_under_1200[df_under_1200['price_per_m2'].notna()].copy()
    df_with_area = df_with_area.sort_values('price_per_m2')

    print(f"Listings with area data: {len(df_with_area)}")

    if len(df_with_area) > 0:
        # Show top 20 best value apartments
        print("\n" + "="*80)
        print("TOP 20 BEST VALUE APARTMENTS (Price per m²)")
        print("="*80)
        print(df_with_area[['price', 'area_m2', 'price_per_m2', 'typology', 'location']].head(20).to_string())
else:
    print("⚠️ No area data available in listings")

# Save filtered results
df_under_1200.to_csv('data/filtered_under_1200.csv', index=False)
print(f"\n✓ Saved {len(df_under_1200)} listings to data/filtered_under_1200.csv")

# Save URLs for detailed scraping
urls_to_scrape = df_under_1200['url'].tolist()
with open('data/urls_to_scrape.txt', 'w') as f:
    for url in urls_to_scrape:
        f.write(url + '\n')

print(f"✓ Saved {len(urls_to_scrape)} URLs to data/urls_to_scrape.txt")
print("\nReady for detailed scraping!")
