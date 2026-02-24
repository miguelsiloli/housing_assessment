"""
Rank apartments by distance to work (Deloitte Restelo) and school (NOVA IMS)
Now with standardized 1-5 scores by typology
"""

import pandas as pd
import numpy as np
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# Initialize geocoder
geolocator = Nominatim(user_agent="housing_analysis")

# Load ranked apartments
df = pd.read_csv('data/apartments_ranked.csv')

# Remove duplicates by URL before processing
initial_count = len(df)
df = df.drop_duplicates(subset='url', keep='first')
duplicates_removed = initial_count - len(df)
if duplicates_removed > 0:
    print(f"✓ Removed {duplicates_removed} duplicate listings before distance calculation")

print("=" * 100)
print("CALCULATING DISTANCES TO WORK & SCHOOL")
print("=" * 100)

# Reference locations
work_address = "Rua Luís Castanho de Almeida, 2, Lisboa, Portugal"
school_address = "NOVA IMS, Campus de Campolide, Lisboa, Portugal"

print(f"\nWork: {work_address}")
print(f"School: {school_address}")

# Geocode reference locations
print("\nGeolocating reference points...")
try:
    work_location = geolocator.geocode(work_address)
    if work_location:
        work_coords = (work_location.latitude, work_location.longitude)
        print(f"✓ Work (Deloitte Restelo): {work_coords}")
    else:
        # Fallback to known Restelo coordinates
        work_coords = (38.7023, -9.2049)  # Approximate Restelo location
        print(f"⚠️ Using approximate Work coordinates: {work_coords}")

    time.sleep(1)

    school_location = geolocator.geocode(school_address)
    if school_location:
        school_coords = (school_location.latitude, school_location.longitude)
        print(f"✓ School (NOVA IMS): {school_coords}")
    else:
        # Fallback to known NOVA IMS coordinates
        school_coords = (38.7333, -9.1549)  # Campolide
        print(f"⚠️ Using approximate School coordinates: {school_coords}")

except Exception as e:
    print(f"Error geocoding reference locations: {e}")
    # Use fallback coordinates
    work_coords = (38.7023, -9.2049)
    school_coords = (38.7333, -9.1549)
    print(f"Using fallback coordinates")

# Function to geocode apartment address
def geocode_apartment(location_str):
    """Geocode apartment location"""
    if pd.isna(location_str) or location_str == '':
        return None

    try:
        # Try with Lisboa appended
        search_query = f"{location_str}, Lisboa, Portugal"
        location = geolocator.geocode(search_query, timeout=10)

        if location:
            return (location.latitude, location.longitude)

        # Try just the location string
        location = geolocator.geocode(location_str, timeout=10)
        if location:
            return (location.latitude, location.longitude)

    except Exception as e:
        print(f"  Error geocoding '{location_str}': {e}")

    return None

# Calculate distances for each apartment
print(f"\nCalculating distances for {len(df)} apartments...")

distances_to_work = []
distances_to_school = []
coords_list = []

for idx, row in df.iterrows():
    location = row.get('location', '')

    if idx % 10 == 0:
        print(f"  Processing {idx+1}/{len(df)}...")

    # Geocode apartment
    apt_coords = geocode_apartment(location)
    coords_list.append(apt_coords)

    if apt_coords:
        # Calculate distances in km
        dist_work = geodesic(apt_coords, work_coords).km
        dist_school = geodesic(apt_coords, school_coords).km

        distances_to_work.append(dist_work)
        distances_to_school.append(dist_school)
    else:
        distances_to_work.append(None)
        distances_to_school.append(None)

    # Rate limit
    time.sleep(1.1)

# Add distances to dataframe
df['coords'] = coords_list
df['distance_to_work_km'] = distances_to_work
df['distance_to_school_km'] = distances_to_school

# Calculate combined distance score
# Work is priority, so weight it higher (70% work, 30% school)
def calculate_distance_score(row):
    """Calculate score based on distance (closer = better)"""
    if pd.isna(row['distance_to_work_km']) or pd.isna(row['distance_to_school_km']):
        return 0  # No distance data = low score

    # Distances in km
    work_dist = row['distance_to_work_km']
    school_dist = row['distance_to_school_km']

    # Score inversely proportional to distance
    # Maximum score: 50 points for being very close
    work_score = max(0, 35 - (work_dist * 3.5))  # 35 points max for work
    school_score = max(0, 15 - (school_dist * 1.5))  # 15 points max for school

    return work_score + school_score

