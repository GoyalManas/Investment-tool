# app.py
import streamlit as st
import os
import json
from dotenv import load_dotenv
from api_calls import get_company_data, generate_qualitative_analysis, generate_investment_thesis, generate_founders_analysis, generate_product_analysis
from rules import apply_investment_rules
from pdf_generator import PDFReport

# --- UI Rendering Functions ---

def display_report_ui(report_data):
    """Renders the entire report UI from the report_data dictionary."""
    company_data = report_data.get('company_data', {})
    llm_analysis = report_data.get('llm_analysis', {})
    investment_thesis = report_data.get('investment_thesis', {})
    founders_analysis = report_data.get('founders_analysis', {})
    product_analysis = report_data.get('product_analysis', {})
    rules_feedback = report_data.get('rules_feedback', [])
    startup_name = report_data.get('startup_name', 'N/A')

    st.header(f"Preliminary Investment Fit Report: {company_data.get('name', startup_name)}")
    
    col1, col2 = st.columns((1, 1))

    # --- Column 1: Company Details, Social, Founders, Investors ---
    with col1:
        st.subheader("Company Details")
        st.markdown(f"**Year Founded:** {company_data.get('foundedYear', 'N/A')}")
        geo = company_data.get('geo', {})
        st.markdown(f"**HQ Location:** {geo.get('city', 'N/A')}, {geo.get('country', 'N/A')}")
        st.markdown(f"**Address:** {geo.get('address', 'N/A')}")
        domain = company_data.get('domain', 'N/A')
        website_url = f"https://{domain}" if domain != 'N/A' else '#'
        st.markdown(f"**Website:** [{domain}]({website_url})")
        st.markdown(f"**Team Strength:** {company_data.get('metrics', {}).get('employees', 'N/A')} employees")

        st.subheader("Social Media")
        social_media = company_data.get('social_media', {})
        if social_media:
            for platform, link in social_media.items():
                if link and link != 'N/A':
                    # Ensure the link has a scheme for correct redirection
                    fixed_link = f'https://{link}' if not link.startswith(('http://', 'https://')) else link
                    st.markdown(f"- **{platform.capitalize()}:** [{link}]({fixed_link})")
        else:
            st.markdown("N/A")

        st.subheader("Founders")
        st.markdown(f"**Founder(s):** {', '.join(company_data.get('founders_analysis', {}).get('names_of_founders', []))}")
        st.markdown(f"**Complementarity:** {company_data.get('founders_analysis', {}).get('complementarity', 'N/A')}")
        st.markdown(f"**Key Competency:** {company_data.get('founders_analysis', {}).get('key_competency', 'N/A')}")
        st.markdown(f"**Prior Experience:** {company_data.get('founders_analysis', {}).get('prior_startup_experience', 'N/A')}")
        st.markdown(f"**Red Flags:** {company_data.get('founders_analysis', {}).get('red_flags', 'N/A')}")

        st.subheader("Key Investors")
        key_investors = company_data.get('key_investors', [])
        if key_investors:
            # Now we just display each investor name from the simple list
            for investor in key_investors:
                st.markdown(f"- **{investor}**")
        else:
            st.markdown("N/A")

    # --- Column 2: Sector, Business, Revenue, Financials ---
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
        st.markdown(f"**Pricing Model:** {company_data.get('pricing_model', 'N/A')}")
        st.markdown(f"**Revenue Stream Diversified:** {company_data.get('revenue_stream_diversified', 'N/A')}")

        st.subheader("Financials")
        st.markdown(f"**Total Funding:** {company_data.get('total_funding', 'N/A')}")
        st.markdown(f"**Last Funding Round:** {company_data.get('last_funding_round', 'N/A')}")
        st.markdown(f"**Valuation:** {company_data.get('valuation', 'N/A')}")
        st.markdown(f"**Revenue:** {company_data.get('revenue', 'N/A')}")
        st.markdown(f"**Profitability:** {company_data.get('profitability', 'N/A')}")


    # --- Full Width Sections ---
    st.subheader("Market & Competition")
    st.markdown(f"**Market Size:** {company_data.get('market_size', 'N/A')}")
    st.markdown(f"**Market Growth Rate:** {company_data.get('market_growth_rate', 'N/A')}")
    st.markdown(f"**Competitive Advantage:** {company_data.get('competitive_advantage', 'N/A')}")
    st.markdown(f"**Competitors:** {', '.join(company_data.get('competitors', [])) if company_data.get('competitors') else 'N/A'}")

    st.subheader("Product & Technology")
    st.markdown(f"**Product Differentiation:** {company_data.get('product_differentiation', 'N/A')}")
    st.markdown(f"**Innovative Solution:** {company_data.get('innovative_solution', 'N/A')}")
    st.markdown(f"**Patents:** {', '.join(company_data.get('patents', [])) if company_data.get('patents') else 'N/A'}")
    st.markdown(f"**Product Validation:** {company_data.get('product_validation', 'N/A')}")
    st.markdown(f"**Technology Stack:** {company_data.get('technology_stack', 'N/A')}")
    st.markdown(f"**Product Roadmap:** {company_data.get('product_roadmap', 'N/A')}")

    st.subheader("Team")
    st.markdown(f"**Key Hires:** {', '.join(company_data.get('key_hires', [])) if company_data.get('key_hires') else 'N/A'}")
    st.markdown(f"**Employee Growth Rate:** {company_data.get('employee_growth_rate', 'N/A')}")
    st.markdown(f"**Glassdoor Rating:** {company_data.get('glassdoor_rating', 'N/A')}")

    st.subheader("AI-Generated Analysis")
    if llm_analysis and not llm_analysis.get('error'):
        st.info(f"**SWOT Analysis:** {llm_analysis.get('swot_analysis', 'N/A')}")
        st.info(f"**Competitive Landscape:** {llm_analysis.get('competitive_landscape', 'N/A')}")
        st.info(f"**TAM Analysis:** {llm_analysis.get('tam_analysis', 'N/A')}")
        st.subheader("Highlights")
        highlights = llm_analysis.get('key_highlights', [])
        if highlights:
            for item in highlights:
                st.markdown(f"- {item}")
        else:
            st.markdown("N/A")

    st.subheader("Founder Analysis")
    if founders_analysis and not founders_analysis.get('error'):
        for key, value in founders_analysis.items():
            st.info(f"**{key.replace('_', ' ').title()}:** {value}")

    st.subheader("Product Analysis")
    if product_analysis and not product_analysis.get('error'):
        for key, value in product_analysis.items():
            st.info(f"**{key.replace('_', ' ').title()}:** {value}")

    st.subheader("Investment Thesis")
    if investment_thesis and not investment_thesis.get('error'):
        st.success(f"**Investment Summary:** {investment_thesis.get('investment_summary', 'N/A')}")
        st.warning(f"**Key Risks:** {investment_thesis.get('key_risks', 'N/A')}")
        st.info(f"**Investment Recommendation:** {investment_thesis.get('investment_recommendation', 'N/A')}")

    st.subheader("Investment Fit (Our Rules)")
    if rules_feedback:
        for item in rules_feedback:
            if item['type'] == 'positive':
                st.success(item['text'])
            elif item['type'] == 'negative':
                st.warning(item['text'])
            else:
                st.info(item['text'])

    st.subheader("Download Report")
    pdf = PDFReport()
    pdf_output = pdf.generate(startup_name, company_data, llm_analysis, rules_feedback, investment_thesis, founders_analysis, product_analysis)
    st.download_button(
        label="Download as PDF",
        data=pdf_output,
        file_name=f"Investment_Fit_Report_{startup_name.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
    
    markdown_report_string = generate_markdown_report(startup_name, company_data, llm_analysis, rules_feedback, investment_thesis, founders_analysis, product_analysis)
    st.download_button(
        label="Download as Markdown (.md)",
        data=markdown_report_string,
        file_name=f"Investment_Fit_Report_{startup_name.replace(' ', '_')}.md",
        mime="text/markdown"
    )

# --- The Markdown generation function ---
def generate_markdown_report(startup_name, company_data, llm_analysis, rules_feedback, investment_thesis, founders_analysis, product_analysis):
    name = company_data.get('name', startup_name)
    geo = company_data.get('geo', {})
    category = company_data.get('category', {})
    social_media = company_data.get('social_media', {})
    domain = company_data.get('domain', 'N/A')
    website_url = f"https://{domain}" if domain != 'N/A' else '#'
    
    report = f'''
# Preliminary Investment Fit Report: {name}

---

## Company Details
- **Year Founded:** {company_data.get('foundedYear', 'N/A')}
- **HQ Location:** {geo.get('city', 'N/A')}, {geo.get('country', 'N/A')}
- **Address:** {geo.get('address', 'N/A')}
- **Website:** [{domain}]({website_url})
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
    report += f"**Founder(s):** {', '.join(company_data.get('founders_analysis', {}).get('names_of_founders', []))}\n"
    report += f"**Complementarity:** {company_data.get('founders_analysis', {}).get('complementarity', 'N/A')}\n"
    report += f"**Key Competency:** {company_data.get('founders_analysis', {}).get('key_competency', 'N/A')}\n"
    report += f"**Prior Experience:** {company_data.get('founders_analysis', {}).get('prior_startup_experience', 'N/A')}\n"
    report += f"**Red Flags:** {company_data.get('founders_analysis', {}).get('red_flags', 'N/A')}\n"

    report += '''
## Key Investors
'''
    key_investors = company_data.get('key_investors', [])
    if key_investors:
        for investor in key_investors:
            report += f"- **{investor}**\n"
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
- **Pricing Model:** {company_data.get('pricing_model', 'N/A')}
- **Revenue Stream Diversified:** {company_data.get('revenue_stream_diversified', 'N/A')}

## Financials
- **Total Funding:** {company_data.get('total_funding', 'N/A')}
- **Last Funding Round:** {company_data.get('last_funding_round', 'N/A')}
- **Valuation:** {company_data.get('valuation', 'N/A')}
- **Revenue:** {company_data.get('revenue', 'N/A')}
- **Profitability:** {company_data.get('profitability', 'N/A')}

---

## Market & Competition
- **Market Size:** {company_data.get('market_size', 'N/A')}
- **Market Growth Rate:** {company_data.get('market_growth_rate', 'N/A')}
- **Competitive Advantage:** {company_data.get('competitive_advantage', 'N/A')}
- **Competitors:** {', '.join(company_data.get('competitors', [])) if company_data.get('competitors') else 'N/A'}

## Product & Technology
- **Product Differentiation:** {company_data.get('product_differentiation', 'N/A')}
- **Innovative Solution:** {company_data.get('innovative_solution', 'N/A')}
- **Patents:** {', '.join(company_data.get('patents', [])) if company_data.get('patents') else 'N/A'}
- **Product Validation:** {company_data.get('product_validation', 'N/A')}
- **Technology Stack:** {company_data.get('technology_stack', 'N/A')}
- **Product Roadmap:** {company_data.get('product_roadmap', 'N/A')}

## Team
- **Key Hires:** {', '.join(company_data.get('key_hires', [])) if company_data.get('key_hires') else 'N/A'}
- **Employee Growth Rate:** {company_data.get('employee_growth_rate', 'N/A')}
- **Glassdoor Rating:** {company_data.get('glassdoor_rating', 'N/A')}

---

## AI-Generated Analysis

### SWOT Analysis
{llm_analysis.get('swot_analysis', 'N/A')}

### Competitive Landscape
{llm_analysis.get('competitive_landscape', 'N/A')}

### TAM Analysis
{llm_analysis.get('tam_analysis', 'N/A')}

### Highlights
'''
    highlights = llm_analysis.get('key_highlights', [])
    if highlights:
        for item in highlights:
            report += f"- {item}\n"
    else:
        report += "- N/A\n"

    report += '''
---

## Founder Analysis
'''
    if founders_analysis and not founders_analysis.get('error'):
        for key, value in founders_analysis.items():
            report += f"### {key.replace('_', ' ').title()}\n{value}\n\n"

    report += '''
---

## Product Analysis
'''
    if product_analysis and not product_analysis.get('error'):
        for key, value in product_analysis.items():
            report += f"### {key.replace('_', ' ').title()}\n{value}\n\n"

    report += f'''
---

## Investment Thesis

### Investment Summary
{investment_thesis.get('investment_summary', 'N/A')}

### Key Risks
{investment_thesis.get('key_risks', 'N/A')}

### Investment Recommendation
{investment_thesis.get('investment_recommendation', 'N/A')}

---

## Investment Fit (Our Rules)
'''
    for item in rules_feedback:
        report += f"- {item['text']}\n"
        
    return report 

# --- MAIN APP LOGIC ---
load_dotenv()

st.set_page_config(layout="wide", page_title="Investment Fit Report")
st.title("AI-Powered Investment Fit Report Generator")

if not os.getenv("PERPLEXITY_API_KEY") or not os.getenv("GROQ_API_KEY"):
    st.error(" Missing API Keys! Please check your .env file for PERPLEXITY_API_KEY and GROQ_API_KEY.")
    st.stop()

# Initialize session state
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

st.sidebar.header("Inputs")
startup_name_input = st.sidebar.text_input("Startup Name", placeholder="e.g., Cred, Figma, Stripe")
sector_input = st.sidebar.text_input("Target Sector", placeholder="e.g., Healthtech, Crypto")
debug_mode = st.sidebar.checkbox("Enable Debug Mode", value=st.session_state.debug_mode)


if st.sidebar.button("Generate Report", type="primary"):
    if not startup_name_input:
        st.warning("Please enter a startup name.")
    else:
        st.session_state.debug_mode = debug_mode
        # Initialize data dictionaries
        company_data = {}
        llm_analysis = {}
        investment_thesis = {}
        founders_analysis = {}
        product_analysis = {}
        rules_feedback = []

        with st.spinner("Layer 1: Gathering data from Perplexity..."):
            company_data = get_company_data(startup_name_input, sector_input)
            if company_data.get("error"):
                st.error(f"Layer 1 (Perplexity) Error: {company_data['error']}")

        if not company_data.get("error"):
            with st.spinner("ðŸ§  Layer 2: Generating qualitative analysis..."):
                llm_analysis = generate_qualitative_analysis(company_data)
                if llm_analysis.get("error"):
                    st.error(f"Layer 2 (Groq) Error: {llm_analysis['error']}")
            
            with st.spinner("ðŸ¤” Layer 3: Forming investment thesis..."):
                investment_thesis = generate_investment_thesis(company_data, llm_analysis)
                if investment_thesis.get("error"):
                    st.error(f"Layer 3 (Groq) Error: {investment_thesis['error']}")

            with st.spinner("ðŸ§  Layer 4: Analyzing founders..."):
                founders_analysis = generate_founders_analysis(company_data)
                if founders_analysis.get("error"):
                    st.error(f"Layer 4 (Groq) Error: {founders_analysis['error']}")

            with st.spinner("ðŸ’¡ Layer 5: Analyzing product..."):
                product_analysis = generate_product_analysis(company_data)
                if product_analysis.get("error"):
                    st.error(f"Layer 5 (Groq) Error: {product_analysis['error']}")

            with st.spinner("âœ… Applying investment rules..."):
                rules_feedback = apply_investment_rules(company_data, sector_input)
        
        st.session_state.report_data = {
            'company_data': company_data,
            'llm_analysis': llm_analysis,
            'investment_thesis': investment_thesis,
            'founders_analysis': founders_analysis,
            'product_analysis': product_analysis,
            'rules_feedback': rules_feedback,
            'startup_name': startup_name_input
        }

        if debug_mode:
            print("--- DEBUG MODE ENABLED ---")
            print("\n--- RAW PERPLEXITY RESPONSE ---")
            print(json.dumps(company_data, indent=2))
            print("\n--- RAW GROQ ANALYSIS RESPONSE ---")
            print(json.dumps(llm_analysis, indent=2))
            print("\n--- RAW GROQ THESIS RESPONSE ---")
            print(json.dumps(investment_thesis, indent=2))
            print("\n--- RAW FOUNDERS ANALYSIS RESPONSE ---")
            print(json.dumps(founders_analysis, indent=2))
            print("\n--- RAW PRODUCT ANALYSIS RESPONSE ---")
            print(json.dumps(product_analysis, indent=2))
            print("\n--- RULES FEEDBACK ---")
            print(json.dumps(rules_feedback, indent=2))
            print("\n--- END OF DEBUG INFORMATION ---")

if st.session_state.report_data:
    display_report_ui(st.session_state.report_data)