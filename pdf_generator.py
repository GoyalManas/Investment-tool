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
        self.styles.add(ParagraphStyle(name='KeyStyle', fontName='Helvetica-Bold', fontSize=10, leading=12))
        self.styles.add(ParagraphStyle(name='ValueStyle', fontName='Helvetica', fontSize=10, leading=12))
        self.styles.add(ParagraphStyle(name='BulletStyle', fontName='Helvetica', fontSize=10, leading=12, leftIndent=18))

    def _add_header(self, company_name):
        style = self.styles['h1']
        style.textColor = navy
        style.alignment = TA_CENTER
        self.story.append(Paragraph(f"Investment Memo: {company_name}", style))
        self.story.append(Spacer(1, 0.2*inch))

    def _add_section(self, title, content=None, is_sub_section=False):
        self.story.append(Spacer(1, 0.15*inch))
        if is_sub_section:
            title_style = self.styles['h3']
            title_style.textColor = navy
            self.story.append(Paragraph(title, title_style))
        else:
            title_style = self.styles['h2']
            title_style.textColor = navy
            self.story.append(Paragraph(title, title_style))
            self.story.append(Line(7*inch)) # Horizontal line for main sections
        self.story.append(Spacer(1, 0.1*inch))

        if content:
            if isinstance(content, list):
                for item in content:
                    self.story.append(Paragraph(f"• {item}", self.styles['BulletStyle']))
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
                    table_data.append([Paragraph(f"<b>{key}:</b>", self.styles['KeyStyle']), Paragraph(value, self.styles['ValueStyle'])])
                
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
                Paragraph("<b>Criteria</b>", self.styles['KeyStyle']), 
                Paragraph("<b>Result</b>", self.styles['KeyStyle']), 
                Paragraph("<b>Comment</b>", self.styles['KeyStyle'])
            ]
        ]
        for item in rules_feedback:
            criteria = item['text'].split(':')[0]
            comment = ':'.join(item['text'].split(':')[1:]).strip()
            result = item['type'].upper()
            data.append([
                Paragraph(criteria, self.styles['ValueStyle']), 
                Paragraph(result, self.styles['ValueStyle']), 
                Paragraph(comment, self.styles['ValueStyle'])
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

    def _add_company_details(self, company_data):
        self.story.append(PageBreak())
        self._add_section("Company Overview")

        # Company Details
        geo = company_data.get('geo', {})
        domain = company_data.get('domain', 'N/A')
        website_url = f"https://{domain}" if domain != 'N/A' else '#'
        company_details_data = {
            "Year Founded": company_data.get('foundedYear', 'N/A'),
            "HQ Location": f"{geo.get('city', 'N/A')}, {geo.get('country', 'N/A')}",
            "Website": website_url,
            "Team Strength": f"{company_data.get('metrics', {}).get('employees', 'N/A')} employees",
        }
        self._add_section("Company Details", company_details_data, is_sub_section=True)

        # Founders
        founders_analysis = company_data.get('founders_analysis', {})
        if founders_analysis and founders_analysis.get('names_of_founders'):
            founders_content = {
                "Founder(s)": ', '.join(founders_analysis.get('names_of_founders', [])),
                "Complementarity": founders_analysis.get('complementarity', 'N/A'),
                "Key Competency": founders_analysis.get('key_competency', 'N/A'),
                "Prior Experience": founders_analysis.get('prior_startup_experience', 'N/A'),
                "Red Flags": founders_analysis.get('red_flags', 'N/A'),
            }
            self._add_section("Founders", founders_content, is_sub_section=True)

        # Key Investors
        key_investors = company_data.get('key_investors', [])
        if key_investors:
            self._add_section("Key Investors", key_investors, is_sub_section=True)

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
        financials_data = {
            "Total Funding": company_data.get('total_funding', 'N/A'),
            "Last Funding Round": company_data.get('last_funding_round', 'N/A'),
            "Valuation": company_data.get('valuation', 'N/A'),
            "Revenue": company_data.get('revenue', 'N/A'),
            "Profitability": company_data.get('profitability', 'N/A'),
        }
        self._add_section("Financials", financials_data, is_sub_section=True)

    def _add_market_and_product_details(self, company_data):
        # Market & Competition
        market_competition_data = {
            "Market Size": company_data.get('market_size', 'N/A'),
            "Market Growth Rate": company_data.get('market_growth_rate', 'N/A'),
            "Competitive Advantage": company_data.get('competitive_advantage', 'N/A'),
            "Competitors": ", ".join(company_data.get('competitors', []) if company_data.get('competitors') else ['N/A']),
        }
        self._add_section("Market & Competition", market_competition_data, is_sub_section=True)

        # Product & Technology
        product_technology_data = {
            "Product Differentiation": company_data.get('product_differentiation', 'N/A'),
            "Innovative Solution": company_data.get('innovative_solution', 'N/A'),
            "Patents": ", ".join(company_data.get('patents', []) if company_data.get('patents') else ['N/A']),
            "Product Validation": company_data.get('product_validation', 'N/A'),
            "Technology Stack": company_data.get('technology_stack', 'N/A'),
            "Product Roadmap": company_data.get('product_roadmap', 'N/A'),
        }
        self._add_section("Product & Technology", product_technology_data, is_sub_section=True)

    def generate(self, startup_name, company_data, llm_analysis, rules_feedback, investment_thesis):
        self.story = []
        self._add_header(company_data.get('name', startup_name))

        # Page 1: Thesis and Scorecard
        self._add_investment_thesis(investment_thesis)
        if rules_feedback:
            self._add_section("Investment Fit Scorecard")
            self._create_scorecard_table(rules_feedback)

        # Page 2: AI Analysis
        self._add_llm_analysis(llm_analysis)

        # Page 3: Company Details
        self._add_company_details(company_data)
        self._add_business_details(company_data)
        self._add_financial_details(company_data)
        self._add_market_and_product_details(company_data)

        # Build the PDF
        self.doc.build(self.story)
        pdf_value = self.buffer.getvalue()
        self.buffer.close()
        return pdf_value