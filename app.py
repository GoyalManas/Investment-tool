# app.py
import streamlit as st
import os
from dotenv import load_dotenv
from api_calls import get_company_data, generate_qualitative_analysis, generate_investment_thesis
from rules import apply_investment_rules
from pdf_generator import PDFReport

# --- The Markdown generation function ---
def generate_markdown_report(startup_name, company_data, llm_analysis, rules_feedback, investment_thesis):
    name = company_data.get('name', startup_name)
    geo = company_data.get('geo', {})
    category = company_data.get('category', {})
    social_media = company_data.get('social_media', {})
    
    report = f'''
# Preliminary Investment Fit Report: {name}

---

## Company Details
- **Year Founded:** {company_data.get('foundedYear', 'N/A')}
- **HQ Location:** {geo.get('city', 'N/A')}, {geo.get('country', 'N/A')}
- **Address:** {geo.get('address', 'N/A')}
- **Website:** [{company_data.get('domain', 'N/A')}]({company_data.get('domain', 'N/A')})
- **Team Strength:** {company_data.get('metrics', {}).get('employees', 'N/A')} employees

## Social Media
'''
    if social_media:
        for platform, link in social_media.items():
            report += f"- **{platform.capitalize()}:** [{link}]({link})\n"
    else:
        report += "- N/A\n"

    report += '''
## Founders
'''
    founders = company_data.get('founders', [])
    if founders:
        for founder in founders:
            report += f"- {founder}\n"
    else:
        report += "- N/A\n"

    report += '''
## Key Investors
'''
    key_investors = company_data.get('key_investors', [])
    if key_investors:
        for investor in key_investors:
            report += f"- {investor}\n"
    else:
        report += "- N/A\n"

    report += f'''
---

## Sector & Activity
- **Sector:** {category.get('sector', 'N/A')}
- **Sub-sector:** {category.get('sub_sector', 'N/A')}
- **Industry:** {category.get('industry', 'N/A')}
- **Activity:** {category.get('activity', 'N/A')}

## Business & Revenue
- **Business Model:** {company_data.get('business_model', 'N/A')}
- **Revenue Model:** {company_data.get('revenue_model', 'N/A')}
- **Revenue Stream:** {company_data.get('revenue_stream', 'N/A')}

---

## AI-Generated Analysis

### Products/Services Description
{llm_analysis.get('products_services', 'N/A')}

### Market Description
{llm_analysis.get('market_description', 'N/A')}

### Traction (Inferred)
{llm_analysis.get('traction_analysis', 'N/A')}

### Highlights
'''
    highlights = llm_analysis.get('key_highlights', [])
    if highlights:
        for item in highlights:
            report += f"- {item}\n"
    else:
        report += "- N/A\n"

    report += f'''
---

## Investment Thesis

### The Bull Case
{investment_thesis.get('bull_case', 'N/A')}

### The Bear Case
{investment_thesis.get('bear_case', 'N/A')}

---

## Investment Fit (Our Rules)
'''
    for item in rules_feedback:
        report += f"- {item}\n"
        
    return report 

# --- MAIN APP LOGIC ---
load_dotenv()

st.set_page_config(layout="wide", page_title="Investment Fit Report")
st.title("AI-Powered Investment Fit Report Generator")

if not os.getenv("PERPLEXITY_API_KEY") or not os.getenv("GROQ_API_KEY"):
    st.error("🚨 Missing API Keys! Please check your .env file.")
    st.stop()

# Initialize session state
if 'report_data' not in st.session_state:
    st.session_state.report_data = None

st.sidebar.header("Inputs")
startup_name_input = st.sidebar.text_input("Startup Name", placeholder="e.g., Cred, Figma, Stripe")
sector_input = st.sidebar.text_input("Target Sector", value="FinTech")

if st.sidebar.button("Generate Report", type="primary"):
    if not startup_name_input:
        st.warning("Please enter a startup name.")
    else:
        with st.spinner("🚀 Gathering company data..."):
            company_data = get_company_data(startup_name_input, sector_input)
            if "error" in company_data:
                st.error(f"Layer 1 Error: {company_data['error']}")
                st.stop()

        with st.spinner("🧠 Generating qualitative analysis..."):
            llm_analysis = generate_qualitative_analysis(company_data)
            if "error" in llm_analysis:
                st.error(f"Layer 2 Error: {llm_analysis['error']}")
                st.stop()
        
        with st.spinner("🤔 Forming investment thesis..."):
            investment_thesis = generate_investment_thesis(company_data, llm_analysis)
            if "error" in investment_thesis:
                st.error(f"Layer 3 Error: {investment_thesis['error']}")
                st.stop()

        with st.spinner("✅ Applying investment rules..."):
            rules_feedback = apply_investment_rules(company_data, sector_input)
        
        st.session_state.report_data = {
            'company_data': company_data,
            'llm_analysis': llm_analysis,
            'investment_thesis': investment_thesis,
            'rules_feedback': rules_feedback,
            'startup_name': startup_name_input
        }

