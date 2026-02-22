# NER Calculator Implementation Guide
## Quick Reference for Porta 65 Jovem Integration

**Purpose:** Update `ner_calculator.py` with accurate 2025/2026 Porta 65 Jovem rules

---

## Critical Updates Needed

### 1. Update Reference Rents (RMR) - 2025 Official Values

**Replace current REFERENCE_RENTS with:**

```python
REFERENCE_RENTS_2025 = {
    'Lisboa': {
        'T0': 649,
        'T1': 847,
        'T2': 1093,
        'T3': 1311,
        'T4': 1476,
        'T5': 1639
    },
    'Oeiras': {
        'T0': 649,  # Same as Lisboa (metropolitan area)
        'T1': 847,
        'T2': 1093,
        'T3': 1311,
        'T4': 1476,
        'T5': 1639
    }
}
```

**Note:** The old values in the current calculator (750, 900, 1100) are incorrect estimates.

---

## 2. Update Subsidy Calculation Logic

### Current Issue
The current calculator assumes a flat 50% subsidy. This is oversimplified.

### New Three-Tier System

```python
# Subsidy percentages by tier and year
SUBSIDY_TIERS = {
    1: {  # 1st Tier (best)
        1: 0.50,  # Year 1: 50%
        2: 0.35,  # Year 2: 35%
        3: 0.25,  # Years 3-5: 25%
        4: 0.25,
        5: 0.25
    },
    2: {  # 2nd Tier
        1: 0.40,
        2: 0.30,
        3: 0.20,
        4: 0.20,
        5: 0.20
    },
    3: {  # 3rd Tier (lowest)
        1: 0.30,
        2: 0.25,
        3: 0.15,
        4: 0.15,
        5: 0.15
    }
}
```

---

## 3. Add Eligibility Validation

### New Class Method: `check_eligibility()`

```python
def check_eligibility(self, gross_rent: float, age: int = None) -> Dict:
    """
    Check if user meets Porta 65 Jovem eligibility criteria

    Returns:
        {
            'eligible': bool,
            'reasons': List[str],  # Failure reasons if ineligible
            'warnings': List[str]   # Warnings even if eligible
        }
    """
    eligible = True
    reasons = []
    warnings = []

    # Age check (18-35)
    if age and (age < 18 or age > 35):
        eligible = False
        reasons.append(f"Age {age} outside range 18-35")

    # Income check (RMC ≤ €3,680)
    if self.rmc > 3680:
        eligible = False
        reasons.append(f"Income €{self.rmc} exceeds maximum €3,680")

    # Effort rate check (rent ≤ 60% of income)
    # Convert RMC to gross monthly for effort rate calculation
    # Simplified: assume RMC ≈ net, gross ≈ RMC × 1.25
    estimated_gross = self.rmc * 1.25
    effort_rate = (gross_rent / estimated_gross) * 100

    if effort_rate > 60:
        eligible = False
        reasons.append(f"Effort rate {effort_rate:.1f}% exceeds 60%")
    elif effort_rate > 50:
        warnings.append(f"High effort rate {effort_rate:.1f}% (max 60%)")

    return {
        'eligible': eligible,
        'reasons': reasons,
        'warnings': warnings,
        'effort_rate': effort_rate
    }
```

---

## 4. Update calculate_subsidy() Method

### Key Changes

