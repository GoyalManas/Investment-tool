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
        self.set_y(5)
        self.set_font('Arial', 'B', 18)
        self.set_text_color(255, 255, 255)
        # self.company_name is set in the generate() method before add_page() is called
        self.cell(0, 10, self.sanitize_text(self.company_name), 0, 1, 'L')
        self.set_y(15)
        self.set_font('Arial', '', 14)
        # The subtitle is included in the company_name, so this cell can be empty
        self.cell(0, 10, '', 0, 1, 'L')
        self.ln(15)

    def create_section(self, title, body):
        """Creates a full, professionally-spaced section with robust cursor management."""
        # --- Explicitly set cursor to the left margin to start the section ---
        self.set_x(self.l_margin)
        
        # --- Title ---
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, self.sanitize_text(title), 0, 1, 'L')
        
        # --- Underline ---
        self.set_draw_color(65, 105, 225)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(5)
        
        # --- Body ---
        self.set_font('Arial', '', 10)
        if isinstance(body, list):
            for item in body:
                # Explicitly reset cursor for every list item to prevent crashes
                self.set_x(self.l_margin)
                clean_item = self.sanitize_text(item)
                # The 'w=0' makes it use the full page width from the current x position
                self.multi_cell(w=0, h=5, text=f"- {clean_item}")
        else:
            self.set_x(self.l_margin) # Also reset for single blocks
            clean_body = self.sanitize_text(body)
            self.multi_cell(w=0, h=5, text=clean_body)
        
        # --- Professional Spacing ---
        self.ln(10)

    def generate(self, startup_name, company_data, llm_analysis, rules_feedback):
        self.company_name = company_data.get('name', startup_name)
        self.add_page()
        
        company_overview = (
            f"Year founded: {company_data.get('foundedYear', 'N/A')}\n"
            f"HQ Location: {self.sanitize_text(company_data.get('geo', {}).get('city', 'N/A'))}, {self.sanitize_text(company_data.get('geo', {}).get('country', 'N/A'))}\n"
            f"Website: {company_data.get('domain', 'N/A')}\n"
            f"Team strength: {company_data.get('metrics', {}).get('employees', 'N/A')} employees\n"
            f"Sector: {self.sanitize_text(company_data.get('category', {}).get('sector', 'N/A'))}"
        )
        self.create_section("Company Overview", company_overview)

        self.create_section("Products/Services Description", llm_analysis.get('products_services', 'N/A'))
        self.create_section("Market Description", llm_analysis.get('market_description', 'N/A'))
        self.create_section("Traction (Inferred)", llm_analysis.get('traction_analysis', 'N/A'))
        self.create_section("Highlights", llm_analysis.get('key_highlights', []))
        
        cleaned_rules = [
            item.replace('✅', '').replace('⚠️', '').replace('ℹ️', '').replace('**', '').strip()
            for item in rules_feedback
        ]
        self.create_section("Investment Fit", cleaned_rules)
        
        return bytes(self.output())