# Porta 65 Jovem - Complete Terms & Conditions for 2026
## Official Guide for NER Calculator Implementation

**Last Updated:** February 22, 2026
**Data Sources:** Portal da Habitação, Official Government Documentation

---

## Program Overview

**Porta 65 Jovem** is a Portuguese government rental subsidy program designed to support young people (18-35 years old) in renting housing for permanent residence. The program grants a monthly subsidy based on rent value, income, and household composition.

### Key Changes in 2024-2025

1. **Rent limit eliminated as exclusion criterion** (effective September 1, 2024)
   - Applications accepted for any rent value in Portugal
   - Rent limits still used for income eligibility calculation

2. **Reduced work history requirement** (effective July 2, 2024)
   - Now requires only 3 months of work history (down from 6 months)
   - Applications can be submitted without existing rental contract

3. **Updated 2025 parameters**
   - Minimum wage: €870/month (2025)
   - Maximum corrected monthly income: €3,680 (4 × minimum wage)

---

## Eligibility Requirements

### Age Requirements
- **Age range:** 18 to 35 years old
- **Exception:** In couples, one member may be up to 37 years old

### Work Requirements
- Minimum **3 months of work history**
- Must have regular employment or self-employment income

### Income Requirements

#### Maximum Income Limit
**Corrected Monthly Income (RMC) cannot exceed:**
- **4 × Minimum Wage** = 4 × €870 = **€3,680/month** (2025)

#### Effort Rate (Taxa de Esforço)
**Rent cannot exceed 60% of household's gross monthly income**

Formula:
```
Effort Rate = (Monthly Rent / Gross Monthly Income) × 100
Maximum Allowed: 60%
```

#### Income Calculation Methodology

**For Employees (Category A - IRS):**
```
Monthly Income = Annual Gross Income (from IRS) / 12
```

**For Self-Employed (Category B - Recibos Verdes):**
- **Services:** Consider only 70% of annual income, then divide by 12
- **Sales:** Consider only 20% of annual income, then divide by 12

**Corrected Monthly Income (RMC):**
```
RMC = Total Household Monthly Income / Equivalent Adults Quotient
```

Where Equivalent Adults Quotient reflects household composition:
- First adult: 1.0
- Second adult: 0.7
- Each child under 14: 0.5
- Each person 14+: 0.7

Example: Single person → Quotient = 1.0
Example: Couple with 1 child → Quotient = 1.0 + 0.7 + 0.5 = 2.2

### Residential Requirements
- Must have or intend to have **permanent residence** in Portugal
- Property must be for **permanent housing** (not temporary/vacation)
- Rental contract must be registered with tax authorities (Finanças)

### Exclusion Criteria
- Household members cannot own or rent other residential properties
- No family relations with landlord
- Household income must not exceed 4 × maximum rent for municipality

---

## Maximum Rent Limits by Municipality (2025)

### Grande Lisboa (Lisbon Metropolitan Area)

| Typology | Maximum Rent (€) |
|----------|------------------|
| **T0** | 649€ |
| **T1** | 847€ |
| **T2** | 1,093€ |
| **T3** | 1,311€ |
| **T4** | 1,476€ |
| **T5** | 1,639€ |

**Note:** Since September 2024, these limits are **NOT exclusion criteria**. You can apply for apartments with rent above these limits, but:
- The limits are used to calculate maximum eligible income (4 × rent limit)
- Subsidy calculation may be capped at these reference values

---

## Subsidy Calculation

### Scoring System (Pontuação)

Applications are evaluated by IHRU (Instituto da Habitação e da Reabilitação Urbana) and assigned a score based on:
- Household size and composition
- Effort rate proportionality
- Monthly income level
- Rent proportionality to reference values
- Financial situation of ascendants (parents)

**Minimum Score Required:** 120 points

### Three-Tier Support System (Escalões)

#### **1st Tier (1º Escalão)** - Score ≥ 120 points
- **Year 1:** 50% of rent
- **Year 2:** 35% of rent
- **Years 3-5:** 25% of rent

#### **2nd Tier (2º Escalão)** - Lower scores
- **Year 1:** 40% of rent
- **Year 2:** 30% of rent
- **Years 3-5:** 20% of rent

#### **3rd Tier (3º Escalão)** - Lowest scores
- **Year 1:** 30% of rent
- **Year 2:** 25% of rent
- **Years 3-5:** 15% of rent

**Note:** Typical support ranges from **30% to 50%** in the first year, potentially reaching **70% with majorations**.

### Subsidy Cap
The subsidy is calculated as a percentage of rent, but may be capped at the **Reference Maximum Rent (RMR)** for that municipality and typology.

For example, for a T1 in Lisboa with 847€ RMR:
- Actual rent: 1,000€
- Base subsidy (50%): 500€
- **But capped at:** 50% × 847€ = 423.50€

