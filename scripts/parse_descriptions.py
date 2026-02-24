"""
Parse descriptions to extract features and calculate best bang for buck
"""

import pandas as pd
import json
import re

# Load from filtered CSV (instead of old JSON file)
df = pd.read_csv('data/filtered_under_1200.csv')

# Remove duplicates by URL before processing
initial_count = len(df)
df = df.drop_duplicates(subset='url', keep='first')
duplicates_removed = initial_count - len(df)
if duplicates_removed > 0:
    print(f"✓ Removed {duplicates_removed} duplicate listings before processing")

print(f"Analyzing {len(df)} listings under 1200€\n")

# Extract features from descriptions
def parse_features(desc):
    """Extract features from Portuguese description"""
    if pd.isna(desc):
        return {}

    desc_lower = desc.lower()
    features = {}

    # Furnished
    features['furnished'] = any(word in desc_lower for word in ['mobilado', 'mobilada', 'furnished'])

    # Balcony
    features['balcony'] = 'varanda' in desc_lower or 'balcony' in desc_lower

    # Terrace
    features['terrace'] = 'terraço' in desc_lower or 'terraco' in desc_lower or 'terrace' in desc_lower

    # Air conditioning
    features['ac'] = 'ar condicionado' in desc_lower or 'a/c' in desc_lower or 'air conditioning' in desc_lower

    # Elevator
    if 'sem elevador' in desc_lower or 'without elevator' in desc_lower or 'no elevator' in desc_lower:
        features['elevator'] = False
    elif 'elevador' in desc_lower or 'elevator' in desc_lower or 'lift' in desc_lower:
        features['elevator'] = True
    else:
        features['elevator'] = None

    # Parking/Garage
    features['parking'] = any(word in desc_lower for word in ['estacionamento', 'garagem', 'parking', 'garage'])

    # Kitchen equipped
    features['kitchen_equipped'] = any(phrase in desc_lower for phrase in ['cozinha equipada', 'equipped kitchen'])

    # Renovated/remodeled
    features['renovated'] = any(word in desc_lower for word in ['remodelad', 'renova', 'novo'])

    # Bills included
    features['bills_included'] = any(phrase in desc_lower for phrase in ['despesas incluídas', 'contas incluídas', 'bills included'])

    # Extract number of bathrooms
    bathroom_matches = re.findall(r'(\d+)\s*(?:casa de banho|wc|bathroom)', desc_lower)
    if bathroom_matches:
        features['bathrooms'] = int(bathroom_matches[0])

    # Extract number of bedrooms from typology if not in description
    bedroom_match = re.search(r'(\d+)\s*quarto', desc_lower)
    if bedroom_match:
        features['bedrooms'] = int(bedroom_match.group(1))

    return features

# Apply feature extraction if descriptions are available
if 'description' in df.columns:
    print("Extracting features from descriptions...")
    features_list = df['description'].apply(parse_features)
    features_df = pd.DataFrame(features_list.tolist())

    # Merge with main dataframe
    df_enriched = pd.concat([df.reset_index(drop=True), features_df.reset_index(drop=True)], axis=1)
else:
    print("⚠️ No descriptions available in source data. Setting default amenity values...")
    # Add default columns for amenities
    df_enriched = df.copy()
    df_enriched['furnished'] = False
    df_enriched['balcony'] = False
    df_enriched['terrace'] = False
    df_enriched['ac'] = False
    df_enriched['elevator'] = None
    df_enriched['parking'] = False
    df_enriched['kitchen_equipped'] = False
    df_enriched['renovated'] = False
    df_enriched['bills_included'] = False
    df_enriched['bathrooms'] = None
    df_enriched['bedrooms'] = None