if st.session_state.report_data:
    report_data = st.session_state.report_data
    company_data = report_data['company_data']
    llm_analysis = report_data['llm_analysis']
    investment_thesis = report_data['investment_thesis']
    rules_feedback = report_data['rules_feedback']
    startup_name = report_data['startup_name']

    st.header(f"Preliminary Investment Fit Report: {company_data.get('name', startup_name)}")
    
    col1, col2 = st.columns((1, 1))

    with col1:
        st.subheader("Company Details")
        st.markdown(f"**Year Founded:** {company_data.get('foundedYear', 'N/A')}")
        geo = company_data.get('geo', {})
        st.markdown(f"**HQ Location:** {geo.get('city', 'N/A')}, {geo.get('country', 'N/A')}")
        st.markdown(f"**Address:** {geo.get('address', 'N/A')}")
        st.markdown(f"**Website:** [{company_data.get('domain', 'N/A')}]({company_data.get('domain', 'N/A')})")
        st.markdown(f"**Team Strength:** {company_data.get('metrics', {}).get('employees', 'N/A')} employees")

        st.subheader("Social Media")
        social_media = company_data.get('social_media', {})
        if social_media:
            for platform, link in social_media.items():
                st.markdown(f"- **{platform.capitalize()}:** [{link}]({link})")
        else:
            st.markdown("N/A")

        st.subheader("Founders")
        founders = company_data.get('founders', [])
        if founders:
            for founder in founders:
                st.markdown(f"- {founder}")
        else:
            st.markdown("N/A")

        st.subheader("Key Investors")
        key_investors = company_data.get('key_investors', [])
        if key_investors:
            for investor in key_investors:
                st.markdown(f"- {investor}")
        else:
            st.markdown("N/A")

    with col2:
        st.subheader("Sector & Activity")
        category = company_data.get('category', {})
        st.markdown(f"**Sector:** {category.get('sector', 'N/A')}")
        st.markdown(f"**Sub-sector:** {category.get('sub_sector', 'N/A')}")
        st.markdown(f"**Industry:** {category.get('industry', 'N/A')}")
        st.markdown(f"**Activity:** {category.get('activity', 'N/A')}")

        st.subheader("Business & Revenue")
        st.markdown(f"**Business Model:** {company_data.get('business_model', 'N/A')}")
        st.markdown(f"**Revenue Model:** {company_data.get('revenue_model', 'N/A')}")
        st.markdown(f"**Revenue Stream:** {company_data.get('revenue_stream', 'N/A')}")
    
    st.subheader("Products/Services Description")
    st.info(llm_analysis.get('products_services', 'N/A'))

    st.subheader("Market Description")
    st.info(llm_analysis.get('market_description', 'N/A'))

    st.subheader("Traction (Inferred)")
    st.info(llm_analysis.get('traction_analysis', 'N/A'))

    st.subheader("Highlights")
    highlights = llm_analysis.get('key_highlights', [])
    if highlights:
        for item in highlights:
            st.markdown(f"- {item}")
    else:
        st.markdown("N/A")

    st.subheader("Investment Thesis")
    bull_case = investment_thesis.get('bull_case', 'N/A')
    bear_case = investment_thesis.get('bear_case', 'N/A')
    
    st.success(f"**The Bull Case:** {bull_case}")
    st.warning(f"**The Bear Case:** {bear_case}")

    st.subheader("Investment Fit (Our Rules)")
    for item in rules_feedback:
        if item['type'] == 'positive':
            st.success(item['text'])
        elif item['type'] == 'negative':
            st.warning(item['text'])
        else:
            st.info(item['text'])

    st.subheader("Download Report")
    
    pdf_rules_feedback = [item['text'] for item in rules_feedback]
    
    pdf = PDFReport()
    pdf_output = pdf.generate(startup_name, company_data, llm_analysis, pdf_rules_feedback, investment_thesis)
    st.download_button(
        label="Download as PDF",
        data=pdf_output,
        file_name=f"Investment_Fit_Report_{startup_name.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
    
    markdown_report_string = generate_markdown_report(startup_name, company_data, llm_analysis, pdf_rules_feedback, investment_thesis)
    st.download_button(
        label="Download as Markdown (.md)",
        data=markdown_report_string,
        file_name=f"Investment_Fit_Report_{startup_name.replace(' ', '_')}.md",
        mime="text/markdown"
    )