```python
def calculate_subsidy(self, gross_rent: float, municipality: str, typology: str,
                     parish: str = None, tier: int = 1, year: int = 1,
                     has_dependents: int = 0, has_disability: bool = False) -> Dict:
    """
    Calculate Porta 65 subsidy with 2025/2026 rules

    Args:
        tier: 1 (best), 2 (middle), 3 (lowest) - based on IHRU scoring
        year: 1-5 (subsidy decreases each year)
        has_dependents: 0, 1, or 2+ (affects majoration)
        has_disability: Any household member with disability ≥60%
    """

    # Get Reference Rent (RMR) for this location/typology
    rmr = REFERENCE_RENTS_2025.get(municipality, {}).get(typology, 847)

    # Get base subsidy percentage for tier and year
    base_percentage = SUBSIDY_TIERS.get(tier, {}).get(year, 0.30)

    # Rent used for subsidy calculation (capped at RMR)
    rent_for_subsidy = min(gross_rent, rmr)

    # Calculate base subsidy
    base_subsidy = rent_for_subsidy * base_percentage

    # Calculate majorations
    majoration_factor = 1.0
    majoration_reasons = []

    # ARU majoration (+20%)
    is_aru = False
    if parish and municipality in ARU_ZONES:
        is_aru = parish in ARU_ZONES[municipality]
        if is_aru:
            majoration_factor *= 1.20
            majoration_reasons.append("ARU Zone (+20%)")

    # Dependent majoration
    if has_dependents >= 2:
        majoration_factor *= 1.20
        majoration_reasons.append("2+ Dependents (+20%)")
    elif has_dependents == 1:
        majoration_factor *= 1.15
        majoration_reasons.append("1 Dependent (+15%)")

    # Disability majoration (+15%)
    if has_disability:
        majoration_factor *= 1.15
        majoration_reasons.append("Disability ≥60% (+15%)")

    # Apply majorations
    final_subsidy = base_subsidy * majoration_factor

    # Calculate how much rent exceeds RMR (user pays this in full)
    rmr_excess = max(0, gross_rent - rmr)

    return {
        'base_subsidy': base_subsidy,
        'base_percentage': base_percentage * 100,  # Convert to %
        'majoration_factor': majoration_factor,
        'majoration_reasons': majoration_reasons,
        'final_subsidy': final_subsidy,
        'rmr': rmr,
        'rmr_excess': rmr_excess,
        'is_aru': is_aru,
        'tier': tier,
        'year': year
    }
```

---

## 5. Update ARU_ZONES

### More Comprehensive ARU List

```python
ARU_ZONES = {
    'Lisboa': [
        # Historical/rehabilitation areas
        'Ajuda',
        'Marvila',
        'Penha de França',
        'Beato',
        'Santa Maria Maior',
        'Alcântara',  # Parts of
        'Santo António',
        'Misericórdia',
        'São Vicente',
        'Arroios',  # Parts of
        # Add more as verified
    ],
    'Oeiras': [
        'Algés',
        'Oeiras e São Julião da Barra',
        'Paço de Arcos',  # Verify
    ]
}
```

**Important:** ARU status should be verified with municipalities. This list is not exhaustive.

---

## 6. Enhanced NER Calculation

### Update calculate_ner() to Include Multi-Year Projection

```python
def calculate_ner_projection(self, gross_rent: float, municipality: str,
                             typology: str, parish: str = None,
                             tier: int = 1, has_dependents: int = 0,
                             has_disability: bool = False) -> Dict:
    """
    Calculate NER with 5-year projection

    Returns dict with year-by-year breakdown and totals
    """

    results = {
        'yearly': [],
        'total_5_year_savings': 0,
        'average_annual_ner': 0
    }

    for year in range(1, 6):
        subsidy_info = self.calculate_subsidy(
            gross_rent, municipality, typology, parish,
            tier=tier, year=year,
            has_dependents=has_dependents,
            has_disability=has_disability
        )

        ner = gross_rent - subsidy_info['final_subsidy'] - IRS_TAX_CREDIT_MONTHLY
        total_support = subsidy_info['final_subsidy'] + IRS_TAX_CREDIT_MONTHLY

        results['yearly'].append({
            'year': year,
            'porta65_subsidy': subsidy_info['final_subsidy'],
            'base_percentage': subsidy_info['base_percentage'],
            'majoration_factor': subsidy_info['majoration_factor'],
            'irs_credit': IRS_TAX_CREDIT_MONTHLY,
            'total_support': total_support,
            'ner': ner,
            'annual_savings': (gross_rent - ner) * 12
        })

        results['total_5_year_savings'] += (gross_rent - ner) * 12

    results['average_annual_ner'] = sum(y['ner'] for y in results['yearly']) / 5

    return results
```

---

## 7. Add Input Validation Helper

```python
class UserProfile:
    """User profile for Porta 65 eligibility"""

    def __init__(self, annual_gross_income: float, household_composition: Dict,
                 age: int, work_months: int = 3):
        """
        Args:
            annual_gross_income: From IRS Category A
            household_composition: {
                'adults': int,
                'children_under_14': int,
                'children_14_plus': int
            }
            age: Applicant age
            work_months: Months of work history
        """
        self.annual_gross = annual_gross_income
        self.composition = household_composition
        self.age = age
        self.work_months = work_months

        # Calculate RMC (Corrected Monthly Income)
        self.monthly_gross = annual_gross_income / 12
        self.rmc = self._calculate_rmc()

    def _calculate_rmc(self) -> float:
        """Calculate corrected monthly income using equivalent adults"""
        # Equivalent adults quotient
        quotient = 1.0  # First adult

        if self.composition.get('adults', 0) > 1:
            quotient += 0.7 * (self.composition['adults'] - 1)

        quotient += 0.5 * self.composition.get('children_under_14', 0)
        quotient += 0.7 * self.composition.get('children_14_plus', 0)

        return self.monthly_gross / quotient

    def is_eligible_age(self) -> bool:
        return 18 <= self.age <= 35

    def is_eligible_work_history(self) -> bool:
        return self.work_months >= 3

    def is_eligible_income(self) -> bool:
        return self.rmc <= 3680

    def count_dependents(self) -> int:
        """Count total dependents for majoration calculation"""
        return (self.composition.get('children_under_14', 0) +
                self.composition.get('children_14_plus', 0))
```

