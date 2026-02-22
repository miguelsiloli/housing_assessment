"""
PDF Report Generator for NER Analysis
Uses ReportLab to create professional PDF reports with tables
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import pandas as pd
from reportlab.pdfgen import canvas


class PDFReportGenerator:
    """Generate PDF reports for NER analysis"""

    def __init__(self, output_path: str):
        """
        Args:
            output_path: Path where PDF will be saved
        """
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        self.styles = getSampleStyleSheet()
        self.story = []

        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))

        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            fontSize=9,
            textColor=colors.HexColor('#7f8c8d'),
        ))

        self.styles.add(ParagraphStyle(
            name='MetricValue',
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        ))

    def add_title(self, title: str, subtitle: str = None):
        """Add report title"""
        self.story.append(Paragraph(title, self.styles['CustomTitle']))
        if subtitle:
            self.story.append(Paragraph(subtitle, self.styles['Normal']))
        self.story.append(Spacer(1, 0.5*cm))

    def add_heading(self, text: str):
        """Add section heading"""
        self.story.append(Paragraph(text, self.styles['CustomHeading']))

    def add_summary_box(self, stats: dict):
        """Add executive summary box with key metrics"""

        has_tier2 = 'avg_ner_tier2' in stats

        if has_tier2:
            data = [
                ['Total', 'Filtered', 'Avg Gross', 'Avg NER (T1)', 'Avg NER (T2)', 'Avg Discount', 'ARU Zones'],
                [
                    f"{stats['total_apartments']}",
                    f"{stats['filtered_apartments']}",
                    f"€{stats['avg_gross_rent']:.0f}",
                    f"€{stats['avg_ner']:.0f}",
                    f"€{stats['avg_ner_tier2']:.0f}",
                    f"{stats['avg_discount_pct']:.1f}%",
                    f"{stats['aru_count']} ({stats['aru_percentage']:.1f}%)"
                ]
            ]
            col_widths = [2.5*cm, 2.5*cm, 2.8*cm, 3*cm, 3*cm, 3*cm, 4*cm]
        else:
            data = [
                ['Total Apartments', 'Filtered (≥30m²)', 'Avg Gross Rent', 'Avg NER', 'Avg Discount', 'ARU Zones'],
                [
                    f"{stats['total_apartments']}",
                    f"{stats['filtered_apartments']}",
                    f"€{stats['avg_gross_rent']:.0f}",
                    f"€{stats['avg_ner']:.0f}",
                    f"{stats['avg_discount_pct']:.1f}%",
                    f"{stats['aru_count']} ({stats['aru_percentage']:.1f}%)"
                ]
            ]
            col_widths = [3.5*cm, 3.5*cm, 3.5*cm, 3*cm, 3*cm, 4*cm]

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Data row
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ecf0f1')),
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 11),
            ('TOPPADDING', (0, 1), (-1, 1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))

    def add_top_apartments_table(self, df: pd.DataFrame, top_n: int = 20):
        """Add table of top N apartments"""

        self.add_heading(f'Top {top_n} Apartments by Net Effective Rent')

        # Check if we have Tier 2 data
        has_tier2 = 'ner_tier2' in df.columns

        # Prepare data
        if has_tier2:
            headers = ['#', 'NER\n(T1)', 'NER\n(T2)', 'Gross', 'Type', 'Area', 'Location', 'ARU', 'URL']
        else:
            headers = ['#', 'NER', 'Gross', 'Discount', 'Type', 'Area', 'Location', 'ARU', 'URL']

        rows = [headers]

        for idx, (i, row) in enumerate(df.head(top_n).iterrows(), 1):
            # Format location
            location = str(row.get('location', ''))[:25]
            if pd.isna(row.get('location')) or location == 'nan':
                location = '-'

            # ARU indicator
            aru = '🏛️' if row.get('is_aru', False) else ''

            # Extract listing ID from URL
            url = str(row.get('url', ''))
            if 'idealista.pt/imovel/' in url:
                listing_id = url.split('/')[-2]
                short_url = f".../{listing_id}/"
            else:
                short_url = '-'

            if has_tier2:
                rows.append([
                    str(idx),
                    f"€{row['ner']:.0f}",
                    f"€{row['ner_tier2']:.0f}",
                    f"€{row['price']:.0f}",
                    row['typology'],
                    f"{row['area_m2']:.0f}m²",
                    location,
                    aru,
                    short_url
                ])
            else:
                rows.append([
                    str(idx),
                    f"€{row['ner']:.0f}",
                    f"€{row['price']:.0f}",
                    f"{row['discount_pct']:.1f}%",
                    row['typology'],
                    f"{row['area_m2']:.0f}m²",
                    location,
                    aru,
                    short_url
                ])

        # Create table with adjusted column widths for landscape
        if has_tier2:
            col_widths = [0.7*cm, 1.4*cm, 1.4*cm, 1.4*cm, 1.2*cm, 1.4*cm, 5.2*cm, 0.8*cm, 2.5*cm]
        else:
            col_widths = [0.8*cm, 1.6*cm, 1.6*cm, 1.8*cm, 1.2*cm, 1.6*cm, 5*cm, 0.8*cm, 2.5*cm]

        table = Table(rows, colWidths=col_widths)

        # Styling
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Rank
            ('ALIGN', (1, 1), (3, -1), 'RIGHT'),   # NER, Gross, Discount
            ('ALIGN', (4, 1), (5, -1), 'CENTER'),  # Type, Area
            ('ALIGN', (6, 1), (6, -1), 'LEFT'),    # Location
            ('ALIGN', (7, 1), (-1, -1), 'CENTER'), # ARU, Amenities, Distance

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Top padding for data rows
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))

    def add_category_table(self, df: pd.DataFrame, title: str, max_rows: int = 5):
        """Add a category table (e.g., furnished T1s, with parking)"""

        if len(df) == 0:
            return

        self.add_heading(title)

        has_tier2 = 'ner_tier2' in df.columns

        if has_tier2:
            headers = ['#', 'NER (T1)', 'NER (T2)', 'Gross', 'Type', 'Area', 'Location', 'Amenities']
        else:
            headers = ['#', 'NER', 'Gross', 'Type', 'Area', 'Location', 'Amenities']

        rows = [headers]

        for idx, (i, row) in enumerate(df.head(max_rows).iterrows(), 1):
            # Get amenities
            amenities = []
            if row.get('furnished'): amenities.append('Furn')
            if row.get('parking'): amenities.append('Park')
            if row.get('elevator'): amenities.append('Elev')
            if row.get('ac'): amenities.append('AC')
            if row.get('renovated'): amenities.append('Renov')

            amenity_str = ', '.join(amenities) if amenities else '-'

            location = str(row.get('location', ''))[:28]
            if pd.isna(row.get('location')) or location == 'nan':
                location = '-'

            if has_tier2:
                rows.append([
                    str(idx),
                    f"€{row['ner']:.0f}",
                    f"€{row['ner_tier2']:.0f}",
                    f"€{row['price']:.0f}",
                    row['typology'],
                    f"{row['area_m2']:.0f}m²",
                    location,
                    amenity_str
                ])
            else:
                rows.append([
                    str(idx),
                    f"€{row['ner']:.0f}",
                    f"€{row['price']:.0f}",
                    row['typology'],
                    f"{row['area_m2']:.0f}m²",
                    location,
                    amenity_str
                ])

        if has_tier2:
            col_widths = [0.8*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.3*cm, 1.8*cm, 5.5*cm, 4.5*cm]
        else:
            col_widths = [1*cm, 2*cm, 2*cm, 1.5*cm, 2*cm, 6*cm, 5*cm]

        table = Table(rows, colWidths=col_widths)

        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),

            # Data
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
            ('ALIGN', (3, 1), (4, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.3*cm))

    def add_comparison_table(self, comparison: dict):
        """Add ARU vs Non-ARU comparison table"""

        self.add_heading('ARU Zone Impact Analysis')

        headers = ['Category', 'Count', 'Avg NER', 'Avg Discount']
        data = [
            headers,
            [
                '🏛️ ARU Zones',
                str(comparison['aru']['count']),
                f"€{comparison['aru']['avg_ner']:.0f}",
                f"{comparison['aru']['avg_discount']:.1f}%"
            ],
            [
                'Non-ARU',
                str(comparison['non_aru']['count']),
                f"€{comparison['non_aru']['avg_ner']:.0f}",
                f"{comparison['non_aru']['avg_discount']:.1f}%"
            ]
        ]

        if comparison['aru']['count'] > 0 and comparison['non_aru']['count'] > 0:
            savings = comparison['non_aru']['avg_ner'] - comparison['aru']['avg_ner']
            data.append([
                '💰 ARU Advantage',
                '-',
                f"€{savings:.0f}/mo",
                '-'
            ])

        table = Table(data, colWidths=[5*cm, 3*cm, 3*cm, 3*cm])

        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e67e22')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),

            # Data
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fef5e7'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))

    def add_size_analysis_table(self, size_data: dict):
        """Add size category analysis table"""

        self.add_heading('Analysis by Size Category')

        headers = ['Size Range', 'Count', 'Best NER', 'Avg NER']
        rows = [headers]

        for category, data in size_data.items():
            if data['count'] > 0:
                rows.append([
                    data['range'],
                    str(data['count']),
                    f"€{data['best_ner']:.0f}",
                    f"€{data['avg_ner']:.0f}"
                ])

        table = Table(rows, colWidths=[4*cm, 3*cm, 3*cm, 3*cm])

        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),

            # Data
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4ecf7')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))

    def add_url_reference_page(self, df: pd.DataFrame, top_n: int = 20):
        """Add a dedicated page with full URLs for easy access"""

        self.story.append(PageBreak())
        self.add_heading('📋 Apartment Listing URLs - Top 20')

        # Create URL table
        headers = ['#', 'NER (T1)', 'Type', 'Area', 'Full URL']
        rows = [headers]

        for idx, (i, row) in enumerate(df.head(top_n).iterrows(), 1):
            url = str(row.get('url', ''))
            if pd.isna(row.get('url')) or url == 'nan':
                url = 'URL not available'

            # Create clickable link in paragraph
            url_para = f'<link href="{url}" color="blue">{url}</link>'

            rows.append([
                str(idx),
                f"€{row['ner']:.0f}",
                row['typology'],
                f"{row['area_m2']:.0f}m²",
                Paragraph(url_para, self.styles['Normal'])
            ])

        col_widths = [1*cm, 2*cm, 1.5*cm, 2*cm, 14*cm]
        table = Table(rows, colWidths=col_widths)

        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Data rows
            ('FONTSIZE', (0, 1), (3, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Rank
            ('ALIGN', (1, 1), (3, -1), 'CENTER'),  # NER, Type, Area
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),    # URL
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Alternating colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.3*cm))

        # Add note about clicking URLs
        note = Paragraph(
            "<b>Note:</b> URLs are clickable in PDF viewers. Click to open listings directly in your browser.",
            self.styles['Normal']
        )
        self.story.append(note)

    def add_footer_notes(self, has_tier2: bool = False):
        """Add footer notes about methodology"""

        self.story.append(Spacer(1, 0.5*cm))

        notes = [
            "<b>Notes:</b>",
            "• <b>NER (Net Effective Rent):</b> Actual monthly cost after Porta 65 subsidy + IRS credit",
            "• <b>ARU (🏛️):</b> Urban Rehabilitation Area - receives +20% subsidy bonus",
        ]

        if has_tier2:
            notes.extend([
                "• <b>Tier 1 (T1):</b> Best case scenario - 50% base subsidy (optimistic)",
                "• <b>Tier 2 (T2):</b> Realistic scenario - 40% base subsidy (more conservative)",
                "• <b>Approval tier:</b> Depends on IHRU scoring (income, household, effort rate)",
            ])
        else:
            notes.append("• <b>Assumptions:</b> 1st tier approval (50% base subsidy), Year 1, no dependents")

        notes.extend([
            "• <b>Subsidy cap:</b> Capped at Reference Maximum Rent (RMR) for each typology",
            "• <b>IRS Credit:</b> €75/month - claimed on annual tax return",
            "• <b>Year 1 only:</b> Subsidies decrease in subsequent years (Y2: -15%, Y3-5: -25%)",
            "• <b>URL Reference:</b> Full clickable URLs available on dedicated page",
            f"• <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])

        for note in notes:
            self.story.append(Paragraph(note, self.styles['Normal']))
            self.story.append(Spacer(1, 0.1*cm))

    def build(self):
        """Build and save the PDF"""
        self.doc.build(self.story)
        print(f"✅ PDF report generated: {self.output_path}")
