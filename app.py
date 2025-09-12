# app.py
import streamlit as st
import os
from dotenv import load_dotenv
from api_calls import get_company_data, generate_qualitative_analysis
from rules import apply_investment_rules
from pdf_generator import PDFReport  # <-- IMPORT OUR NEW PDF CLASS

# --- The Markdown generation function (still useful) ---
def generate_markdown_report(startup_name, company_data, llm_analysis, rules_feedback):
    # (This function code remains the same as before)
    name = company_data.get('name', startup_name)
    founded = company_data.get('foundedYear', 'N/A')
    location = f"{company_data.get('geo', {}).get('city', 'N/A')}, {company_data.get('geo', {}).get('country', 'N/A')}"
    employees = company_data.get('metrics', {}).get('employees', 'N/A')
    domain = company_data.get('domain', 'N/A')
    sector_industry = company_data.get('category', {}).get('sector', 'N/A')
    products = llm_analysis.get('products_services', 'N/A')
    market = llm_analysis.get('market_description', 'N/A')
    traction = llm_analysis.get('traction_analysis', 'N/A')
    highlights = llm_analysis.get('key_highlights', [])
    report = f"""
# Preliminary Investment Fit Report: {name}
---
## Company Details
- **Year Founded:** {founded}
- **HQ Location:** {location}
- **Team Strength:** {employees} employees
- **Website:** [{domain}](http://{domain})
## Sector & Activity
- **Sector/Industry:** {sector_industry}
---
## Products/Services Description
{products}
---
## Market Description
{market}
---
## Traction (Inferred)
{traction}
---
## Highlights
"""
    for item in highlights:
        report += f"- {item}\n"
    report += "\n---\n\n## Investment Fit (Based on Custom Rules)\n"
    for item in rules_feedback:
        report += f"- {item}\n"
    return report

# --- MAIN APP LOGIC (Starts here) ---
load_dotenv()

st.set_page_config(layout="wide", page_title="Investment Fit Report")
st.title("AI-Powered Investment Fit Report Generator")

if not os.getenv("PERPLEXITY_API_KEY") or not os.getenv("GROQ_API_KEY"):
    st.error("🚨 Missing API Keys! Please check your .env file.")
    st.stop()

st.sidebar.header("Inputs")
startup_name = st.sidebar.text_input("Startup Name", placeholder="e.g., Figma, Stripe, Perplexity")
sector = st.sidebar.text_input("Target Sector", value="SaaS")

if st.sidebar.button("Generate Report", type="primary"):
    if not startup_name:
        st.warning("Please enter a startup name.")
    else:
        with st.spinner(f"🚀 Generating report for {startup_name}..."):
            company_data = get_company_data(startup_name)
            if "error" in company_data:
                st.error(f"Layer 1 Error: {company_data['error']}")
                st.stop()
            
            llm_analysis = generate_qualitative_analysis(company_data)
            if "error" in llm_analysis:
                st.error(f"Layer 2 Error: {llm_analysis['error']}")
                st.stop()
            
            rules_feedback = apply_investment_rules(company_data, sector)

        st.success("Report Generated!")
        # ... (The rest of the display logic is the same) ...
        st.header(f"Analysis for: {company_data.get('name', startup_name)}")
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.subheader("Company Details (from Perplexity)")
            st.markdown(f"**Founded:** `{company_data.get('foundedYear', 'N/A')}`")
            st.markdown(f"**Location:** `{company_data.get('geo', {}).get('city', 'N/A')}, {company_data.get('geo', {}).get('country', 'N/A')}`")
            st.markdown(f"**Team Size:** `{company_data.get('metrics', {}).get('employees', 'N/A')}` employees")
            domain = company_data.get('domain')
            if domain and domain != "N/A" and '.' in domain:
                st.markdown(f"**Website:** [{domain}](http://{domain})")
            else:
                st.markdown("**Website:** `N/A`")
            st.subheader("Sector & Activity")
            st.markdown(f"**Sector/Industry:** `{company_data.get('category', {}).get('sector', 'N/A')}`")
            st.subheader("Investment Fit (Our Rules)")
            for item in rules_feedback:
                st.markdown(item)
        with col2:
            st.subheader("Products/Services Description (from Llama 3)")
            st.info(llm_analysis.get('products_services', 'N/A'))
            st.subheader("Market Description")
            st.info(llm_analysis.get('market_description', 'N/A'))
            st.subheader("Traction Analysis (Inferred)")
            st.info(llm_analysis.get('traction_analysis', 'N/A'))
            st.subheader("Key Highlights")
            for item in llm_analysis.get('key_highlights', []):
                st.markdown(f"- {item}")

        # --- DOWNLOAD BUTTONS SECTION ---
        st.subheader("Download Report")
        
        # --- PDF Download ---
        pdf = PDFReport()
        pdf_output = pdf.generate(startup_name, company_data, llm_analysis, rules_feedback)
        st.download_button(
            label="Download as PDF",
            data=pdf_output,
            file_name=f"Investment_Fit_Report_{startup_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        
        # --- Markdown Download ---
        markdown_report_string = generate_markdown_report(startup_name, company_data, llm_analysis, rules_feedback)
        st.download_button(
            label="Download as Markdown (.md)",
            data=markdown_report_string,
            file_name=f"Investment_Fit_Report_{startup_name.replace(' ', '_')}.md",
            mime="text/markdown"
        )