---

## Majorations (Bonus Increases)

### +20% Majorations

**Urban Rehabilitation Areas (ARU):**
- Property located in classified historical or old areas
- Properties in areas undergoing urban rehabilitation and reconversion

**Dependents:**
- **Two or more dependents** under care

### +15% Majorations

**Single Dependent:**
- One dependent under care

**Disability:**
- Any household member with disability degree ≥ 60%

### +10% Majorations

**Interior/Rural Areas:**
- Property in areas benefiting from incentives for accelerated recovery of interior regions

### Majoration Stacking
Majorations can potentially stack, increasing subsidy beyond base percentage.

**Example:**
- Base subsidy: 50% of rent = 400€
- ARU bonus (+20%): 400€ × 1.20 = 480€
- Two dependents (+20%): 480€ × 1.20 = 576€

---

## IRS Tax Credit for Renters

In addition to Porta 65 subsidy, young renters in Portugal may claim an IRS tax credit:

**Annual Cap:** €900
**Monthly Equivalent:** €75

This is a separate benefit from Porta 65 and must be claimed on annual IRS tax return.

---

## Duration and Renewal

- **Initial approval:** 12 months
- **Maximum duration:** 5 years (renewable annually)
- Must report any changes in circumstances to IHRU
- Must maintain permanent residence in the property

---

## Urban Rehabilitation Areas (ARU) - Sample List

### Lisboa
- Ajuda
- Marvila
- Penha de França
- Beato
- Santa Maria Maior
- Alcântara (parts)

### Oeiras
- Algés
- Oeiras e São Julião da Barra

**Note:** ARU classification may change. Verify current status on Portal da Habitação or municipal websites.

---

## Net Effective Rent (NER) Calculation Formula

### Complete Formula

```
NER = Gross Rent - Porta 65 Subsidy - IRS Credit

Where:
  Porta 65 Subsidy = min(Rent, RMR) × Base % × Majorations
  IRS Credit = €75/month

  Base % = 30-50% depending on tier and year
  Majorations = 1.0 to 1.5+ depending on bonuses
  RMR = Reference Maximum Rent for municipality/typology
```

### Example Calculation

**Scenario:**
- Apartment: T1 in Ajuda, Lisboa
- Gross Rent: 1,000€
- RMR for T1 Lisboa: 847€
- Applicant: 1st tier, Year 1 (50% base)
- ARU Zone: Yes (Ajuda is ARU) → +20%
- Dependents: None

**Calculation:**
```
1. Rent for subsidy = min(1,000€, 847€) = 847€
2. Base subsidy = 847€ × 50% = 423.50€
3. ARU majoration = 423.50€ × 1.20 = 508.20€
4. IRS Credit = 75€

NER = 1,000€ - 508.20€ - 75€ = 416.80€
```

**Effective Discount:** 58.3% of gross rent

---

## Application Process

### How to Apply

