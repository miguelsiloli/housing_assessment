"""
Generate enhanced PDF report with apartment images
Shows top 20 listings with photos, NER analysis, and amenities
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

def create_image_report(df, output_path='reports/apartments_with_images.pdf'):
    """
    Create PDF report with images of top apartments

    Args:
        df: DataFrame with apartment data including image_path
        output_path: Where to save the PDF
    """

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='Subtitle',
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_CENTER,
        spaceAfter=20
    ))

    styles.add(ParagraphStyle(
        name='ListingTitle',
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name='ListingDetail',
        fontSize=10,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name='NERHighlight',
        fontSize=16,
        textColor=colors.HexColor('#27ae60'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    ))

    story = []

    # Title page
    story.append(Paragraph("🏠 Top 20 Lisbon Apartments", styles['Title']))
    story.append(Paragraph(
        f"Net Effective Rent Analysis with Photos<br/>{datetime.now().strftime('%B %d, %Y')}",
        styles['Subtitle']
    ))

    # Summary box
    total_listings = len(df)
    avg_gross = df['price'].mean()
    avg_ner_t1 = df['ner'].mean()
    avg_ner_t2 = df['ner_tier2'].mean() if 'ner_tier2' in df.columns else None

    summary_text = f"""
    <b>Report Summary</b><br/>
    Total Apartments Analyzed: {total_listings}<br/>
    Average Gross Rent: €{avg_gross:.0f}/month<br/>
    Average NER (Tier 1 - 50%): €{avg_ner_t1:.0f}/month<br/>
    """

    if avg_ner_t2:
        summary_text += f"Average NER (Tier 2 - 40%): €{avg_ner_t2:.0f}/month<br/>"

    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    # Separator
    story.append(PageBreak())

    # Top 20 listings with images
    top_20 = df.head(20)

    for idx, (i, row) in enumerate(top_20.iterrows(), 1):
        # Listing header
        title = f"#{idx} - {row['typology']} • {row['area_m2']:.0f}m²"
        if row.get('is_aru'):
            title += " • 🏛️ ARU Zone"

        story.append(Paragraph(title, styles['ListingTitle']))

        # NER highlight
        ner_t1 = row['ner']
        ner_t2 = row.get('ner_tier2')

        if ner_t2:
            ner_text = f"💰 €{ner_t1:.0f}/mo (T1) • €{ner_t2:.0f}/mo (T2) • Gross: €{row['price']:.0f}"
        else:
            ner_text = f"💰 Net Effective Rent: €{ner_t1:.0f}/month (Gross: €{row['price']:.0f})"

        story.append(Paragraph(ner_text, styles['NERHighlight']))

        # Create two-column layout: Image on left, details on right
        content_data = []

        # Image
        image_path = row.get('image_path')
        if image_path and os.path.exists(image_path):
            try:
                img = Image(image_path, width=7*cm, height=5*cm)
                img.hAlign = 'LEFT'
            except Exception as e:
                print(f"  ⚠️ Error loading image {image_path}: {e}")
                img = Paragraph("<i>Image not available</i>", styles['Normal'])
        else:
            img = Paragraph("<i>Image not available</i>", styles['Normal'])

        # Details
        details_list = []

        # Location
        location = str(row.get('location', 'Location not specified'))[:60]
        if location != 'nan' and pd.notna(row.get('location')):
            details_list.append(f"<b>📍 Location:</b> {location}")

        # Amenities
        amenities = []
        if row.get('furnished'): amenities.append('Furnished')
        if row.get('balcony'): amenities.append('Balcony')
        if row.get('terrace'): amenities.append('Terrace')
        if row.get('ac'): amenities.append('AC')
        if row.get('elevator'): amenities.append('Elevator')
        if row.get('parking'): amenities.append('Parking')
        if row.get('renovated'): amenities.append('Renovated')

        if amenities:
            details_list.append(f"<b>✨ Amenities:</b> {', '.join(amenities)}")
        else:
            details_list.append(f"<b>✨ Amenities:</b> None listed")

        # Distance (if available)
        distance_to_work = row.get('distance_to_work_km')
        if pd.notna(distance_to_work):
            details_list.append(f"<b>🚶 Distance to Work:</b> {distance_to_work:.1f} km")

        # ARU bonus
        if row.get('is_aru'):
            details_list.append(f"<b>🏛️ ARU Bonus:</b> +20% subsidy")

        # Savings
        if ner_t2:
            savings_t2 = row['price'] - ner_t2
            details_list.append(f"<b>💵 Monthly Savings (T2):</b> €{savings_t2:.0f}")

        # URL
        url = str(row.get('url', ''))
        if url and url != 'nan':
            short_url = url.split('/')[-2] if '/imovel/' in url else url[:40]
            url_link = f'<link href="{url}" color="blue">View Listing ({short_url})</link>'
            details_list.append(f"<b>🔗 Link:</b> {url_link}")

        details_text = "<br/>".join(details_list)
        details = Paragraph(details_text, styles['ListingDetail'])

        # Create table for layout
        content_table = Table(
            [[img, details]],
            colWidths=[8*cm, 9*cm]
        )

        content_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))

        story.append(content_table)
        story.append(Spacer(1, 0.3*cm))

        # Separator line
        separator_table = Table([['']], colWidths=[17*cm])
        separator_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#ecf0f1')),
        ]))
        story.append(separator_table)
        story.append(Spacer(1, 0.4*cm))

        # Page break every 3 listings for better formatting
        if idx % 3 == 0 and idx < 20:
            story.append(PageBreak())

    # Build PDF
    doc.build(story)
    print(f"✅ Enhanced PDF report generated: {output_path}")

def main():
    print("=" * 80)
    print("ENHANCED PDF REPORT GENERATOR (WITH IMAGES)")
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
    import pandas as pd
    main()
