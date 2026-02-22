# 🏠 Lisbon Housing Analysis & NER Calculator

Comprehensive apartment search tool for Lisbon rental market with **Porta 65 Jovem** subsidy calculator.

**Goal:** Find the best value apartment under 1,200€/month optimized for proximity to Deloitte Restelo office and NOVA IMS campus, factoring in Portuguese government rental subsidies.

---

## 📊 Quick Start

### 🤖 Automated (GitHub Actions) - RECOMMENDED

Set up automated daily scraping that bypasses anti-bot detection:

```bash
# See comprehensive guide:
cat docs/QUICKSTART_GITHUB_ACTIONS.md
```

**Options:**
- **Self-hosted runner** (free, uses your IP) - Most reliable
- **Cloud + proxy** ($49-500/mo) - No local machine needed
- **Hybrid** (free, fallback to proxy) - Best of both

**[→ Quick Setup Guide](docs/QUICKSTART_GITHUB_ACTIONS.md)**

### 📝 Manual (Local Execution)

#### Generate PDF Report (Main Use Case)

```bash
python3 scripts/generate_pdf_report.py
```

**Output:**
- `reports/YYYY-MM-DD_ner_report.pdf` - Professional PDF with dual-scenario analysis
- `reports/apartment_urls.txt` - Listing URLs for easy access
- `data/apartments_with_ner.csv` - Enhanced dataset with NER calculations

#### Run Full Data Refresh

```bash
# 1. Scrape fresh data from Idealista
python3 scripts/scrape_neighborhoods.py

# 2. Filter apartments under budget
python3 scripts/filter_and_analyze.py

# 3. Extract amenities from descriptions
python3 scripts/parse_descriptions.py

# 4. Calculate distances to work/school
python3 scripts/rank_by_distance.py

# 5. Generate NER analysis report
python3 scripts/generate_pdf_report.py
```

---

## 🎯 Key Features

### 1. **Web Scraping**
- Scrapes Idealista.pt using Selenium + Undetected ChromeDriver
- Bypasses bot detection
- Extracts: price, typology, location, area, amenities

### 2. **Net Effective Rent (NER) Calculator**
- Calculates actual monthly cost after **Porta 65 Jovem** subsidies + IRS tax credit
- **Dual-scenario analysis:**
  - Tier 1 (50% subsidy) - Best case
  - Tier 2 (40% subsidy) - Realistic case
- ARU zone detection (+20% bonus for Urban Rehabilitation Areas)

### 3. **Distance-Based Ranking**
- Geocodes apartment addresses
- Calculates distance to work (Deloitte Restelo) - 70% weight
- Calculates distance to school (NOVA IMS) - 30% weight

### 4. **Professional PDF Reports**
- Landscape A4 format with tables
- Color-coded sections
- Clickable URLs
- Executive summary with key metrics
- Category breakdowns (furnished, parking, proximity, size)

---

## 📂 Project Structure

```
housing_analysis/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── dlt_fast_track.md           # DLT notes
│
├── scripts/                    # Executable scripts
│   ├── scrape_neighborhoods.py    # Scrape Idealista
│   ├── filter_and_analyze.py      # Filter by budget
│   ├── parse_descriptions.py      # Extract amenities
│   ├── rank_by_distance.py        # Calculate distances
│   ├── generate_pdf_report.py     # ⭐ Main report generator
│   └── debug/                     # Debug utilities
│
├── src/                        # Core library code
│   ├── idealista_scraper.py       # Web scraper
│   ├── ner_analyzer.py            # NER calculation logic
│   └── pdf_report_generator.py    # PDF generation
│
├── docs/                       # Documentation
│   ├── NER_CALCULATOR_README.md
│   ├── DUAL_SCENARIO_GUIDE.md
│   ├── porta_65_jovem_terms_2026.md
│   ├── ner_calculator_implementation_guide.md
│   └── 2026-02-22_market_analysis.md
│
├── data/                       # Data files (CSVs)
│   ├── apartments_with_ner.csv           # ⭐ Final dataset
│   ├── apartments_ranked_with_distance.csv
│   ├── filtered_under_1200.csv
│   ├── lisboa_ajuda_listings.csv
│   └── lisboa_alcantara_listings.csv
│
└── reports/                    # Generated reports
    ├── YYYY-MM-DD_ner_report.pdf        # ⭐ Main PDF report
    └── apartment_urls.txt               # URL list
```

---

## 💰 Net Effective Rent (NER) Explained

