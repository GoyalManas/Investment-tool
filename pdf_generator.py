# pdf_generator.py
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
        self.story = []

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
                    table_data.append([Paragraph(f"<b>{key}:</b>", self.styles['KeyStyle']), Paragraph(str(value), self.styles['ValueStyle'])])
                
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
            ('ALIGN', (0,0), (-1,-1), 'LEFT'), # Align text left in table
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), white),
            ('GRID', (0,0), (-1,-1), 1, gray)
        ])
        table.setStyle(style)

        # Add color coding for results
        for i, item in enumerate(rules_feedback, start=1):
            color = gray
            if item['type'] == 'positive': color = green
            elif item['type'] == 'negative': color = red
            elif item['type'] == 'neutral': color = orange
            style.add('BACKGROUND', (1,i), (1,i), color)
            style.add('TEXTCOLOR', (1,i), (1,i), white)

        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))


    def generate(self, startup_name, company_data, investment_decision, rules_feedback):
        self._add_header(company_data.get('name', startup_name))

        # Investment Decision
        if investment_decision and not investment_decision.get('error'):
            self._add_section("Investment Decision", {
                "Recommendation": investment_decision.get('recommendation', 'N/A'),
                "Score": f"{investment_decision.get('total_score', 'N/A')}/100"
            })

            reasons_to_invest = investment_decision.get('reasons_to_invest', [])
            if reasons_to_invest:
                self._add_section("Reasons to Invest", reasons_to_invest, is_sub_section=True)

            reasons_to_pass = investment_decision.get('reasons_to_pass', [])
            if reasons_to_pass:
                self._add_section("Reasons to Pass", reasons_to_pass, is_sub_section=True)

            critical_questions = investment_decision.get('critical_questions', [])
            if critical_questions:
                self._add_section("Critical Questions", critical_questions, is_sub_section=True)

        # Investment Fit Scorecard
        if rules_feedback:
            self._add_section("Investment Fit Scorecard", "")
            self._create_scorecard_table(rules_feedback)

        self.story.append(PageBreak())

        # Company Details
        company_details_data = {}
        if company_data.get('foundedYear') and company_data.get('foundedYear') != 'N/A':
            company_details_data["Year Founded"] = company_data.get('foundedYear')
        geo = company_data.get('geo', {})
        if geo.get('city') and geo.get('city') != 'N/A':
            company_details_data["HQ Location"] = f"{geo.get('city', 'N/A')}, {geo.get('country', 'N/A')}"
        if geo.get('address') and geo.get('address') != 'N/A':
            company_details_data["Address"] = geo.get('address')
        domain = company_data.get('domain', 'N/A')
        if domain != 'N/A':
            website_url = f"https://{domain}"
            company_details_data["Website"] = f"<link href='{website_url}'>{domain}</link>"
        if company_data.get('metrics', {}).get('employees') and company_data.get('metrics', {}).get('employees') != 'N/A':
            company_details_data["Team Strength"] = f"{company_data.get('metrics', {}).get('employees')} employees"
        if company_details_data:
            self._add_section("Company Details", company_details_data)

        # Social Media
        social_media = company_data.get('social_media', {})
        if social_media:
            social_media_content = []
            for platform, link in social_media.items():
                if link and link != 'N/A':
                    social_media_content.append(f"{platform.capitalize()}: <link href='{link}'>{link}</link>")
            if social_media_content:
                self._add_section("Social Media", social_media_content)

        # Founders
        founders_analysis = company_data.get('founders_analysis', {})
        if founders_analysis and founders_analysis.get('names_of_founders'):
            founders_content = {}
            if founders_analysis.get('names_of_founders'):
                founders_content["Founder(s)"] = ', '.join(founders_analysis.get('names_of_founders', []))
            if founders_analysis.get('complementarity') and founders_analysis.get('complementarity') != 'N/A':
                founders_content["Complementarity"] = founders_analysis.get('complementarity')
            if founders_analysis.get('key_competency') and founders_analysis.get('key_competency') != 'N/A':
                founders_content["Key Competency"] = founders_analysis.get('key_competency')
            if founders_analysis.get('prior_startup_experience') and founders_analysis.get('prior_startup_experience') != 'N/A':
                founders_content["Prior Experience"] = founders_analysis.get('prior_startup_experience')
            if founders_analysis.get('red_flags') and founders_analysis.get('red_flags') != 'N/A':
                founders_content["Red Flags"] = founders_analysis.get('red_flags')
            if founders_content:
                self._add_section("Founders", founders_content)

        # Key Investors
        key_investors = company_data.get('key_investors', [])
        if key_investors:
            self._add_section("Key Investors", key_investors)

        # Sector & Activity
        sector_activity_data = {}
        category = company_data.get('category', {})
        if category.get('sector') and category.get('sector') != 'N/A':
            sector_activity_data["Sector"] = category.get('sector')
        if category.get('sub_sector') and category.get('sub_sector') != 'N/A':
            sector_activity_data["Sub-sector"] = category.get('sub_sector')
        if category.get('industry') and category.get('industry') != 'N/A':
            sector_activity_data["Industry"] = category.get('industry')
        if category.get('activity') and category.get('activity') != 'N/A':
            sector_activity_data["Activity"] = category.get('activity')
        if sector_activity_data:
            self._add_section("Sector & Activity", sector_activity_data)

        # Business & Revenue
        business_revenue_data = {}
        if company_data.get('business_model') and company_data.get('business_model') != 'N/A':
            business_revenue_data["Business Model"] = company_data.get('business_model')
        if company_data.get('revenue_model') and company_data.get('revenue_model') != 'N/A':
            business_revenue_data["Revenue Model"] = company_data.get('revenue_model')
        if company_data.get('pricing_model') and company_data.get('pricing_model') != 'N/A':
            business_revenue_data["Pricing Model"] = company_data.get('pricing_model')
        if company_data.get('revenue_stream_diversified') is not None and company_data.get('revenue_stream_diversified') != 'N/A':
            business_revenue_data["Revenue Stream Diversified"] = str(company_data.get('revenue_stream_diversified'))
        if business_revenue_data:
            self._add_section("Business & Revenue", business_revenue_data)

        # Financials
        financials_data = {}
        if company_data.get('total_funding') and company_data.get('total_funding') != 'N/A':
            financials_data["Total Funding"] = company_data.get('total_funding')
        if company_data.get('last_funding_round') and company_data.get('last_funding_round') != 'N/A':
            financials_data["Last Funding Round"] = company_data.get('last_funding_round')
        if company_data.get('valuation') and company_data.get('valuation') != 'N/A':
            financials_data["Valuation"] = company_data.get('valuation')
        if company_data.get('revenue') and company_data.get('revenue') != 'N/A':
            financials_data["Revenue"] = company_data.get('revenue')
        if company_data.get('profitability') and company_data.get('profitability') != 'N/A':
            financials_data["Profitability"] = company_data.get('profitability')
        if financials_data:
            self._add_section("Financials", financials_data)

        # Market & Competition
        market_competition_data = {} 
        if company_data.get('market_description') and company_data.get('market_description') != 'N/A':
            market_competition_data["Market Description"] = company_data.get('market_description')
        if company_data.get('market_size') and company_data.get('market_size') != 'N/A':
            market_competition_data["Market Size"] = company_data.get('market_size')
        if company_data.get('market_growth_rate') and company_data.get('market_growth_rate') != 'N/A':
            market_competition_data["Market Growth Rate"] = company_data.get('market_growth_rate')
        if company_data.get('competitive_advantage') and company_data.get('competitive_advantage') != 'N/A':
            market_competition_data["Competitive Advantage"] = company_data.get('competitive_advantage')
        competitors = company_data.get('competitors', [])
        if competitors:
            market_competition_data["Competitors"] = ", ".join(competitors)
        if market_competition_data:
            self._add_section("Market & Competition", market_competition_data)

        # Product & Technology
        product_technology_data = {}
        if company_data.get('product_differentiation') and company_data.get('product_differentiation') != 'N/A':
            product_technology_data["Product Differentiation"] = company_data.get('product_differentiation')
        if company_data.get('innovative_solution') and company_data.get('innovative_solution') != 'N/A':
            product_technology_data["Innovative Solution"] = company_data.get('innovative_solution')
        patents = company_data.get('patents', [])
        if patents:
            product_technology_data["Patents"] = ", ".join(patents)
        if company_data.get('product_validation') and company_data.get('product_validation') != 'N/A':
            product_technology_data["Product Validation"] = company_data.get('product_validation')
        if company_data.get('technology_stack') and company_data.get('technology_stack') != 'N/A':
            product_technology_data["Technology Stack"] = company_data.get('technology_stack')
        if company_data.get('product_roadmap') and company_data.get('product_roadmap') != 'N/A':
            product_technology_data["Product Roadmap"] = company_data.get('product_roadmap')
        if product_technology_data:
            self._add_section("Product & Technology", product_technology_data)

        # Team
        team_data = {}
        key_hires = company_data.get('key_hires', [])
        if key_hires:
            team_data["Key Hires"] = ", ".join(key_hires)
        if company_data.get('employee_growth_rate') and company_data.get('employee_growth_rate') != 'N/A':
            team_data["Employee Growth Rate"] = company_data.get('employee_growth_rate')
        if company_data.get('glassdoor_rating') and company_data.get('glassdoor') != 'N/A':
            team_data["Glassdoor Rating"] = company_data.get('glassdoor_rating')
        if team_data:
            self._add_section("Team", team_data)

        self.story.append(PageBreak())

        # AI-Generated Analysis
        # This section is removed as per the new design

        # Build the PDF
        self.doc.build(self.story)
        pdf_value = self.buffer.getvalue()
        self.buffer.close()
        return pdf_value