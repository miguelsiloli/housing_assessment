"""
Rank apartments by distance to work (Deloitte Restelo) and school (NOVA IMS)
"""

import pandas as pd
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# Initialize geocoder
geolocator = Nominatim(user_agent="housing_analysis")

# Load ranked apartments
df = pd.read_csv('data/apartments_ranked.csv')

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

# Sort by total score
df_sorted = df.sort_values('total_score', ascending=False)

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

print("\n✓ Results saved to:")
print("  - data/apartments_ranked_with_distance.csv")
print("  - data/apartments_ranked_with_distance.json")
