# pdf_generator.py
from fpdf import FPDF

class PDFReport(FPDF):
    def sanitize_text(self, text):
        """
        Replaces characters that are not supported by the default PDF font (latin-1)
        with a placeholder '?' to prevent crashes.
        """
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    def header(self):
        self.set_fill_color(65, 105, 225)
        self.rect(0, 0, 210, 25, 'F')
        self.set_y(10)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, self.sanitize_text(f"Preliminary Investment Fit Report: {self.company_name}"), 0, 1, 'C')
        self.ln(15)

    def create_section(self, title, body):
        """Creates a full, professionally-spaced section with robust cursor management."""
        self.set_x(self.l_margin)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, self.sanitize_text(title), 0, 1, 'L')
        self.set_draw_color(65, 105, 225)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(5)
        
        self.set_font('Arial', '', 10)
        if isinstance(body, list):
            for item in body:
                self.set_x(self.l_margin)
                clean_item = self.sanitize_text(item)
                self.multi_cell(w=0, h=5, text=f"- {clean_item}")
        else:
            self.set_x(self.l_margin)
            clean_body = self.sanitize_text(body)
            self.multi_cell(w=0, h=5, text=clean_body)
        
        self.ln(8)

    def generate(self, startup_name, company_data, llm_analysis, rules_feedback, investment_thesis):
        self.company_name = company_data.get('name', startup_name)
        self.add_page()
        
        geo = company_data.get('geo', {})
        company_details = (
            f"Year Founded: {company_data.get('foundedYear', 'N/A')}\n"
            f"HQ Location: {self.sanitize_text(geo.get('city', 'N/A'))}, {self.sanitize_text(geo.get('country', 'N/A'))}\n"
            f"Address: {self.sanitize_text(geo.get('address', 'N/A'))}\n"
            f"Website: {company_data.get('domain', 'N/A')}\n"
            f"Team Strength: {company_data.get('metrics', {}).get('employees', 'N/A')} employees"
        )
        self.create_section("Company Details", company_details)

        social_media = company_data.get('social_media', {})
        social_media_list = [f"{platform.capitalize()}: {link}" for platform, link in social_media.items()] if social_media else ["N/A"]
        self.create_section("Social Media", social_media_list)

        founders = company_data.get('founders', [])
        self.create_section("Founders", founders if founders else ["N/A"])

        key_investors = company_data.get('key_investors', [])
        self.create_section("Key Investors", key_investors if key_investors else ["N/A"])

        category = company_data.get('category', {})
        sector_activity = (
            f"Sector: {self.sanitize_text(category.get('sector', 'N/A'))}\n"
            f"Sub-sector: {self.sanitize_text(category.get('sub_sector', 'N/A'))}\n"
            f"Industry: {self.sanitize_text(category.get('industry', 'N/A'))}\n"
            f"Activity: {self.sanitize_text(category.get('activity', 'N/A'))}"
        )
        self.create_section("Sector & Activity", sector_activity)

        business_revenue = (
            f"Business Model: {self.sanitize_text(company_data.get('business_model', 'N/A'))}\n"
            f"Revenue Model: {self.sanitize_text(company_data.get('revenue_model', 'N/A'))}\n"
            f"Revenue Stream: {self.sanitize_text(company_data.get('revenue_stream', 'N/A'))}"
        )
        self.create_section("Business & Revenue", business_revenue)

        self.create_section("Products/Services Description", llm_analysis.get('products_services', 'N/A'))
        self.create_section("Market Description", llm_analysis.get('market_description', 'N/A'))
        self.create_section("Traction (Inferred)", llm_analysis.get('traction_analysis', 'N/A'))
        self.create_section("Highlights", llm_analysis.get('key_highlights', []))

        self.create_section("The Bull Case", investment_thesis.get('bull_case', 'N/A'))
        self.create_section("The Bear Case", investment_thesis.get('bear_case', 'N/A'))

        self.create_section("Investment Fit (Our Rules)", rules_feedback)
        
        return bytes(self.output())