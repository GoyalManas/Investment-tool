import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import navy, white, black, gray, red, green, orange
from reportlab.lib.units import inch

class Line(Flowable):
    """Draws a horizontal line."""
    def __init__(self, width, height=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height
    def draw(self):
        self.canv.line(0, self.height, self.width, self.height)

class PDFReport:
    def __init__(self, buffer=None):
        self.buffer = buffer if buffer else io.BytesIO()
        self.doc = SimpleDocTemplate(self.buffer, pagesize=(8.5*inch, 11*inch),
                                     leftMargin=0.75*inch, rightMargin=0.75*inch,
                                     topMargin=0.75*inch, bottomMargin=0.75*inch)
        self.styles = getSampleStyleSheet()
        
        # Modify Title style
        self.styles['Title'].fontName = 'Helvetica-Bold'
        self.styles['Title'].fontSize = 24
        self.styles['Title'].leading = 28
        self.styles['Title'].textColor = navy
        self.styles['Title'].alignment = TA_CENTER

        # Modify Heading2 for MainSection
        self.styles['h2'].fontName = 'Helvetica-Bold'
        self.styles['h2'].fontSize = 16
        self.styles['h2'].leading = 20
        self.styles['h2'].textColor = navy

        # Modify Heading3 for SubSection
        self.styles['h3'].fontName = 'Helvetica-Bold'
        self.styles['h3'].fontSize = 12
        self.styles['h3'].leading = 16
        self.styles['h3'].textColor = navy

        # Modify BodyText
        self.styles['BodyText'].fontName = 'Helvetica'
        self.styles['BodyText'].fontSize = 10
        self.styles['BodyText'].leading = 14

        # Modify Bullet
        self.styles['Bullet'].fontName = 'Helvetica'
        self.styles['Bullet'].fontSize = 10
        self.styles['Bullet'].leading = 14
        self.styles['Bullet'].leftIndent = 18

        # Add Key and Value styles
        self.styles.add(ParagraphStyle(name='Key', fontName='Helvetica-Bold', fontSize=10, leading=12))
        self.styles.add(ParagraphStyle(name='Value', fontName='Helvetica', fontSize=10, leading=12))

    def _add_header(self, company_name):
        # Add logo placeholder
        self.story.append(Paragraph("Your Logo Here", self.styles['Normal']))
        self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(Paragraph(f"Investment Memo: {company_name}", self.styles['Title']))
        self.story.append(Spacer(1, 0.2*inch))

    def _add_section(self, title, content=None, is_sub_section=False):
        self.story.append(Spacer(1, 0.15*inch))
        if is_sub_section:
            self.story.append(Paragraph(title, self.styles['h3']))
        else:
            self.story.append(Paragraph(title, self.styles['h2']))
            self.story.append(Line(7*inch)) # Horizontal line for main sections
        self.story.append(Spacer(1, 0.1*inch))

        if content:
            if isinstance(content, list):
                for item in content:
                    self.story.append(Paragraph(f"• {item}", self.styles['Bullet']))
                    self.story.append(Spacer(1, 0.05*inch))
            elif isinstance(content, str):
                self.story.append(Paragraph(content, self.styles['BodyText']))
            elif isinstance(content, dict):
                table_data = []
                for key, value in content.items():
                    # Ensure value is a string
                    if not isinstance(value, str):
                        value = str(value)
                    # Handle links
                    if value.startswith('http'):
                        value = f"<link href='{value}'>{value}</link>"
                    table_data.append([Paragraph(f"<b>{key}:</b>", self.styles['Key']), Paragraph(value, self.styles['Value'])])
                
                if table_data:
                    table = Table(table_data, colWidths=[2*inch, 5*inch])
                    table.setStyle(TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('LEFTPADDING', (0,0), (-1,-1), 0),
                        ('RIGHTPADDING', (0,0), (-1,-1), 0),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                        ('TOPPADDING', (0,0), (-1,-1), 2),
                    ]))
                    self.story.append(table)
            self.story.append(Spacer(1, 0.1*inch))

    def _create_scorecard_table(self, rules_feedback):
        data = [
            [
                Paragraph("<b>Criteria</b>", self.styles['Key']), 
                Paragraph("<b>Result</b>", self.styles['Key']), 
                Paragraph("<b>Comment</b>", self.styles['Key'])
            ]
        ]
        for item in rules_feedback:
            criteria = item['text'].split(':')[0]
            comment = ':'.join(item['text'].split(':')[1:]).strip()
            result = item['type'].upper()
            data.append([
                Paragraph(criteria, self.styles['Value']), 
                Paragraph(result, self.styles['Value']), 
                Paragraph(comment, self.styles['Value'])
            ])

        table = Table(data, colWidths=[1.75*inch, 0.75*inch, 4.5*inch])
        
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), navy),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), white),
            ('GRID', (0,0), (-1,-1), 1, gray)
        ])
        table.setStyle(style)

        for i, item in enumerate(rules_feedback, start=1):
            color = gray
            if item['type'] == 'positive': color = green
            elif item['type'] == 'negative': color = red
            elif item['type'] == 'neutral': color = orange
            style.add('BACKGROUND', (1,i), (1,i), color)
            style.add('TEXTCOLOR', (1,i), (1,i), white)

        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))

    def _add_investment_thesis(self, investment_thesis):
        if investment_thesis and not investment_thesis.get('error'):
            self._add_section("Investment Thesis")
            self._add_section("Investment Summary", investment_thesis.get('investment_summary', 'N/A'), is_sub_section=True)
            self._add_section("Key Risks", investment_thesis.get('key_risks', 'N/A'), is_sub_section=True)
            self._add_section("Investment Recommendation", investment_thesis.get('investment_recommendation', 'N/A'), is_sub_section=True)

    def _add_llm_analysis(self, llm_analysis):
        if llm_analysis and not llm_analysis.get('error'):
            self.story.append(PageBreak())
            self._add_section("AI-Generated Analysis")
            self._add_section("SWOT Analysis", llm_analysis.get('swot_analysis', 'N/A'), is_sub_section=True)
            self._add_section("Competitive Landscape", llm_analysis.get('competitive_landscape', 'N/A'), is_sub_section=True)
            self._add_section("TAM Analysis", llm_analysis.get('tam_analysis', 'N/A'), is_sub_section=True)
            highlights = llm_analysis.get('key_highlights', [])
            if highlights:
                self._add_section("Key Highlights", highlights, is_sub_section=True)

    def _add_founder_analysis(self, founders_analysis):
        if founders_analysis and not founders_analysis.get('error'):
            self.story.append(PageBreak())
            self._add_section("Founder Analysis")
            for key, value in founders_analysis.items():
                self._add_section(key.replace('_', ' ').title(), value, is_sub_section=True)

    def _add_product_analysis(self, product_analysis):
        if product_analysis and not product_analysis.get('error'):
            self.story.append(PageBreak())
            self._add_section("Product Analysis")
            for key, value in product_analysis.items():
                self._add_section(key.replace('_', ' ').title(), value, is_sub_section=True)

    def _add_company_details(self, company_data):
        self._add_section("Company Overview")

        # Left column content
        left_column = []
        geo = company_data.get('geo', {})
        domain = company_data.get('domain', 'N/A')
        website_url = f"https://{domain}" if domain != 'N/A' else '#'
        
        left_column.append(Paragraph("<b>Company Details</b>", self.styles['h3']))
        left_column.append(Spacer(1, 0.1*inch))
        company_details_data = [
            [Paragraph("<b>Year Founded:</b>", self.styles['Key']), Paragraph(str(company_data.get('foundedYear', 'N/A')), self.styles['Value'])],
            [Paragraph("<b>HQ Location:</b>", self.styles['Key']), Paragraph(f"{geo.get('city', 'N/A')}, {geo.get('country', 'N/A')}", self.styles['Value'])],
            [Paragraph("<b>Website:</b>", self.styles['Key']), Paragraph(f"<link href='{website_url}'>{domain}</link>", self.styles['Value'])],
            [Paragraph("<b>Team Strength:</b>", self.styles['Key']), Paragraph(f"{company_data.get('metrics', {}).get('employees', 'N/A')} employees", self.styles['Value'])],
        ]
        table = Table(company_details_data, colWidths=[1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        left_column.append(table)


        left_column.append(Spacer(1, 0.2*inch))
        
        founders_analysis = company_data.get('founders_analysis', {})
        if founders_analysis and founders_analysis.get('names_of_founders'):
            left_column.append(Paragraph("<b>Founders</b>", self.styles['h3']))
            left_column.append(Spacer(1, 0.1*inch))
            founders_content = [
                [Paragraph("<b>Founder(s):</b>", self.styles['Key']), Paragraph(', '.join(founders_analysis.get('names_of_founders', [])), self.styles['Value'])],
                [Paragraph("<b>Complementarity:</b>", self.styles['Key']), Paragraph(founders_analysis.get('complementarity', 'N/A'), self.styles['Value'])],
                [Paragraph("<b>Key Competency:</b>", self.styles['Key']), Paragraph(founders_analysis.get('key_competency', 'N/A'), self.styles['Value'])],
                [Paragraph("<b>Prior Experience:</b>", self.styles['Key']), Paragraph(founders_analysis.get('prior_startup_experience', 'N/A'), self.styles['Value'])],
                [Paragraph("<b>Red Flags:</b>", self.styles['Key']), Paragraph(founders_analysis.get('red_flags', 'N/A'), self.styles['Value'])],
            ]
            table = Table(founders_content, colWidths=[1.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 2),
            ]))
            left_column.append(table)

        # Right column content
        right_column = []
        key_investors = company_data.get('key_investors', [])
        if key_investors:
            right_column.append(Paragraph("<b>Key Investors</b>", self.styles['h3']))
            right_column.append(Spacer(1, 0.1*inch))
            for investor in key_investors:
                right_column.append(Paragraph(f"• {investor}", self.styles['Bullet']))
                right_column.append(Spacer(1, 0.05*inch))

        # Create table with two columns
        table_data = [[left_column, right_column]]
        table = Table(table_data, colWidths=[4*inch, 3*inch])
        table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        self.story.append(table)

    def _add_business_details(self, company_data):
        # Sector & Activity
        category = company_data.get('category', {})
        sector_activity_data = {
            "Sector": category.get('sector', 'N/A'),
            "Sub-sector": category.get('sub_sector', 'N/A'),
            "Industry": category.get('industry', 'N/A'),
            "Activity": category.get('activity', 'N/A'),
        }
        self._add_section("Sector & Activity", sector_activity_data, is_sub_section=True)

        # Business & Revenue
        business_revenue_data = {
            "Business Model": company_data.get('business_model', 'N/A'),
            "Revenue Model": company_data.get('revenue_model', 'N/A'),
            "Pricing Model": company_data.get('pricing_model', 'N/A'),
            "Revenue Stream Diversified": company_data.get('revenue_stream_diversified', 'N/A'),
        }
        self._add_section("Business & Revenue", business_revenue_data, is_sub_section=True)

    def _add_financial_details(self, company_data):
        self._add_section("Financials", is_sub_section=True)
        financials_data = [
            [Paragraph("<b>Total Funding:</b>", self.styles['Key']), Paragraph(company_data.get('total_funding', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Last Funding Round:</b>", self.styles['Key']), Paragraph(company_data.get('last_funding_round', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Valuation:</b>", self.styles['Key']), Paragraph(company_data.get('valuation', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Revenue:</b>", self.styles['Key']), Paragraph(company_data.get('revenue', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Profitability:</b>", self.styles['Key']), Paragraph(company_data.get('profitability', 'N/A'), self.styles['Value'])],
        ]
        table = Table(financials_data, colWidths=[2*inch, 5*inch])
        table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        self.story.append(table)

    def _add_market_and_product_details(self, company_data):
        self._add_section("Market & Competition", is_sub_section=True)
        market_competition_data = [
            [Paragraph("<b>Market Size:</b>", self.styles['Key']), Paragraph(company_data.get('market_size', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Market Growth Rate:</b>", self.styles['Key']), Paragraph(company_data.get('market_growth_rate', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Competitive Advantage:</b>", self.styles['Key']), Paragraph(company_data.get('competitive_advantage', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Competitors:</b>", self.styles['Key']), Paragraph(", ".join(company_data.get('competitors', []) if company_data.get('competitors') else ['N/A']), self.styles['Value'])],
        ]
        table = Table(market_competition_data, colWidths=[2*inch, 5*inch])
        table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        self.story.append(table)

        self._add_section("Product & Technology", is_sub_section=True)
        product_technology_data = [
            [Paragraph("<b>Product Differentiation:</b>", self.styles['Key']), Paragraph(company_data.get('product_differentiation', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Innovative Solution:</b>", self.styles['Key']), Paragraph(company_data.get('innovative_solution', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Patents:</b>", self.styles['Key']), Paragraph(", ".join(company_data.get('patents', []) if company_data.get('patents') else ['N/A']), self.styles['Value'])],
            [Paragraph("<b>Product Validation:</b>", self.styles['Key']), Paragraph(company_data.get('product_validation', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Technology Stack:</b>", self.styles['Key']), Paragraph(company_data.get('technology_stack', 'N/A'), self.styles['Value'])],
            [Paragraph("<b>Product Roadmap:</b>", self.styles['Key']), Paragraph(company_data.get('product_roadmap', 'N/A'), self.styles['Value'])],
        ]
        table = Table(product_technology_data, colWidths=[2*inch, 5*inch])
        table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        self.story.append(table)

    def generate(self, startup_name, company_data, llm_analysis, rules_feedback, investment_thesis, founders_analysis, product_analysis):
        self.story = []
        self._add_header(company_data.get('name', startup_name))

        # Page 1: Company Overview
        self._add_company_details(company_data)
        self._add_business_details(company_data)
        self._add_financial_details(company_data)
        self._add_market_and_product_details(company_data)

        # Page 2: Founder Analysis
        self._add_founder_analysis(founders_analysis)

        # Page 3: Product Analysis
        self._add_product_analysis(product_analysis)

        # Page 4: AI Analysis
        self._add_llm_analysis(llm_analysis)

        # Page 5: Investment Thesis and Scorecard
        self._add_investment_thesis(investment_thesis)
        if rules_feedback:
            self._add_section("Investment Fit Scorecard")
            self._create_scorecard_table(rules_feedback)

        # Build the PDF
        self.doc.build(self.story)
        pdf_value = self.buffer.getvalue()
        self.buffer.close()
        return pdf_value