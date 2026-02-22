"""
Filter apartments under 1200€ and prepare for detailed scraping
"""

import pandas as pd
import glob

# Load all CSV files
csv_files = glob.glob('data/*.csv')

all_listings = []
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    df['source_file'] = csv_file
    all_listings.append(df)

# Combine all data
df_all = pd.concat(all_listings, ignore_index=True)

print(f"Total listings: {len(df_all)}")
print(f"Price range: {df_all['price'].min()}€ - {df_all['price'].max()}€")

# Filter under 1200
df_under_1200 = df_all[df_all['price'] < 1200].copy()

print(f"\nListings under 1200€: {len(df_under_1200)}")

# Calculate price per m2 where we have area data
df_under_1200['price_per_m2'] = df_under_1200.apply(
    lambda row: row['price'] / row['area_m2'] if pd.notna(row['area_m2']) and row['area_m2'] > 0 else None,
    axis=1
)

# Sort by price per m2 (best value first)
df_with_area = df_under_1200[df_under_1200['price_per_m2'].notna()].copy()
df_with_area = df_with_area.sort_values('price_per_m2')

print(f"Listings with area data: {len(df_with_area)}")

# Show top 20 best value apartments
print("\n" + "="*80)
print("TOP 20 BEST VALUE APARTMENTS (Price per m²)")
print("="*80)
print(df_with_area[['price', 'area_m2', 'price_per_m2', 'typology', 'location']].head(20).to_string())

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
