# Dual-Scenario NER Analysis Guide

## What Changed?

The NER calculator now shows **two scenarios** side-by-side to give you a realistic range of potential costs:

### Scenario 1: Tier 1 (Optimistic) - 50% Subsidy
**Best case scenario** - if you get approved for the 1st tier by IHRU

- Base subsidy: **50% of rent** (capped at RMR)
- ARU bonus: +20% (if applicable)
- Most favorable outcome

### Scenario 2: Tier 2 (Realistic) - 40% Subsidy
**More conservative scenario** - if you get approved for 2nd tier

- Base subsidy: **40% of rent** (capped at RMR)
- ARU bonus: +20% (if applicable)
- Still very good, just more realistic

---

## Why Show Both?

**You don't know which tier you'll get until IHRU approves your application.**

Tier approval depends on:
- Your income level
- Household composition
- Effort rate (rent as % of income)
- IHRU scoring system

**By showing both scenarios:**
- You see the **best case** (Tier 1)
- You see a **realistic case** (Tier 2)
- You can budget conservatively using Tier 2
- You'll be pleasantly surprised if you get Tier 1!

---

## Example: Top Apartment

**Apartment:** 850€ T2, 40m² in Alcântara (ARU zone)

### Tier 1 (50% subsidy):
```
Gross rent:       €850
RMR (T2):         €1,093 (no cap applied)
Base subsidy:     €850 × 50% = €425
ARU bonus:        €425 × 1.2 = €510
IRS credit:       €75
Total support:    €585

NER (Tier 1):     €850 - €585 = €265/month
```

### Tier 2 (40% subsidy):
```
Gross rent:       €850
RMR (T2):         €1,093 (no cap applied)
Base subsidy:     €850 × 40% = €340
ARU bonus:        €340 × 1.2 = €408
IRS credit:       €75
Total support:    €483

NER (Tier 2):     €850 - €483 = €367/month
```

**Difference:** €102/month between scenarios

---

## How to Read the PDF Report

### Summary Box
Shows both average NERs:
- **Avg NER (T1):** €499 - if you get Tier 1
- **Avg NER (T2):** €590 - if you get Tier 2

### Main Table
Two NER columns:
- **NER (T1):** Best case
- **NER (T2):** Realistic case

Look at the range to understand your actual cost will be somewhere between these two values.

### Category Tables
Same dual-column format - always compare both scenarios when evaluating apartments.

---

## Decision Making Guide

### Conservative Budgeting (Recommended)
**Use Tier 2 (40%) for your budget planning**

Example decision tree:
```
If Tier 2 NER fits your budget comfortably → GO FOR IT
  ↓
If you get Tier 1 → BONUS! Extra €91/month in savings
```

### Optimistic Budgeting (Risky)
**Don't rely solely on Tier 1 (50%)**

If you budget based on Tier 1 and only get Tier 2:
- You'll be short €91/month on average
- Could struggle with rent payments
- Not recommended

---

## Average NER Comparison

| Metric | Tier 1 (50%) | Tier 2 (40%) | Difference |
|--------|--------------|--------------|------------|
| **Average NER** | €499/mo | €590/mo | €91/mo |
| **Top apartment** | €265/mo | €367/mo | €102/mo |
| **Average discount** | 51.5% | 42.5% | -9% |

**Key takeaway:** Even Tier 2 (40%) gives you a massive discount - average €435/month savings!

---

## What Determines Your Tier?

### Factors IHRU Considers:

1. **Income Level**
   - Lower income → Higher tier
   - Higher income → Lower tier

2. **Household Size**
   - More people → Higher tier
   - Single → Lower tier

3. **Effort Rate**
   - Higher rent/income ratio → Higher tier
   - Lower ratio → Lower tier

4. **Dependents**
   - More dependents → Higher tier
   - No dependents → Lower tier

5. **Overall Need Score**
   - IHRU uses a points system
   - 120+ points typically needed
   - Higher points → Better tier

### Rough Guidelines:

**Likely Tier 1 (50%):**
- Single person with income €1,000-1,500/mo
- Rent is 50-60% of gross income
- In need of housing support

**Likely Tier 2 (40%):**
- Single person with income €1,500-2,500/mo
- Rent is 40-50% of gross income
- Moderate housing need

**Likely Tier 3 (30%):**
- Income €2,500-3,680/mo
- Rent is <40% of income
- Lower priority for support

**Note:** These are rough estimates. Actual tier depends on IHRU scoring.

---

## Recommendation

### For Budget Planning:
✅ **Use Tier 2 (40%) values**
- More conservative
- Less risk
- Pleasant surprise if you get Tier 1

### For Apartment Hunting:
✅ **Look at both columns**
- Tier 1 shows the best possible outcome
- Tier 2 shows realistic expectations
- Range shows your actual likely cost

### Example Strategy:
```
Find apartments where:
- Tier 2 NER ≤ Your comfortable budget
- Tier 1 NER = Nice bonus/savings buffer

Example:
Your budget: €600/mo max

Look for apartments with:
- Tier 2 NER: €550-600 (fits budget)
- Tier 1 NER: €450-500 (bonus savings if you get it)
```

---

## Important Reminders

### Year 1 Only!
These calculations show **Year 1 subsidies only**.

Subsidies decrease in subsequent years:
- **Year 1:** 50% (T1) or 40% (T2)
- **Year 2:** 35% (T1) or 30% (T2) → -15%
- **Years 3-5:** 25% (T1) or 20% (T2) → -25%

**Your NER will increase each year** unless you negotiate lower rent.

### ARU Zones Still Matter!
Both tiers get the **+20% ARU bonus** if in rehabilitation zones:
- Ajuda, Alcântara, Marvila, etc.
- ARU apartments are better deals in BOTH scenarios

### IRS Credit (€75/mo)
This is **separate** from Porta 65 and **doesn't change** between tiers.
- Must claim on annual tax return
- Not automatic
- Same €75/month for everyone

---

## Files Updated

All files now support dual-scenario analysis:

1. **`ner_analyzer.py`**
   - Calculates both Tier 1 and Tier 2 NER
   - Stores both in output CSV

2. **`pdf_report_generator.py`**
   - Displays both tiers in tables
   - Formatted for easy comparison

3. **`generate_pdf_report.py`**
   - Orchestrates dual-scenario report
   - Shows both in summary

4. **`data/apartments_with_ner.csv`**
   - Contains both `ner` (Tier 1) and `ner_tier2` columns
   - Full transparency

---

## Quick Reference Table

| Item | Tier 1 | Tier 2 | Tier 3 |
|------|--------|--------|--------|
| **Base subsidy %** | 50% | 40% | 30% |
| **ARU bonus** | +20% | +20% | +20% |
| **Typical approval** | High need | Moderate need | Lower need |
| **Use for budgeting** | Optimistic | ✅ Recommended | Conservative |

---

**Last Updated:** February 22, 2026
**Report Version:** 2.0 (Dual-Scenario)