---

## 8. Usage Example for Apartment Listings

### Integrate with Your Dataset

```python
def analyze_listings_with_ner(csv_path: str, user_profile: UserProfile,
                               tier: int = 1, has_disability: bool = False):
    """
    Analyze apartment listings with NER calculations

    Args:
        csv_path: Path to apartments_ranked_with_distance.csv
        user_profile: User's profile for eligibility
        tier: Expected Porta 65 tier (1-3)
    """
    df = pd.read_csv(csv_path)

    calculator = NERCalculator(corrected_monthly_income=user_profile.rmc)
    dependents = user_profile.count_dependents()

    results = []

    for idx, row in df.iterrows():
        # Parse municipality from location
        municipality = 'Lisboa'  # Default
        if pd.notna(row['location']):
            if 'Oeiras' in row['location']:
                municipality = 'Oeiras'

        # Extract parish (simplified - needs better parsing)
        parish = None
        if pd.notna(row['location']):
            parts = row['location'].split(',')
            if len(parts) > 1:
                parish = parts[-2].strip()

        # Check eligibility
        eligibility = calculator.check_eligibility(
            gross_rent=row['price'],
            age=user_profile.age
        )

        if not eligibility['eligible']:
            continue  # Skip ineligible apartments

        # Calculate NER for Year 1
        ner_data = calculator.calculate_ner(
            gross_rent=row['price'],
            municipality=municipality,
            typology=row['typology'],
            parish=parish,
            tier=tier,
            year=1,
            has_dependents=dependents,
            has_disability=has_disability
        )

        # Add original listing data
        ner_data.update({
            'url': row['url'],
            'location': row['location'],
            'area_m2': row['area_m2'],
            'price_per_m2': row['price_per_m2'],
            'total_score': row.get('total_score', 0)
        })

        results.append(ner_data)

    # Create DataFrame sorted by NER (lowest = best)
    ner_df = pd.DataFrame(results).sort_values('net_effective_rent')

    return ner_df
```

---

## 9. Key Formulas Summary

### Eligibility
```
Age: 18 ≤ age ≤ 35
RMC: ≤ €3,680
Effort Rate: (Rent / Gross Income) × 100 ≤ 60%
Work History: ≥ 3 months
```

### RMC Calculation
```
RMC = (Annual Gross Income / 12) / Equivalent Adults Quotient

Quotient = 1.0 (first adult)
         + 0.7 × (additional adults)
         + 0.5 × (children < 14)
         + 0.7 × (children/teens ≥ 14)
```

### Subsidy Calculation
```
Rent_for_subsidy = min(Gross_Rent, RMR)
Base_Subsidy = Rent_for_subsidy × Base_Percentage
Final_Subsidy = Base_Subsidy × Majoration_Factor

Where:
  Base_Percentage = 30-50% (depends on tier and year)
  Majoration_Factor = 1.0 to 1.55+ (ARU, dependents, disability)
```

### NER Calculation
```
NER = Gross_Rent - Porta65_Subsidy - IRS_Credit
    = Gross_Rent - Final_Subsidy - €75
```

---

## 10. Testing Checklist

### Test Cases to Implement

