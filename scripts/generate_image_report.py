"""
Generate enhanced PDF report with apartment images
Shows top 20 listings with photos, NER analysis, standardized scores, and amenities
Table-based layout with each listing as a row
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime


def calculate_additional_scores(df):
    """
    Calculate additional standardized 1-5 scores:
    - Price by location/zone
    - Price per m² by typology
    - These supplement the existing scores from rank_by_distance.py
    """
    df_scored = df.copy()

    # Initialize new score columns
    df_scored['price_location_score'] = np.nan
    df_scored['price_per_m2_score'] = np.nan

    # Extract zone/parish from location for grouping
    def extract_zone(location_str):
        """Extract the last part after comma as zone"""
        if pd.isna(location_str):
            return 'Unknown'
        parts = str(location_str).split(',')
        return parts[-1].strip() if len(parts) > 0 else 'Unknown'

    df_scored['zone'] = df_scored['location'].apply(extract_zone)

    # Score price by location/zone
    zones = df_scored['zone'].unique()
    for zone in zones:
        mask = df_scored['zone'] == zone
        zone_df = df_scored[mask]

        if len(zone_df) >= 2:  # Need at least 2 to rank
            valid_prices = zone_df['price'].notna()
            if valid_prices.sum() > 1:
                price_ranks = zone_df.loc[valid_prices, 'price'].rank(method='average', ascending=True)
                price_percentiles = (price_ranks - 1) / (len(price_ranks) - 1) * 100
                price_scores = 1 + (price_percentiles / 25).clip(0, 4)
                df_scored.loc[zone_df[valid_prices].index, 'price_location_score'] = price_scores.round(1)

    # Score price per m² by typology
    typologies = df_scored['typology'].unique()
    for typo in typologies:
        mask = df_scored['typology'] == typo
        typo_df = df_scored[mask]

        if len(typo_df) >= 2:
            valid_ppm2 = typo_df['price_per_m2'].notna()
            if valid_ppm2.sum() > 1:
                ppm2_ranks = typo_df.loc[valid_ppm2, 'price_per_m2'].rank(method='average', ascending=True)
                ppm2_percentiles = (ppm2_ranks - 1) / (len(ppm2_ranks) - 1) * 100
                ppm2_scores = 1 + (ppm2_percentiles / 25).clip(0, 4)
                df_scored.loc[typo_df[valid_ppm2].index, 'price_per_m2_score'] = ppm2_scores.round(1)

    return df_scored


def create_image_report(df, output_path='reports/apartments_with_images.pdf'):
    """
    Create PDF report with table-based layout
    Each listing is a row with image, details, and scores

    Args:
        df: DataFrame with apartment data including scores
        output_path: Where to save the PDF
    """

    # Calculate additional scores
    df = calculate_additional_scores(df)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),  # Landscape for wider tables
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name='ReportTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='CompactDetail',
        fontSize=7,
        textColor=colors.HexColor('#34495e'),
        leading=9
    ))

    styles.add(ParagraphStyle(
        name='ScoreLabel',
        fontSize=6,
        textColor=colors.HexColor('#7f8c8d'),
        leading=7
    ))

    story = []

    # Title
    story.append(Paragraph("🏠 Top 20 Lisbon Apartments - Net Effective Rent Analysis", styles['ReportTitle']))
    story.append(Paragraph(
        f"With Photos & Standardized Scores • {datetime.now().strftime('%B %d, %Y')}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*cm))

    # Summary
    total = len(df)
    avg_gross = df['price'].mean()
    avg_ner_t1 = df['ner'].mean()
    avg_ner_t2 = df['ner_tier2'].mean() if 'ner_tier2' in df.columns else None

    summary_data = [
        ['Total Apartments', 'Avg Gross', 'Avg NER (T1)', 'Avg NER (T2)', 'ARU Zones'],
        [
            str(total),
            f"€{avg_gross:.0f}",
            f"€{avg_ner_t1:.0f}",
            f"€{avg_ner_t2:.0f}" if avg_ner_t2 else 'N/A',
            f"{df['is_aru'].sum()} ({df['is_aru'].sum()/len(df)*100:.0f}%)"
        ]
    ]

    summary_table = Table(summary_data, colWidths=[4*cm, 3*cm, 3*cm, 3*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ecf0f1')),
        ('FONTSIZE', (0, 1), (-1, 1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 0.5*cm))

    # Legend for scores
    legend_text = """<b>Score Legend (1-5 scale):</b> Price (Typology) | Price (Location) | Price/m² | Area | Distance to Work<br/>
    <i>Higher score = better value. All scores are relative to similar apartments.</i>"""
    story.append(Paragraph(legend_text, styles['Normal']))
    story.append(Spacer(1, 0.3*cm))

    # Table header
    headers = ['#', 'Image', 'Details', 'NER (T1/T2)', 'Scores (1-5)', 'Location & Amenities']

    # Build rows for top 20
    top_20 = df.head(20)
    table_data = [headers]

    for idx, (i, row) in enumerate(top_20.iterrows(), 1):
        # Column 1: Rank
        rank = Paragraph(f"<b>{idx}</b>", styles['Normal'])

        # Column 2: Image
        image_path = row.get('image_path')
        if image_path and os.path.exists(image_path):
            try:
                file_size = os.path.getsize(image_path)
                if file_size > 5000:  # Valid image
                    img = Image(image_path, width=4*cm, height=3*cm)
                else:
                    img = Paragraph("<i>No photo</i>", styles['CompactDetail'])
            except Exception as e:
                img = Paragraph("<i>Error</i>", styles['CompactDetail'])
        else:
            img = Paragraph("<i>No photo</i>", styles['CompactDetail'])

        # Column 3: Details
        details_lines = [
            f"<b>{row['typology']} • {row['area_m2']:.0f}m²</b>",
            f"€{row['price']:.0f}/mo • €{row.get('price_per_m2', 0):.1f}/m²"
        ]

        if row.get('is_aru'):
            details_lines.append("🏛️ <b>ARU Zone</b> (+20%)")

        if pd.notna(row.get('distance_to_work_km')):
            details_lines.append(f"📍 {row['distance_to_work_km']:.1f}km to work")

        details = Paragraph("<br/>".join(details_lines), styles['CompactDetail'])

        # Column 4: NER
        ner_t1 = row['ner']
        ner_t2 = row.get('ner_tier2')

        ner_lines = [
            f"<b>€{ner_t1:.0f}</b>",
            f"€{ner_t2:.0f}" if pd.notna(ner_t2) else 'N/A'
        ]
        ner = Paragraph("<br/>".join(ner_lines), styles['CompactDetail'])

        # Column 5: Scores
        score_lines = []

        # Price (Typology)
        price_score = row.get('price_score')
        if pd.notna(price_score):
            score_lines.append(f"P(T): <b>{price_score:.1f}</b>")

        # Price (Location)
        price_loc_score = row.get('price_location_score')
        if pd.notna(price_loc_score):
            score_lines.append(f"P(L): <b>{price_loc_score:.1f}</b>")

        # Price per m²
        ppm2_score = row.get('price_per_m2_score')
        if pd.notna(ppm2_score):
            score_lines.append(f"P/m²: <b>{ppm2_score:.1f}</b>")

        # Area
        area_score = row.get('area_score')
        if pd.notna(area_score):
            score_lines.append(f"Area: <b>{area_score:.1f}</b>")

        # Distance
        dist_score = row.get('distance_work_score')
        if pd.notna(dist_score):
            score_lines.append(f"Dist: <b>{dist_score:.1f}</b>")

        if score_lines:
            scores = Paragraph("<br/>".join(score_lines), styles['ScoreLabel'])
        else:
            scores = Paragraph("<i>N/A</i>", styles['CompactDetail'])

        # Column 6: Location & Amenities
        loc_lines = []

        location = str(row.get('location', ''))[:50]
        if location and location != 'nan':
            loc_lines.append(f"<b>{location}</b>")

        amenities = []
        if row.get('furnished'): amenities.append('Furn')
        if row.get('balcony'): amenities.append('Balc')
        if row.get('terrace'): amenities.append('Terr')
        if row.get('ac'): amenities.append('AC')
        if row.get('elevator'): amenities.append('Elev')
        if row.get('parking'): amenities.append('Park')
        if row.get('renovated'): amenities.append('Renov')

        if amenities:
            loc_lines.append(f"✨ {', '.join(amenities)}")

        # URL
        url = str(row.get('url', ''))
        if url and url != 'nan':
            listing_id = url.split('/')[-2] if '/imovel/' in url else ''
            if listing_id:
                url_link = f'<link href="{url}" color="blue">{listing_id}</link>'
                loc_lines.append(f"🔗 {url_link}")

        location_amenities = Paragraph("<br/>".join(loc_lines), styles['CompactDetail'])

        # Add row
        table_data.append([rank, img, details, ner, scores, location_amenities])

    # Create main table
    main_table = Table(
        table_data,
        colWidths=[1*cm, 4.5*cm, 4*cm, 2.5*cm, 3*cm, 10*cm],
        repeatRows=1  # Repeat header on each page
    )

    main_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Data rows
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Rank column centered
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Image column centered
        ('LEFTPADDING', (0, 1), (-1, -1), 6),
        ('RIGHTPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),

        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story.append(main_table)
    story.append(Spacer(1, 0.5*cm))

    # Footer notes
    notes = """
    <b>Notes:</b><br/>
    • <b>NER (Net Effective Rent):</b> Actual monthly cost after Porta 65 Jovem subsidy + €75 IRS credit<br/>
    • <b>T1/T2:</b> Tier 1 (50% subsidy) / Tier 2 (40% subsidy)<br/>
    • <b>Scores:</b> P(T)=Price vs Typology, P(L)=Price vs Location, P/m²=Price per m², Area=Size, Dist=Distance to work<br/>
    • <b>ARU:</b> Urban Rehabilitation Area (receives +20% subsidy bonus)<br/>
    • Generated: {}<br/>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M'))

    story.append(Paragraph(notes, styles['Normal']))

    # Build PDF
    doc.build(story)
    print(f"✅ Enhanced PDF report generated: {output_path}")


def main():
    print("=" * 80)
    print("ENHANCED PDF REPORT GENERATOR (WITH IMAGES & SCORES)")
    print("=" * 80)

    # Load data with images
    data_file = 'data/apartments_with_images.csv'

    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("Run scrape_listing_images.py first to download images")
        return

    df = pd.read_csv(data_file)
    print(f"\n📊 Loaded {len(df)} apartments")

    # Check how many have images
    has_images = df['image_path'].notna().sum()
    print(f"📸 Apartments with images: {has_images}")

    if has_images == 0:
        print("⚠️ No images found. The report will be generated without photos.")

    # Generate report
    output_path = f"reports/{datetime.now().strftime('%Y-%m-%d')}_apartments_with_images.pdf"
    create_image_report(df, output_path)

    print(f"\n✅ Report saved to: {output_path}")

if __name__ == '__main__':
    main()