1. **Online Application:** Portal da Habitação (https://www.portaldahabitacao.pt)
2. **Required Documents:**
   - IRS (tax return) from previous year
   - Employment contract or proof of self-employment
   - Rental contract or promise of rental contract
   - ID documents
   - Proof of household composition

3. **Processing Time:** 30-45 days average

4. **Retroactive Payment:** If approved, subsidy is paid retroactively from month of application

### Official Simulator

**Portal da Habitação provides an official subsidy simulator:**
https://www.portaldahabitacao.pt/pt/porta65j/simuladorValorSubvencaoForm.jsp

Use this to verify your eligibility and estimated subsidy amount.

---

## Key Considerations for Calculator Implementation

### 1. Conservative Assumptions
When building the NER calculator, consider using:
- **1st Tier, Year 1 (50%)** as optimistic scenario
- **2nd Tier, Year 1 (40%)** as moderate scenario
- **3rd Tier, Year 1 (30%)** as conservative scenario

### 2. Rent Cap Impact
Always check if rent exceeds RMR:
- If rent > RMR → subsidy calculated on RMR only
- User pays full amount above RMR

### 3. ARU Detection
Implement parish/neighborhood lookup to detect ARU zones automatically.

### 4. Income Verification
- Verify user's RMC is ≤ €3,680
- Verify effort rate ≤ 60%
- Both must pass for eligibility

### 5. Multi-Year Projection
Show projected NER for all 5 years, accounting for percentage decrease:
- Year 1: Highest subsidy
- Year 2: Reduced
- Years 3-5: Further reduced but stable

### 6. Warnings
Alert users when:
- Rent exceeds RMR (reduced subsidy efficiency)
- Effort rate > 60% (ineligible)
- RMC > €3,680 (ineligible)
- Rent is significantly above RMR (poor value)

---

## Recommended Calculator Features

### Input Fields
1. **User Income Data:**
   - Annual gross income (IRS)
   - Household composition
   - Number of dependents

2. **Property Data:**
   - Rent amount
   - Municipality
   - Typology (T0/T1/T2/etc.)
   - Parish/neighborhood
   - ARU status (auto-detect or manual)

3. **Scenario Selection:**
   - Expected tier (1st/2nd/3rd)
   - Year of subsidy (1-5)
   - Applicable majorations

### Output Fields
1. **Eligibility Check:**
   - ✅ or ❌ based on income and effort rate
   - Specific reasons if ineligible

2. **Subsidy Breakdown:**
   - Base subsidy percentage
   - Majorations applied
   - Final subsidy amount
   - IRS credit

3. **Net Effective Rent:**
   - Monthly NER
   - Annual NER
   - Effective discount percentage
   - 5-year projection

4. **Comparison Metrics:**
   - NER vs Gross Rent
   - NER vs market average
   - Total savings over 5 years

---

## Data Sources & Official Links

### Official Government Resources
- **Portal da Habitação:** https://www.portaldahabitacao.pt/porta-65-jovem
- **Official Simulator:** https://www.portaldahabitacao.pt/pt/porta65j/simuladorValorSubvencaoForm.jsp
- **Application Page:** https://www2.gov.pt/servicos/candidatar-se-ao-porta-65-jovem

### Reference Documentation
- Decreto-Lei n.º 42/2024 (July 2, 2024) - Latest amendments
- Maximum Rents 2025: RendasMaximas_2025.pdf (Portal da Habitação)

### News & Guides
- [Porta 65 Modalidade Jovem+: complete guide for 2025](https://supercasa.pt/en-gb/noticias/porta-65-modalidade-jovem-complete-guide-for-225/n7294)
- [Novas regras do Porta 65 - Jovem](https://www.doutorfinancas.pt/vida-e-familia/novas-regras-do-porta-65-jovem-quem-se-pode-candidatar/)
- [Porta 65: Quais as regras de apoio ao arrendamento jovem?](https://www.cgd.pt/Site/Saldo-Positivo/casa-e-familia/Pages/porta-65.aspx)
- [Porta 65 com novas regras: Limites das rendas chegam ao fim](https://www.doutorfinancas.pt/vida-e-familia/habitacao/porta-65-com-novas-regras-limites-das-rendas-chegam-ao-fim/)
- [Simulador Porta 65 Jovem: guia completo](https://e-loan.pt/minhas-financas/diversidades/simulador-porta-65-jovem-como-funciona-e-como-candidatar-se/)
- [Porta 65: todas as regras do apoio para o arrendamento jovem](https://www.e-konomista.pt/porta-65-regras-acesso/)

---

## Important Disclaimers

1. **This is not official legal advice.** Always verify with Portal da Habitação official simulator.

2. **Subsidy amounts are estimates.** Final approval depends on IHRU evaluation and scoring.

3. **Rules may change.** Check Portal da Habitação for most current regulations.

4. **ARU zones may change.** Verify current ARU status with municipality.

5. **IRS credit is separate.** Must be claimed on annual tax return; not automatic.

---

## Quick Reference Table

| Parameter | Value (2025) |
|-----------|--------------|
| **Minimum Age** | 18 years |
| **Maximum Age** | 35 years (37 for one in couple) |
| **Work History Required** | 3 months |
| **Maximum RMC** | €3,680/month |
| **Maximum Effort Rate** | 60% |
| **Subsidy Range Year 1** | 30-50% (up to 70% with majorations) |
| **Subsidy Range Year 2** | 25-35% |
| **Subsidy Range Years 3-5** | 15-25% |
| **IRS Credit (Annual)** | €900 |
| **IRS Credit (Monthly)** | €75 |
| **Program Duration** | Max 5 years |
| **Lisboa T1 RMR** | 847€ |
| **Lisboa T2 RMR** | 1,093€ |
| **ARU Majoration** | +20% |
| **Dependent Majoration** | +15-20% |

---

## Implementation Checklist for NER Calculator

- [ ] Input validation for age (18-35)
- [ ] Input validation for RMC (≤ €3,680)
- [ ] Effort rate calculation and validation (≤ 60%)
- [ ] Municipality and typology selection
- [ ] RMR lookup table (all municipalities and typologies)
- [ ] Parish/ARU zone detection
- [ ] Tier selection (1st/2nd/3rd escalão)
- [ ] Year selection (1-5) with automatic percentage adjustment
- [ ] Majoration checkboxes (ARU, dependents, disability, interior)
- [ ] Subsidy calculation with RMR cap
- [ ] IRS credit addition
- [ ] NER calculation
- [ ] 5-year projection table
- [ ] Eligibility warnings and alerts
- [ ] Export/save calculations
- [ ] Integration with apartment listings CSV

---

**Document Version:** 1.0
**Created:** February 22, 2026
**Next Review:** June 2026 (check for program updates)