```python
def test_ner_calculator():
    # Test Case 1: Basic eligibility - should pass
    profile1 = UserProfile(
        annual_gross_income=18000,  # €1,500/month
        household_composition={'adults': 1, 'children_under_14': 0, 'children_14_plus': 0},
        age=28,
        work_months=12
    )
    assert profile1.is_eligible_age() == True
    assert profile1.is_eligible_income() == True
    assert profile1.rmc == 1500

    # Test Case 2: Income too high - should fail
    profile2 = UserProfile(
        annual_gross_income=50000,  # €4,167/month
        household_composition={'adults': 1, 'children_under_14': 0, 'children_14_plus': 0},
        age=28
    )
    assert profile2.is_eligible_income() == False

    # Test Case 3: T1 in Lisboa, ARU zone, Year 1, 1st tier
    calc = NERCalculator(corrected_monthly_income=1500)
    result = calc.calculate_ner(
        gross_rent=1000,
        municipality='Lisboa',
        typology='T1',
        parish='Ajuda',
        tier=1,
        year=1,
        has_dependents=0
    )
    # Expected: RMR=847, base=847×0.5=423.50, ARU=423.50×1.2=508.20
    # NER = 1000 - 508.20 - 75 = 416.80
    assert abs(result['net_effective_rent'] - 416.80) < 0.1

    # Test Case 4: Rent below RMR
    result2 = calc.calculate_ner(
        gross_rent=700,
        municipality='Lisboa',
        typology='T1',
        parish='Ajuda',
        tier=1,
        year=1
    )
    # Expected: base=700×0.5=350, ARU=350×1.2=420
    # NER = 700 - 420 - 75 = 205
    assert abs(result2['net_effective_rent'] - 205) < 0.1
```

---

## 11. Display/Output Improvements

### Enhanced Result Display

```python
def display_ner_analysis(ner_df: pd.DataFrame, top_n: int = 10):
    """Pretty print NER analysis results"""

    print("=" * 100)
    print(f"TOP {top_n} APARTMENTS BY NET EFFECTIVE RENT (After Porta 65 + IRS Credit)")
    print("=" * 100)
    print()

    for idx, (i, row) in enumerate(ner_df.head(top_n).iterrows(), 1):
        print(f"#{idx} - NER: €{row['net_effective_rent']:.2f}/month")
        print(f"    Gross Rent: €{row['gross_rent']} → Effective Discount: {row['subsidy_efficiency_pct']:.1f}%")
        print(f"    Location: {row['location']}")
        print(f"    Type: {row['typology']} | Area: {row['area_m2']}m² | €{row['price_per_m2']:.1f}/m²")
        print(f"    Porta 65: €{row['porta65_subsidy']:.2f} ({row.get('base_percentage', 0):.0f}% base")
        if row.get('majoration_factor', 1.0) > 1.0:
            print(f"              × {row['majoration_factor']:.2f} majoration)", end='')
            if row.get('is_aru'):
                print(" [ARU Zone]", end='')
            print()
        else:
            print(")")
        print(f"    IRS Credit: €{row['irs_credit']}")
        print(f"    Total Support: €{row['total_support']:.2f}")
        print(f"    🔗 {row['url']}")
        print()

    print("=" * 100)
    print("SUMMARY STATISTICS")
    print("=" * 100)
    print(f"Average Gross Rent: €{ner_df['gross_rent'].mean():.2f}")
    print(f"Average NER: €{ner_df['net_effective_rent'].mean():.2f}")
    print(f"Average Savings: €{(ner_df['gross_rent'] - ner_df['net_effective_rent']).mean():.2f}/month")
    print(f"Average Discount: {ner_df['subsidy_efficiency_pct'].mean():.1f}%")
    print()
    print(f"Best NER: €{ner_df['net_effective_rent'].min():.2f}")
    print(f"Highest Discount: {ner_df['subsidy_efficiency_pct'].max():.1f}%")
    print()

    aru_count = ner_df['is_aru'].sum()
    print(f"ARU Properties: {aru_count}/{len(ner_df)} ({aru_count/len(ner_df)*100:.1f}%)")
    print("=" * 100)
```

---

## 12. Next Steps

1. **Update `ner_calculator.py`** with new formulas and constants
2. **Test with sample data** using test cases above
3. **Run on full apartment dataset** (apartments_ranked_with_distance.csv)
4. **Generate new report** showing:
   - Top apartments by NER (not just gross rent)
   - ARU vs non-ARU comparison
   - 5-year cost projections
   - Eligibility warnings

5. **Create interactive version** (optional):
   - Web interface or Jupyter notebook
   - Allow user to input their profile
   - Real-time NER calculation as they browse listings

---

## Implementation Priority

**Phase 1 (Essential):**
- ✅ Update REFERENCE_RENTS_2025
- ✅ Add SUBSIDY_TIERS
- ✅ Update calculate_subsidy() with tier/year parameters
- ✅ Add eligibility checks

**Phase 2 (Important):**
- ✅ Multi-year projection
- ✅ Enhanced majoration calculation
- ✅ Better ARU zone detection

**Phase 3 (Nice to Have):**
- ✅ UserProfile class
- ✅ Integration with CSV dataset
- ✅ Enhanced display/reporting
- ⏸️ Web interface

---

**Last Updated:** February 22, 2026
**Status:** Ready for implementation
