# NER Calculator - Architecture & Usage

## Overview

The NER (Net Effective Rent) Calculator calculates the actual monthly cost of apartments after applying **Porta 65 Jovem** subsidies and **IRS tax credits**. It uses a clean separation of concerns architecture.

---

## Architecture

### 📊 Data Layer: `ner_analyzer.py`

**Pure data logic - no presentation code**

- Loads apartment data from CSV
- Calculates NER for each apartment
- Detects ARU (Urban Rehabilitation Area) zones
- Provides statistical analysis
- Exports enhanced CSV with NER data

**Key Class:** `NERAnalyzer`

**Key Methods:**
- `analyze()` - Run full NER calculation on all apartments
- `get_summary_stats()` - Get summary statistics
- `get_top_n(n)` - Get top N apartments by NER
- `get_by_category()` - Get best by category (furnished, parking, etc.)
- `get_aru_comparison()` - Compare ARU vs non-ARU
- `save_results(path)` - Export to CSV

---

### 📄 Presentation Layer: `pdf_report_generator.py`

**PDF generation using ReportLab - no business logic**

- Creates professional PDF reports
- Table formatting and styling
- Color-coded sections
- Landscape layout for better table visibility

**Key Class:** `PDFReportGenerator`

**Key Methods:**
- `add_title()` - Report title and subtitle
- `add_summary_box()` - Executive summary metrics
- `add_top_apartments_table()` - Main ranking table
- `add_category_table()` - Category-specific tables
- `add_comparison_table()` - ARU vs non-ARU comparison
- `build()` - Generate final PDF

---

### 🎯 Main Script: `generate_pdf_report.py`

**Orchestrates data analysis and PDF generation**

- Loads apartment data
- Runs NER analysis
- Generates PDF report
- Saves enhanced CSV

---

## Usage

### Basic Usage

```bash
python3 generate_pdf_report.py
```

This generates:
- `reports/YYYY-MM-DD_ner_report.pdf` - Professional PDF report
- `data/apartments_with_ner.csv` - Enhanced CSV with NER calculations

### Custom Usage

```python
from ner_analyzer import NERAnalyzer
from pdf_report_generator import PDFReportGenerator

# Analyze data
analyzer = NERAnalyzer('data/apartments_ranked_with_distance.csv', min_area=30)
analyzer.analyze()

# Get statistics
stats = analyzer.get_summary_stats()
top_20 = analyzer.get_top_n(20)

# Generate PDF
pdf = PDFReportGenerator('reports/my_report.pdf')
pdf.add_title('My Custom Report')
pdf.add_summary_box(stats)
pdf.add_top_apartments_table(top_20)
pdf.build()
```

---

## Subsidy Calculation

### Formula

```
NER = Gross Rent - Porta 65 Subsidy - IRS Credit

Where:
  Porta 65 Subsidy = min(Rent, RMR) × 50% × Majoration
  RMR = Reference Maximum Rent for typology
  Majoration = 1.2 if ARU zone, else 1.0
  IRS Credit = €75/month
```

### Reference Maximum Rents (2025)

| Typology | RMR |
|----------|-----|
| T0 | €649 |
| T1 | €847 |
| T2 | €1,093 |
| T3 | €1,311 |

### ARU Zones (Urban Rehabilitation Areas)

Apartments in these areas receive **+20% subsidy bonus**:

- Ajuda
- Alcântara
- Marvila
- Penha de França
- Beato
- Santo António
- São Vicente
- Arroios
- Algés
- Oeiras
- Paço de Arcos
- Junqueira
- Amoreiras
- Rato

---

## Report Contents

### 1. Executive Summary
- Total apartments analyzed
- Average gross rent vs NER
- Average discount percentage
- ARU zone coverage

### 2. Top 20 Apartments
Full table with:
- Net Effective Rent (NER)
- Gross rent
- Discount %
- Type & area
- Location
- ARU status
- Amenity count
- Distance to work

### 3. Category Rankings
- Best Furnished T1s
- Best with Parking
- Best Close to Work (≤3km)
- Best Large Apartments (≥60m²)