df['distance_score'] = df.apply(calculate_distance_score, axis=1)

# Recalculate total value score (original + distance)
df['total_score'] = df['value_score'] + df['distance_score']


# ============================================================================
# STANDARDIZED SCORING SYSTEM (1-5) BY TYPOLOGY
# ============================================================================

print("\n" + "=" * 100)
print("CALCULATING STANDARDIZED SCORES BY TYPOLOGY (1-5 scale)")
print("=" * 100)

def calculate_standardized_scores_by_typology(df):
    """
    Calculate 1-5 scores for price, area, and distance based on percentiles within each typology.
    1 = worst/most expensive/smallest/farthest
    5 = best/cheapest/largest/closest
    """

    df_scored = df.copy()

    # Initialize score columns
    df_scored['price_score'] = np.nan
    df_scored['area_score'] = np.nan
    df_scored['distance_work_score'] = np.nan

    # Get unique typologies
    typologies = df_scored['typology'].unique()

    for typo in typologies:
        mask = df_scored['typology'] == typo
        typo_df = df_scored[mask].copy()

        if len(typo_df) < 3:  # Skip if too few apartments in this typology
            continue

        print(f"\nCalculating scores for {typo} ({len(typo_df)} apartments)...")

        # PRICE SCORE (lower price = higher score)
        # Use percentile rank: lower price gets higher percentile
        valid_prices = typo_df['price'].notna()
        if valid_prices.sum() > 0:
            # Rank from low to high (lower price = lower rank number)
            price_ranks = typo_df.loc[valid_prices, 'price'].rank(method='average', ascending=True)
            # Convert to percentile (0-100)
            price_percentiles = (price_ranks - 1) / (len(price_ranks) - 1) * 100
            # Convert to 1-5 score
            price_scores = 1 + (price_percentiles / 25).clip(0, 4)
            df_scored.loc[typo_df[valid_prices].index, 'price_score'] = price_scores.round(1)

        # AREA SCORE (larger area = higher score)
        valid_areas = typo_df['area_m2'].notna()
        if valid_areas.sum() > 0:
            # Rank from low to high (larger area = higher rank number)
            area_ranks = typo_df.loc[valid_areas, 'area_m2'].rank(method='average', ascending=True)
            # Convert to percentile (0-100)
            area_percentiles = (area_ranks - 1) / (len(area_ranks) - 1) * 100
            # Convert to 1-5 score
            area_scores = 1 + (area_percentiles / 25).clip(0, 4)
            df_scored.loc[typo_df[valid_areas].index, 'area_score'] = area_scores.round(1)

        # DISTANCE TO WORK SCORE (closer = higher score)
        valid_distances = typo_df['distance_to_work_km'].notna()
        if valid_distances.sum() > 0:
            # Rank from high to low (closer = lower distance = higher score)
            distance_ranks = typo_df.loc[valid_distances, 'distance_to_work_km'].rank(method='average', ascending=True)
            # Convert to percentile (0-100)
            distance_percentiles = (distance_ranks - 1) / (len(distance_ranks) - 1) * 100
            # Convert to 1-5 score
            distance_scores = 1 + (distance_percentiles / 25).clip(0, 4)
            df_scored.loc[typo_df[valid_distances].index, 'distance_work_score'] = distance_scores.round(1)

    return df_scored

df_scored = calculate_standardized_scores_by_typology(df)

# Sort by total score
df_sorted = df_scored.sort_values('total_score', ascending=False)

# Save results
df_sorted.to_csv('data/apartments_ranked_with_distance.csv', index=False)
df_sorted.to_json('data/apartments_ranked_with_distance.json', orient='records', force_ascii=False, indent=2)

print("\n" + "=" * 100)
print("TOP 20 APARTMENTS BY TOTAL VALUE (Price + Amenities + Distance)")
print("=" * 100)

top_20 = df_sorted.head(20)