### What is NER?

**Net Effective Rent** = Actual monthly cost after government subsidies

```
NER = Gross Rent - Porta 65 Subsidy - IRS Credit
```

### Example: 900€ Apartment in ARU Zone

**Tier 1 (Best Case - 50% subsidy):**
```
Gross rent:        €900
RMR (T1):          €847 (Reference Maximum Rent)
Base subsidy:      €847 × 50% = €423.50
ARU bonus:         €423.50 × 1.20 = €508.20
IRS credit:        €75
Total support:     €583.20

NER:               €900 - €583.20 = €316.80/month
```

**Tier 2 (Realistic - 40% subsidy):**
```
Gross rent:        €900
Base subsidy:      €847 × 40% = €338.80
ARU bonus:         €338.80 × 1.20 = €406.56
IRS credit:        €75
Total support:     €481.56

NER:               €900 - €481.56 = €418.44/month
```

### Current Market Results

- **Average gross rent:** €1,025/month
- **Average NER (Tier 1):** €499/month (-51.5%)
- **Average NER (Tier 2):** €590/month (-42.5%)
- **ARU zone coverage:** 54.8% of listings

---

## 🏆 Top Recommendations

### #1 - Best NER (€265-367/month)
- **850€ T2, 40m²** in Alcântara (Rua da Junqueira)
- 2.4km to work, elevator
- 🏛️ ARU Zone
- [View listing](https://www.idealista.pt/imovel/34736072/)

### #2 - Best Balance (€287-388/month)
- **870€ T1, 45m²** in Alcântara
- Furnished, ready to move in
- 🏛️ ARU Zone
- [View listing](https://www.idealista.pt/imovel/34824570/)

### #4 - Premium Features (€317-418/month)
- **900€ T1, 55m²** in Amoreiras
- ALL amenities: Furnished, Balcony, Terrace, AC, Elevator, Parking, Renovated
- 🏛️ ARU Zone
- [View listing](https://www.idealista.pt/imovel/34829784/)

---

## 🛠️ Installation

### Requirements

- Python 3.10+
- Chrome/Chromium browser (v143)
- Internet connection

### Install Dependencies

```bash
pip3 install --break-system-packages -r requirements.txt
```

**Required packages:**
- `pandas` - Data analysis
- `selenium` - Web scraping
- `undetected-chromedriver` - Bot detection bypass
- `geopy` - Geocoding and distance calculation
- `reportlab` - PDF generation

---

## 📖 Documentation

### Core Documentation
- **[NER Calculator README](docs/NER_CALCULATOR_README.md)** - Architecture & usage
- **[Dual Scenario Guide](docs/DUAL_SCENARIO_GUIDE.md)** - Understanding Tier 1 vs Tier 2
- **[Porta 65 Terms](docs/porta_65_jovem_terms_2026.md)** - Official program details
- **[Market Analysis](docs/2026-02-22_market_analysis.md)** - Latest market insights

### Automation Documentation
- **[GitHub Actions Quick Start](docs/QUICKSTART_GITHUB_ACTIONS.md)** - ⭐ Automated scraping setup
- **[GitHub Actions Full Guide](docs/GITHUB_ACTIONS_SETUP.md)** - Complete anti-bot solutions

### Technical Documentation
- **[Implementation Guide](docs/ner_calculator_implementation_guide.md)** - Developer guide

---

## 🔧 Configuration

### Update Search Criteria

**Location** - Edit `scripts/scrape_neighborhoods.py`:
```python
neighborhoods = ['ajuda', 'alcantara', 'marvila']  # Add more
```

**Budget** - Edit `scripts/filter_and_analyze.py`:
```python
max_budget = 1200  # Change as needed
```

**Work/School Locations** - Edit `scripts/rank_by_distance.py`:
```python
work_location = "Rua Luís Castanho de Almeida, 2, Lisboa"
school_location = "NOVA IMS, Campus de Campolide, Lisboa"
```

**ARU Zones** - Edit `src/ner_analyzer.py`:
```python
ARU_PARISHES = ['Ajuda', 'Alcântara', ...]  # Update as needed
```

---

## 📈 Subsidy Details

### Porta 65 Jovem Eligibility

- **Age:** 18-35 years old
- **Max income:** €3,680/month (corrected)
- **Effort rate:** Rent ≤ 60% of gross income
- **Work history:** ≥ 3 months

### Reference Maximum Rents (2025)

| Typology | Lisboa RMR |
|----------|------------|
| T0 | €649 |
| T1 | €847 |
| T2 | €1,093 |
| T3 | €1,311 |

### Subsidy Tiers (Year 1)

| Tier | Base Subsidy | Typical Approval |
|------|--------------|------------------|
| 1 | 50% | High need |
| 2 | 40% | Moderate need |
| 3 | 30% | Lower need |

**ARU Bonus:** +20% for all tiers in Urban Rehabilitation Areas
**IRS Credit:** €75/month (separate from Porta 65)

### Multi-Year Subsidy Decline

| Year | Tier 1 | Tier 2 | Tier 3 |
|------|--------|--------|--------|
| 1 | 50% | 40% | 30% |
| 2 | 35% | 30% | 25% |
| 3-5 | 25% | 20% | 15% |

---

## ⚠️ Known Limitations

1. **Geocoding Coverage:** Only 16.9% of apartments have coordinates (incomplete addresses)
2. **CAPTCHA Blocking:** Cannot scrape individual listing pages directly
3. **Description Parsing:** Amenity extraction from Portuguese text may have false positives/negatives
4. **Straight-line Distances:** Actual commute times may vary (not walking/driving routes)
5. **Data Freshness:** Listings change rapidly - re-run scrapers frequently

---

## 🚀 Usage Examples

### Budget Planning (Conservative)

```python
from src.ner_analyzer import NERAnalyzer

# Analyze with Tier 2 (realistic scenario)
analyzer = NERAnalyzer('data/apartments_with_ner.csv')
analyzer.analyze()

# Get apartments within your budget
budget = 600  # Your max NER budget
affordable = analyzer.get_filtered_results()
affordable = affordable[affordable['ner_tier2'] <= budget]

print(f"Found {len(affordable)} apartments within €{budget}/mo (Tier 2)")
```

### Find Best ARU Deals

```python
# Filter for ARU zones only
aru_apartments = affordable[affordable['is_aru'] == True]
print(f"ARU apartments: {len(aru_apartments)}")
print(f"Average NER: €{aru_apartments['ner'].mean():.0f}")
```

---

## 🔄 Workflow

```
┌─────────────────────┐
│ 1. Scrape Idealista │
│  (scrape_neighborhoods.py)
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ 2. Filter by Budget │
│  (filter_and_analyze.py)
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ 3. Parse Amenities  │
│  (parse_descriptions.py)
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ 4. Calculate Distances │
│  (rank_by_distance.py)
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ 5. Generate PDF     │ ⭐ MAIN OUTPUT
│  (generate_pdf_report.py)
└─────────────────────┘
```

---

## 📝 Important Notes

### Budget Recommendations

✅ **Use Tier 2 (40%) for budgeting** - More conservative and realistic
✅ **Tier 1 (50%) is a bonus** - Pleasant surprise if you get it

### ARU Zones Matter

🏛️ ARU zones receive **+20% subsidy bonus** - significant savings!
- Ajuda, Alcântara, Marvila, Penha de França, Beato, etc.

### Subsidies Decrease Yearly

Year 1 subsidies are highest. Budget for decreases in subsequent years.

### Manual Verification Required

- Test actual commute routes during rush hour
- Visit apartments in person
- Verify amenities match descriptions
- Check neighborhood safety and noise

---

## 📞 Support & Context

**Work:** Deloitte Restelo Business Center
- Rua Luís Castanho de Almeida, nº 2, Lisboa

**School:** NOVA IMS
- Campus de Campolide, Lisboa

**Budget:** Maximum 1,200€/month gross rent
**Priority:** Proximity to work > proximity to school

---

## 📅 Data Freshness

**Last Data Refresh:** February 22, 2026
**Total Listings:** 499 apartments under 1,200€
**Analyzed:** 83 apartments (filtered & ranked)

**Recommendation:** Re-run scrapers weekly for fresh data

---

## 🤝 Contributing

This is a personal apartment search project, but the NER calculator logic can be reused for other Portuguese cities with Porta 65 Jovem coverage.

---

## ⚖️ License & Disclaimer

**Personal project** - Data scraped from Idealista.pt for personal apartment search.

**Disclaimers:**
- Subsidy calculations are estimates based on Porta 65 Jovem official rules
- Final approval depends on IHRU evaluation
- Always verify with official Portal da Habitação simulator
- Respect Idealista's terms of service
- Data is for personal use only

---

**Last Updated:** February 22, 2026
**Status:** ✅ Ready for apartment hunting!