### 4. Analysis Tables
- ARU vs Non-ARU comparison
- Size category analysis (compact/medium/large)

### 5. Notes & Methodology
- Subsidy assumptions
- Calculation formulas
- Important disclaimers

---

## Output Files

### PDF Report (`reports/YYYY-MM-DD_ner_report.pdf`)
- Professional formatted tables
- Color-coded sections
- Landscape layout (A4)
- Ready to print or share

### Enhanced CSV (`data/apartments_with_ner.csv`)
Original apartment data plus:
- `ner` - Net Effective Rent
- `porta65_subsidy` - Subsidy amount
- `irs_credit` - IRS credit (€75)
- `total_support` - Total monthly savings
- `discount_pct` - Percentage discount
- `is_aru` - ARU zone flag
- `parish` - Detected parish
- `rmr` - Reference Maximum Rent
- `ner_per_m2` - NER per square meter

---

## Configuration

### Modify Minimum Area Filter

```python
# In generate_pdf_report.py
analyzer = NERAnalyzer(csv_path, min_area=40)  # Change to 40m²
```

### Modify Number of Top Results

```python
top_apartments = analyzer.get_top_n(n=30)  # Get top 30 instead of 20
```

### Add Custom Categories

```python
# In ner_analyzer.py, get_by_category() method
categories['with_ac'] = filtered[filtered['ac'] == True].head(5)
```

---

## Dependencies

```bash
pip3 install --break-system-packages pandas reportlab
```

- **pandas**: Data analysis
- **reportlab**: PDF generation

---

## File Structure

```
housing_analysis/
├── ner_analyzer.py              # Data logic
├── pdf_report_generator.py      # PDF generation
├── generate_pdf_report.py       # Main script
├── data/
│   ├── apartments_ranked_with_distance.csv  # Input
│   └── apartments_with_ner.csv              # Output
└── reports/
    └── YYYY-MM-DD_ner_report.pdf            # Generated report
```

---

## Example Output

**Console:**
```
================================================================================
PDF REPORT GENERATOR - NET EFFECTIVE RENT ANALYSIS
================================================================================

📊 Analyzing apartment data...
📈 Gathering statistics...
✅ Results saved to: data/apartments_with_ner.csv
📄 Generating PDF report...
✅ PDF report generated: reports/2026-02-22_ner_report.pdf

Top 3 by NER:
  1. €265/mo - T2 40m² (€850 gross)
     🏛️ ARU Zone
  2. €287/mo - T1 45m² (€870 gross)
     🏛️ ARU Zone
  3. €317/mo - T1 55m² (€900 gross)
     🏛️ ARU Zone
```

---

## Best Practices

### 1. Always Use Latest Data
Run scrapers before generating reports:
```bash
python3 scrape_neighborhoods.py
python3 filter_and_analyze.py
python3 generate_pdf_report.py
```

### 2. Verify ARU Zones
ARU status may change. Verify with:
- Portal da Habitação
- Municipal websites
- Idealista listing details

### 3. Update Reference Rents Annually
Check for updated RMR values each year in `ner_analyzer.py`

### 4. Consider Multi-Year Projections
Year 1 subsidy (50%) decreases to 35% in Year 2, 25% in Years 3-5

---

## Troubleshooting

### "No module named 'reportlab'"
```bash
pip3 install --break-system-packages reportlab
```

### PDF not generating
Check write permissions in `reports/` directory:
```bash
mkdir -p reports
chmod 755 reports
```

### Wrong subsidies calculated
Verify:
1. RMR values are up to date
2. ARU zones list is current
3. Input CSV has required columns

---

## Future Enhancements

- [ ] Multi-year NER projection (Years 1-5)
- [ ] Income eligibility checker
- [ ] Effort rate calculator
- [ ] Distance-weighted NER scoring
- [ ] Interactive web interface
- [ ] Email report delivery
- [ ] Comparison with previous months

---

**Last Updated:** February 22, 2026
**Version:** 1.0