for i, (idx, row) in enumerate(top_20.iterrows(), 1):
    print(f"\n#{i} - Total Score: {row['total_score']:.1f} (Value: {row['value_score']:.1f} + Distance: {row['distance_score']:.1f})")
    print(f"  {row['price']}€/month | {row['typology']} | {row.get('area_m2', '?')}m² | {row.get('price_per_m2', 0):.1f}€/m²")

    # Display standardized scores
    if pd.notna(row.get('price_score')):
        print(f"  📊 Scores (1-5): Price={row['price_score']:.1f} | Area={row.get('area_score', 'N/A')} | Distance={row.get('distance_work_score', 'N/A')}")

    if pd.notna(row['distance_to_work_km']):
        print(f"  📍 {row['distance_to_work_km']:.1f}km to work | {row['distance_to_school_km']:.1f}km to NOVA IMS")

    print(f"  Location: {row.get('location', 'N/A')}")

    amenities = []
    if row.get('furnished'): amenities.append('Furnished')
    if row.get('balcony'): amenities.append('Balcony')
    if row.get('terrace'): amenities.append('Terrace')
    if row.get('ac'): amenities.append('AC')
    if row.get('elevator'): amenities.append('Elevator')
    if row.get('parking'): amenities.append('Parking')
    if row.get('renovated'): amenities.append('Renovated')

    if amenities:
        print(f"  ✨ {', '.join(amenities)}")

    print(f"  🔗 {row['url']}")

print("\n" + "=" * 100)
print("STATISTICS")
print("=" * 100)

apartments_with_distance = df_sorted[df_sorted['distance_to_work_km'].notna()]
print(f"Apartments with distance data: {len(apartments_with_distance)}")

if len(apartments_with_distance) > 0:
    print(f"\nDistance to work:")
    print(f"  Average: {apartments_with_distance['distance_to_work_km'].mean():.1f}km")
    print(f"  Closest: {apartments_with_distance['distance_to_work_km'].min():.1f}km")
    print(f"  Farthest: {apartments_with_distance['distance_to_work_km'].max():.1f}km")

    print(f"\nDistance to NOVA IMS:")
    print(f"  Average: {apartments_with_distance['distance_to_school_km'].mean():.1f}km")
    print(f"  Closest: {apartments_with_distance['distance_to_school_km'].min():.1f}km")
    print(f"  Farthest: {apartments_with_distance['distance_to_school_km'].max():.1f}km")

# Show score statistics by typology
print("\n" + "=" * 100)
print("STANDARDIZED SCORES BY TYPOLOGY (1-5 scale)")
print("=" * 100)

for typo in sorted(df_sorted['typology'].unique()):
    typo_df = df_sorted[df_sorted['typology'] == typo]

    print(f"\n{typo} ({len(typo_df)} apartments):")

    if typo_df['price_score'].notna().sum() > 0:
        print(f"  Price Score - Avg: {typo_df['price_score'].mean():.2f}, Range: {typo_df['price_score'].min():.1f}-{typo_df['price_score'].max():.1f}")
        print(f"    Best price: €{typo_df.loc[typo_df['price_score'].idxmax(), 'price']:.0f}")
        print(f"    Worst price: €{typo_df.loc[typo_df['price_score'].idxmin(), 'price']:.0f}")

    if typo_df['area_score'].notna().sum() > 0:
        print(f"  Area Score - Avg: {typo_df['area_score'].mean():.2f}, Range: {typo_df['area_score'].min():.1f}-{typo_df['area_score'].max():.1f}")
        print(f"    Largest: {typo_df.loc[typo_df['area_score'].idxmax(), 'area_m2']:.0f}m²")
        print(f"    Smallest: {typo_df.loc[typo_df['area_score'].idxmin(), 'area_m2']:.0f}m²")

    if typo_df['distance_work_score'].notna().sum() > 0:
        print(f"  Distance Score - Avg: {typo_df['distance_work_score'].mean():.2f}, Range: {typo_df['distance_work_score'].min():.1f}-{typo_df['distance_work_score'].max():.1f}")
        print(f"    Closest: {typo_df.loc[typo_df['distance_work_score'].idxmax(), 'distance_to_work_km']:.1f}km")
        print(f"    Farthest: {typo_df.loc[typo_df['distance_work_score'].idxmin(), 'distance_to_work_km']:.1f}km")

print("\n✓ Results saved to:")
print("  - data/apartments_ranked_with_distance.csv")
print("  - data/apartments_ranked_with_distance.json")
print("\n✓ New columns added: price_score, area_score, distance_work_score (1-5 scale)")
