"""
NER Analyzer - Pure Data Logic
Separates calculation from presentation
"""

import pandas as pd
from typing import Dict, List, Tuple

# 2025 Official Reference Maximum Rents for Lisboa
REFERENCE_RENTS = {
    'T0': 649,
    'T1': 847,
    'T2': 1093,
    'T3': 1311,
    'T4': 1476,
    'T5': 1639
}

# ARU zones (Urban Rehabilitation Areas) get +20% subsidy bonus
ARU_PARISHES = [
    'Ajuda', 'Marvila', 'Penha de França', 'Beato', 'Santa Maria Maior',
    'Alcântara', 'Santo António', 'Misericórdia', 'São Vicente', 'Arroios',
    'Algés', 'Oeiras', 'Paço de Arcos', 'Junqueira', 'Rato', 'Amoreiras'
]

# IRS Tax Credit for renters (monthly)
IRS_CREDIT = 75

# Porta 65 subsidy percentages by tier and year
SUBSIDY_PERCENTAGE = 0.50  # 50% for 1st tier, Year 1


class NERAnalyzer:
    """Analyzes apartments and calculates Net Effective Rent"""

    def __init__(self, csv_path: str, min_area: float = 30):
        """
        Args:
            csv_path: Path to apartments CSV
            min_area: Minimum area in m² to include (default 30)
        """
        self.df = pd.read_csv(csv_path)
        self.min_area = min_area
        self.results = None

    def parse_location(self, location_str) -> str:
        """Extract parish from location string"""
        if pd.isna(location_str):
            return None

        parts = str(location_str).split(',')
        for part in parts:
            part = part.strip()
            for parish in ARU_PARISHES:
                if parish.lower() in part.lower():
                    return parish
        return None

    def calculate_ner(self, row: pd.Series, tier: int = 1) -> Dict:
        """
        Calculate Net Effective Rent for a single apartment

        Args:
            row: Apartment data row
            tier: Subsidy tier (1=50%, 2=40%, 3=30%)
        """

        gross_rent = row['price']
        typology = row['typology']
        location = row.get('location', '')

        # Get Reference Maximum Rent
        rmr = REFERENCE_RENTS.get(typology, 847)

        # Rent used for subsidy (capped at RMR)
        rent_for_subsidy = min(gross_rent, rmr)

        # Base subsidy percentage by tier
        tier_percentages = {1: 0.50, 2: 0.40, 3: 0.30}
        base_pct = tier_percentages.get(tier, 0.50)

        # Base subsidy
        base_subsidy = rent_for_subsidy * base_pct

        # Check if ARU zone
        parish = self.parse_location(location)
        is_aru = parish in ARU_PARISHES if parish else False

        # Apply ARU bonus (+20%)
        majoration = 1.20 if is_aru else 1.0
        porta65_subsidy = base_subsidy * majoration

        # Total support
        total_support = porta65_subsidy + IRS_CREDIT

        # Net Effective Rent
        ner = gross_rent - total_support

        # Metrics
        discount_pct = (total_support / gross_rent) * 100
        rmr_excess = max(0, gross_rent - rmr)
        ner_per_m2 = ner / row['area_m2'] if row['area_m2'] > 0 else 0

        return {
            'ner': ner,
            'porta65_subsidy': porta65_subsidy,
            'base_percentage': base_pct * 100,
            'tier': tier,
            'irs_credit': IRS_CREDIT,
            'total_support': total_support,
            'discount_pct': discount_pct,
            'is_aru': is_aru,
            'parish': parish,
            'rmr': rmr,
            'rmr_excess': rmr_excess,
            'ner_per_m2': ner_per_m2
        }

    def analyze(self, calculate_both_tiers: bool = True) -> pd.DataFrame:
        """
        Run full NER analysis on all apartments

        Args:
            calculate_both_tiers: If True, calculates both Tier 1 (50%) and Tier 2 (40%)
        """

        # Calculate NER for each apartment
        ner_results_tier1 = []
        ner_results_tier2 = []

        for idx, row in self.df.iterrows():
            # Tier 1 (Best case: 50% subsidy)
            ner_data_t1 = self.calculate_ner(row, tier=1)
            ner_results_tier1.append(ner_data_t1)

            if calculate_both_tiers:
                # Tier 2 (Realistic case: 40% subsidy)
                ner_data_t2 = self.calculate_ner(row, tier=2)
                # Rename tier 2 columns
                ner_data_t2_renamed = {
                    'ner_tier2': ner_data_t2['ner'],
                    'porta65_subsidy_tier2': ner_data_t2['porta65_subsidy'],
                    'total_support_tier2': ner_data_t2['total_support'],
                    'discount_pct_tier2': ner_data_t2['discount_pct'],
                    'ner_per_m2_tier2': ner_data_t2['ner_per_m2']
                }
                ner_results_tier2.append(ner_data_t2_renamed)

        # Combine with original data
        df_tier1 = pd.DataFrame(ner_results_tier1)

        if calculate_both_tiers:
            df_tier2 = pd.DataFrame(ner_results_tier2)
            self.results = pd.concat([self.df, df_tier1, df_tier2], axis=1)
        else:
            self.results = pd.concat([self.df, df_tier1], axis=1)

        # Sort by NER Tier 1 (lowest = best)
        self.results = self.results.sort_values('ner')

        return self.results

    def get_filtered_results(self, min_area: float = None) -> pd.DataFrame:
        """Get results filtered by minimum area"""
        if self.results is None:
            self.analyze()

        min_a = min_area if min_area is not None else self.min_area
        return self.results[self.results['area_m2'] >= min_a].copy()

    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        filtered = self.get_filtered_results()

        stats = {
            'total_apartments': len(self.df),
            'filtered_apartments': len(filtered),
            'avg_gross_rent': filtered['price'].mean(),
            'avg_ner': filtered['ner'].mean(),
            'avg_discount_pct': filtered['discount_pct'].mean(),
            'avg_savings': filtered['total_support'].mean(),
            'aru_count': filtered['is_aru'].sum(),
            'aru_percentage': (filtered['is_aru'].sum() / len(filtered)) * 100,
            'min_ner': filtered['ner'].min(),
            'max_ner': filtered['ner'].max(),
        }

        # Add Tier 2 stats if available
        if 'ner_tier2' in filtered.columns:
            stats['avg_ner_tier2'] = filtered['ner_tier2'].mean()
            stats['avg_discount_pct_tier2'] = filtered['discount_pct_tier2'].mean()
            stats['min_ner_tier2'] = filtered['ner_tier2'].min()
            stats['max_ner_tier2'] = filtered['ner_tier2'].max()

        return stats

    def get_top_n(self, n: int = 20) -> pd.DataFrame:
        """Get top N apartments by NER"""
        filtered = self.get_filtered_results()
        return filtered.head(n)

    def get_by_category(self) -> Dict[str, pd.DataFrame]:
        """Get best apartments by category"""
        filtered = self.get_filtered_results()

        categories = {}

        # Best furnished T1s
        categories['furnished_t1'] = filtered[
            (filtered['typology'] == 'T1') &
            (filtered['furnished'] == True)
        ].head(5)

        # Best with parking
        categories['with_parking'] = filtered[
            filtered['parking'] == True
        ].head(5)

        # Best close to work (≤3km)
        categories['near_work'] = filtered[
            filtered['distance_to_work_km'].notna() &
            (filtered['distance_to_work_km'] <= 3)
        ].head(5)

        # Best with elevator
        categories['with_elevator'] = filtered[
            filtered['elevator'] == True
        ].head(5)

        # Best large apartments (≥60m²)
        categories['large'] = filtered[
            filtered['area_m2'] >= 60
        ].head(5)

        return categories

    def get_aru_comparison(self) -> Dict:
        """Compare ARU vs non-ARU apartments"""
        filtered = self.get_filtered_results()

        aru = filtered[filtered['is_aru'] == True]
        non_aru = filtered[filtered['is_aru'] == False]

        return {
            'aru': {
                'count': len(aru),
                'avg_ner': aru['ner'].mean() if len(aru) > 0 else 0,
                'avg_discount': aru['discount_pct'].mean() if len(aru) > 0 else 0,
            },
            'non_aru': {
                'count': len(non_aru),
                'avg_ner': non_aru['ner'].mean() if len(non_aru) > 0 else 0,
                'avg_discount': non_aru['discount_pct'].mean() if len(non_aru) > 0 else 0,
            }
        }

    def get_size_analysis(self) -> Dict:
        """Analyze apartments by size category"""
        filtered = self.get_filtered_results()

        compact = filtered[(filtered['area_m2'] >= 30) & (filtered['area_m2'] < 45)]
        medium = filtered[(filtered['area_m2'] >= 45) & (filtered['area_m2'] < 60)]
        large = filtered[filtered['area_m2'] >= 60]

        return {
            'compact': {
                'range': '30-45m²',
                'count': len(compact),
                'avg_ner': compact['ner'].mean() if len(compact) > 0 else 0,
                'best_ner': compact['ner'].min() if len(compact) > 0 else 0,
            },
            'medium': {
                'range': '45-60m²',
                'count': len(medium),
                'avg_ner': medium['ner'].mean() if len(medium) > 0 else 0,
                'best_ner': medium['ner'].min() if len(medium) > 0 else 0,
            },
            'large': {
                'range': '60m²+',
                'count': len(large),
                'avg_ner': large['ner'].mean() if len(large) > 0 else 0,
                'best_ner': large['ner'].min() if len(large) > 0 else 0,
            }
        }

    def save_results(self, output_path: str):
        """Save full results to CSV"""
        if self.results is None:
            self.analyze()

        self.results.to_csv(output_path, index=False)
        print(f"✅ Results saved to: {output_path}")