# Calculate value score
# Higher score = better value
def calculate_value_score(row):
    """Calculate a value score based on multiple factors"""
    score = 0

    # Base: lower price per m² is better
    if pd.notna(row['price_per_m2']):
        # Normalize: lower price/m² gets higher score (max around 30-40 points)
        score += max(0, 50 - row['price_per_m2'])

    # Amenities (1-3 points each)
    if row.get('furnished'): score += 8
    if row.get('balcony'): score += 5
    if row.get('terrace'): score += 7
    if row.get('ac'): score += 6
    if row.get('elevator'): score += 4
    if row.get('parking'): score += 10
    if row.get('kitchen_equipped'): score += 3
    if row.get('renovated'): score += 5
    if row.get('bills_included'): score += 8

    # Larger area is better (bonus points)
    if pd.notna(row['area_m2']):
        if row['area_m2'] >= 60: score += 5
        elif row['area_m2'] >= 50: score += 3
        elif row['area_m2'] >= 40: score += 1

    # T2 and T3 bonus (more space)
    if row['typology'] == 'T2': score += 5
    if row['typology'] == 'T3': score += 8

    return score

df_enriched['value_score'] = df_enriched.apply(calculate_value_score, axis=1)

# Sort by value score
df_sorted = df_enriched.sort_values('value_score', ascending=False)

# Save enriched data
df_sorted.to_csv('data/apartments_ranked.csv', index=False)
df_sorted.to_json('data/apartments_ranked.json', orient='records', force_ascii=False, indent=2)

print("\n" + "="*100)
print("TOP 20 BEST VALUE APARTMENTS (Comprehensive Score)")
print("="*100)

# Display columns
display_cols = ['price', 'typology', 'area_m2', 'price_per_m2', 'value_score',
                'furnished', 'balcony', 'terrace', 'ac', 'elevator', 'parking', 'renovated', 'location']

# Filter to only show columns that exist
display_cols = [col for col in display_cols if col in df_sorted.columns]

top_20 = df_sorted[display_cols].head(20)

for idx, row in top_20.iterrows():
    print(f"\n#{top_20.index.get_loc(idx) + 1} - Score: {row['value_score']:.1f}")
    print(f"  {row['price']}€/month | {row['typology']} | {row['area_m2']}m² | {row['price_per_m2']:.1f}€/m²")
    print(f"  Location: {row.get('location', 'N/A')}")

    amenities = []
    if row.get('furnished'): amenities.append('Furnished')
    if row.get('balcony'): amenities.append('Balcony')
    if row.get('terrace'): amenities.append('Terrace')
    if row.get('ac'): amenities.append('AC')
    if row.get('elevator'): amenities.append('Elevator')
    if row.get('parking'): amenities.append('Parking')
    if row.get('renovated'): amenities.append('Renovated')

    print(f"  Amenities: {', '.join(amenities) if amenities else 'None listed'}")
    print(f"  URL: {df_sorted.loc[idx, 'url']}")

print("\n" + "="*100)
print("\nSUMMARY STATISTICS")
print("="*100)
print(f"Total apartments analyzed: {len(df_enriched)}")
print(f"Average price: {df_enriched['price'].mean():.0f}€")
print(f"Average area: {df_enriched['area_m2'].mean():.1f}m²")
print(f"Average price/m²: {df_enriched['price_per_m2'].mean():.1f}€")
print(f"\nAmenities breakdown:")
print(f"  Furnished: {df_enriched['furnished'].sum()} ({df_enriched['furnished'].sum()/len(df_enriched)*100:.1f}%)")
print(f"  With balcony: {df_enriched['balcony'].sum()} ({df_enriched['balcony'].sum()/len(df_enriched)*100:.1f}%)")
print(f"  With terrace: {df_enriched['terrace'].sum()} ({df_enriched['terrace'].sum()/len(df_enriched)*100:.1f}%)")
print(f"  With AC: {df_enriched['ac'].sum()} ({df_enriched['ac'].sum()/len(df_enriched)*100:.1f}%)")
print(f"  With parking: {df_enriched['parking'].sum()} ({df_enriched['parking'].sum()/len(df_enriched)*100:.1f}%)")
print(f"  Renovated: {df_enriched['renovated'].sum()} ({df_enriched['renovated'].sum()/len(df_enriched)*100:.1f}%)")

print("\n✓ Saved ranked apartments to:")
print("  - data/apartments_ranked.csv")
print("  - data/apartments_ranked.json")
