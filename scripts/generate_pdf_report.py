"""
Main script to generate NER PDF report
Ties together data analysis and PDF generation
"""

import sys
from pathlib import Path

# Add parent directory to path to import from src/
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
import pandas as pd
from src.ner_analyzer import NERAnalyzer
from src.pdf_report_generator import PDFReportGenerator


def generate_url_list(csv_path: str, output_path: str, top_n: int = 20):
    """Generate text file with apartment URLs for easy copy-paste"""

    df = pd.read_csv(csv_path)
    df_filtered = df[df['area_m2'] >= 30].sort_values('ner')
    top_apartments = df_filtered.head(top_n)

    with open(output_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("TOP 20 APARTMENTS - IDEALISTA LISTING URLS\n")
        f.write("Net Effective Rent Analysis - Porta 65 Jovem\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        has_tier2 = 'ner_tier2' in top_apartments.columns

        for idx, (i, row) in enumerate(top_apartments.iterrows(), 1):
            if has_tier2:
                f.write(f"#{idx} - NER: €{row['ner']:.0f} (T1) | €{row['ner_tier2']:.0f} (T2)\n")
            else:
                f.write(f"#{idx} - NER: €{row['ner']:.0f}/month\n")

            f.write(f"Gross Rent: €{row['price']:.0f}\n")
            f.write(f"Type: {row['typology']} | Area: {row['area_m2']:.0f}m²\n")

            if pd.notna(row.get('location')):
                f.write(f"Location: {row['location']}\n")

            if row.get('is_aru'):
                f.write("🏛️ ARU Zone (receives +20% subsidy bonus)\n")

            amenities = []
            if row.get('furnished'): amenities.append('Furnished')
            if row.get('balcony'): amenities.append('Balcony')
            if row.get('terrace'): amenities.append('Terrace')
            if row.get('ac'): amenities.append('AC')
            if row.get('elevator'): amenities.append('Elevator')
            if row.get('parking'): amenities.append('Parking')
            if row.get('renovated'): amenities.append('Renovated')

            if amenities:
                f.write(f"Amenities: {', '.join(amenities)}\n")

            if pd.notna(row.get('distance_to_work_km')):
                f.write(f"Distance to work: {row['distance_to_work_km']:.1f}km\n")

            f.write(f"\nURL: {row['url']}\n")
            f.write("\n" + "-" * 80 + "\n\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("NOTES:\n")
        f.write("=" * 80 + "\n")
        f.write("• Copy URL and paste into browser to view listing\n")
        f.write("• NER = Net Effective Rent (after Porta 65 subsidy + IRS credit)\n")

        if has_tier2:
            f.write("• Tier 1 (T1) = Best case (50% subsidy)\n")
            f.write("• Tier 2 (T2) = Realistic case (40% subsidy)\n")

        f.write("• ARU zones receive +20% subsidy bonus\n")
        f.write("• Subsidies decrease after Year 1\n")


def generate_pdf_report(csv_path: str, output_dir: str = 'reports'):
    """
    Generate comprehensive NER PDF report

    Args:
        csv_path: Path to apartments CSV
        output_dir: Directory to save report
    """

    print("=" * 80)
    print("PDF REPORT GENERATOR - NET EFFECTIVE RENT ANALYSIS")
    print("=" * 80)
    print()

    # Step 1: Analyze data
    print("📊 Analyzing apartment data...")
    analyzer = NERAnalyzer(csv_path, min_area=30)
    analyzer.analyze()

    # Step 2: Get all data needed for report
    print("📈 Gathering statistics...")
    summary_stats = analyzer.get_summary_stats()
    top_apartments = analyzer.get_top_n(n=20)
    categories = analyzer.get_by_category()
    aru_comparison = analyzer.get_aru_comparison()
    size_analysis = analyzer.get_size_analysis()

    # Step 3: Save enhanced CSV
    csv_output = 'data/apartments_with_ner.csv'
    analyzer.save_results(csv_output)

    # Step 4: Generate PDF
    report_date = datetime.now().strftime('%Y-%m-%d')
    pdf_path = f'{output_dir}/{report_date}_ner_report.pdf'

    print(f"📄 Generating PDF report...")
    pdf = PDFReportGenerator(pdf_path)

    # Check if we have tier 2 data
    has_tier2 = 'ner_tier2' in top_apartments.columns

    # Title
    title_suffix = ' • Dual-Scenario Analysis (Tier 1 & 2)' if has_tier2 else ''
    pdf.add_title(
        'Net Effective Rent Analysis Report',
        f'Lisbon Rental Market with Porta 65 Jovem Subsidy • {report_date}{title_suffix}'
    )

    # Executive Summary
    pdf.add_summary_box(summary_stats)

    # Top 20 apartments table
    pdf.add_top_apartments_table(top_apartments, top_n=20)

    # Categories (on new pages for better layout)
    if len(categories['furnished_t1']) > 0:
        pdf.add_category_table(
            categories['furnished_t1'],
            'Best Furnished T1 Apartments'
        )

    if len(categories['with_parking']) > 0:
        pdf.add_category_table(
            categories['with_parking'],
            'Best Apartments with Parking'
        )

    if len(categories['near_work']) > 0:
        pdf.add_category_table(
            categories['near_work'],
            'Best Apartments Close to Work (≤3km)'
        )

    if len(categories['large']) > 0:
        pdf.add_category_table(
            categories['large'],
            'Best Large Apartments (≥60m²)'
        )

    # ARU comparison
    pdf.add_comparison_table(aru_comparison)

    # Size analysis
    pdf.add_size_analysis_table(size_analysis)

    # Footer notes
    pdf.add_footer_notes(has_tier2=has_tier2)

    # URL Reference Page (clickable links)
    pdf.add_url_reference_page(top_apartments, top_n=20)

    # Build PDF
    pdf.build()

    # Generate URL text file
    url_list_path = f'{output_dir}/apartment_urls.txt'
    generate_url_list(csv_output, url_list_path, top_n=20)

    # Print summary
    print()
    print("=" * 80)
    print("REPORT SUMMARY")
    print("=" * 80)
    print(f"Total apartments analyzed: {summary_stats['total_apartments']}")
    print(f"Filtered (≥30m²): {summary_stats['filtered_apartments']}")
    print(f"Average gross rent: €{summary_stats['avg_gross_rent']:.0f}")
    print(f"Average NER (Tier 1): €{summary_stats['avg_ner']:.0f}")
    if 'avg_ner_tier2' in summary_stats:
        print(f"Average NER (Tier 2): €{summary_stats['avg_ner_tier2']:.0f}")
    print(f"Average discount: {summary_stats['avg_discount_pct']:.1f}%")
    print(f"ARU zone apartments: {summary_stats['aru_count']} ({summary_stats['aru_percentage']:.1f}%)")
    print()

    if 'ner_tier2' in top_apartments.columns:
        print("Top 3 by NER (Tier 1 | Tier 2):")
        for idx, (i, row) in enumerate(top_apartments.head(3).iterrows(), 1):
            print(f"  {idx}. €{row['ner']:.0f} | €{row['ner_tier2']:.0f}/mo - {row['typology']} {row['area_m2']:.0f}m² (€{row['price']:.0f} gross)")
            if row.get('is_aru'):
                print(f"     🏛️ ARU Zone")
    else:
        print("Top 3 by NER:")
        for idx, (i, row) in enumerate(top_apartments.head(3).iterrows(), 1):
            print(f"  {idx}. €{row['ner']:.0f}/mo - {row['typology']} {row['area_m2']:.0f}m² (€{row['price']:.0f} gross)")
            if row.get('is_aru'):
                print(f"     🏛️ ARU Zone")
    print()
    print("=" * 80)
    print(f"✅ PDF Report: {pdf_path}")
    print(f"✅ URL List: {url_list_path}")
    print(f"✅ CSV Data: {csv_output}")
    print("=" * 80)


if __name__ == '__main__':
    generate_pdf_report('data/apartments_ranked_with_distance.csv')
