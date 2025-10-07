# app.py
import streamlit as st
import os
import json
from dotenv import load_dotenv
from investment_decision import generate_investment_recommendation
from api_calls import get_company_data_with_analysis
from rules import apply_investment_rules
from pdf_generator import PDFReport

from financial_analyzer import FinancialAnalyzer

# --- UI Rendering Functions ---

def display_report_ui(report_data):
    company_data = report_data.get('company_data', {})
    investment_decision = report_data.get('investment_decision', {})
    
    # Show decision FIRST
    st.title(f"Investment Analysis: {company_data.get('name')}")

    # ==================== CRITICAL METRICS DISPLAY ====================
    # Show capital efficiency warnings FIRST
    cap_warning = company_data.get('capital_efficiency_warning')
    calculated = company_data.get('calculated', {})
    
    if cap_warning:
        st.error(cap_warning)
        st.warning("⚠️ **Action Required:** Investigate why capital efficiency is so poor before proceeding.")
    
    # Show key metrics snapshot
    if calculated:
        st.subheader(" Critical Financial Metrics")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            arr = calculated.get('arr_numeric', 0)
            if arr:
                st.metric("Revenue (ARR)", f"${arr/1e6:.1f}M")
            else:
                st.metric("Revenue", "Not Disclosed")
        
        with metric_col2:
            funding = calculated.get('total_funding_numeric', 0)
            if funding:
                st.metric("Total Funding", f"${funding/1e6:.1f}M")
            else:
                st.metric("Total Funding", company_data.get('total_funding', 'N/A'))
        
        with metric_col3:
            ratio = calculated.get('capital_efficiency_ratio')
            if ratio:
                if ratio > 10:
                    st.metric("Capital Efficiency", f"{ratio}x", delta="Poor", delta_color="inverse")
                elif ratio < 5:
                    st.metric("Capital Efficiency", f"{ratio}x", delta="Good", delta_color="normal")
                else:
                    st.metric("Capital Efficiency", f"{ratio}x")
            else:
                st.metric("Capital Efficiency", "Unknown")
        
        with metric_col4:
            employees = company_data.get('metrics', {}).get('employees', 0)
            if employees and arr:
                revenue_per_employee = arr / employees
                st.metric("Revenue/Employee", f"${revenue_per_employee/1000:.0f}K")
            else:
                st.metric("Team Size", f"{employees}" if employees else "N/A")
        
        # Show rating with color coding
        rating = calculated.get('capital_efficiency_rating')
        if rating:
            if 'RED FLAG' in rating or 'CONCERNING' in rating:
                st.error(f"**Capital Efficiency Rating:** {rating}")
            elif 'EXCELLENT' in rating:
                st.success(f"**Capital Efficiency Rating:** {rating}")
            else:
                st.info(f"**Capital Efficiency Rating:** {rating}")
        
        st.markdown("---")
    # ==================== END CRITICAL METRICS ====================
    
    decision = investment_decision.get('decision')
    if decision == 'STRONG_INVEST':
        st.success(f"✅ STRONG INVEST - Score: {investment_decision.get('total_score')}/100")
    elif decision == 'INVEST':
        st.success(f"✅ INVEST - Score: {investment_decision.get('total_score')}/100")
    elif decision == 'MAYBE':
        st.warning(f"⚠️ MAYBE - Score: {investment_decision.get('total_score')}/100")
    else:
        st.error(f"❌ PASS - Score: {investment_decision.get('total_score')}/100")
    
    st.markdown(investment_decision.get('recommendation'))
    
    # ==================== ADD THIS SECTION ====================
    # Show critical financial warnings FIRST
    cap_warning = company_data.get('capital_efficiency_warning')
    calculated = company_data.get('calculated', {})
    
    if cap_warning:
        st.error(cap_warning)
        st.warning("⚠️ **Action Required:** Investigate why capital efficiency is so poor before proceeding.")
    
    # Show key metrics snapshot
    if calculated:
        st.subheader(" Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            arr = calculated.get('arr_numeric', 0)
            if arr:
                st.metric("Revenue (ARR)", f"${arr/1e6:.1f}M")
            else:
                st.metric("Revenue", "Not Disclosed")
        
        with col2:
            funding = calculated.get('total_funding_numeric', 0)
            if funding:
                st.metric("Total Funding", f"${funding/1e6:.1f}M")
            else:
                st.metric("Total Funding", company_data.get('total_funding', 'N/A'))
        
        with col3:
            ratio = calculated.get('capital_efficiency_ratio')
            if ratio:
                # Color code based on ratio
                if ratio > 10:
                    st.metric("Capital Efficiency", f"{ratio}x", delta="Poor", delta_color="inverse")
                elif ratio < 5:
                    st.metric("Capital Efficiency", f"{ratio}x", delta="Good", delta_color="normal")
                else:
                    st.metric("Capital Efficiency", f"{ratio}x")
            else:
                st.metric("Capital Efficiency", "N/A")
        
        with col4:
            employees = company_data.get('metrics', {}).get('employees', 0)
            if employees and arr:
                revenue_per_employee = arr / employees
                st.metric("Revenue/Employee", f"${revenue_per_employee/1000:.0f}K")
            else:
                st.metric("Team Size", f"{employees}" if employees else "N/A")
        
        # Show rating
        rating = calculated.get('capital_efficiency_rating')
        if rating:
            if 'RED FLAG' in rating or 'CONCERNING' in rating:
                st.error(f"**Capital Efficiency Rating:** {rating}")
            elif 'EXCELLENT' in rating:
                st.success(f"**Capital Efficiency Rating:** {rating}")
            else:
                st.info(f"**Capital Efficiency Rating:** {rating}")
        
        st.markdown("---")
    # ==================== END NEW SECTION ====================
    
    # Show red flags prominently
    red_flags = company_data.get('financial_analysis', {}).get('red_flags', [])
    if red_flags:
        st.subheader(" Critical Red Flags")
        for flag in red_flags:
            st.error(flag)
    
    # Show reasons to invest
    reasons_invest = investment_decision.get('reasons_to_invest', [])
    if reasons_invest:
        st.subheader("✅ Reasons to Invest")
        for reason in reasons_invest:
            st.success(reason)
    
    # Show reasons to pass
    reasons_pass = investment_decision.get('reasons_to_pass', [])
    if reasons_pass:
        st.subheader("⚠️ Concerns")
        for reason in reasons_pass:
            st.warning(reason)
    
    # Critical questions
    critical_q = investment_decision.get('critical_questions', [])
    if critical_q:
        st.subheader("❓ Critical Questions to Answer")
        for i, question in enumerate(critical_q, 1):
            st.markdown(f"{i}. {question}")

    st.subheader("Download Report")
    pdf = PDFReport()
    pdf_output = pdf.generate(report_data.get('startup_name', 'N/A'), company_data, investment_decision, report_data.get('rules_feedback', []))
    st.download_button(
        label="Download as PDF",
        data=pdf_output,
        file_name=f"Investment_Fit_Report_{report_data.get('startup_name', 'N/A').replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
    
    markdown_report_string = generate_markdown_report(report_data.get('startup_name', 'N/A'), company_data, investment_decision, report_data.get('rules_feedback', []))
    st.download_button(
        label="Download as Markdown (.md)",
        data=markdown_report_string,
        file_name=f"Investment_Fit_Report_{report_data.get('startup_name', 'N/A').replace(' ', '_')}.md",
        mime="text/markdown"
    )



# --- The Markdown generation function ---
def generate_markdown_report(startup_name, company_data, investment_decision, rules_feedback):
    name = company_data.get('name', startup_name)
    
    report = f'''
# Investment Analysis: {name}

## Decision: {investment_decision.get('decision')} - Score: {investment_decision.get('total_score')}/100

{investment_decision.get('recommendation')}

---

## Critical Red Flags
'''
    red_flags = company_data.get('financial_analysis', {}).get('red_flags', [])
    if red_flags:
        for flag in red_flags:
            report += f"- {flag}\n"
    else:
        report += "- None\n"
        
    report += '''

## ✅ Reasons to Invest
'''
    reasons_invest = investment_decision.get('reasons_to_invest', [])
    if reasons_invest:
        for reason in reasons_invest:
            report += f"- {reason}\n"
    else:
        report += "- None\n"

    report += '''

## ⚠️ Concerns
'''
    reasons_pass = investment_decision.get('reasons_to_pass', [])
    if reasons_pass:
        for reason in reasons_pass:
            report += f"- {reason}\n"
    else:
        report += "- None\n"
        
    report += '''

## ❓ Critical Questions to Answer
'''
    critical_q = investment_decision.get('critical_questions', [])
    if critical_q:
        for i, question in enumerate(critical_q, 1):
            report += f"{i}. {question}\n"
    else:
        report += "- None\n"

    return report 

def validate_company_data(company_data):
    """Check if we have minimum data for analysis - more lenient now."""
    
    if not company_data or company_data.get("error"):
        return False, "Failed to fetch company data from Perplexity"
    
    if not company_data.get('name'):
        return False, "Could not identify company name"
    
    warnings = []
    if not company_data.get('description') or len(company_data.get('description', '')) < 20:
        warnings.append("⚠️ Limited company description available")
    
    if not company_data.get('foundedYear'):
        warnings.append("⚠️ Founded year not available")
    
    has_revenue = (
        company_data.get('revenue') or 
        company_data.get('calculated', {}).get('arr_numeric')
    )
    has_funding = (
        company_data.get('total_funding') or 
        company_data.get('calculated', {}).get('total_funding_numeric')
    )
    
    if not has_revenue and not has_funding:
        warnings.append("⚠️ No financial data available - analysis will be limited")
    
    if warnings:
        st.warning("Data Quality Issues:\n" + "\n".join(warnings))
    
    return True, "Valid (with limitations)" if warnings else "Valid"

# --- MAIN APP LOGIC ---
load_dotenv()

st.set_page_config(layout="wide", page_title="Investment Fit Report")
st.title("AI-Powered Investment Fit Report Generator")

if not os.getenv("PERPLEXITY_API_KEY") or not os.getenv("GROQ_API_KEY"):
    st.error("🚨 Missing API Keys! Please check your .env file for PERPLEXITY_API_KEY and GROQ_API_KEY.")
    st.stop()

# Initialize session state
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

st.sidebar.header("Inputs")
startup_name_input = st.sidebar.text_input("Startup Name", placeholder="e.g., Cred, Figma, Stripe")
sector_input = st.sidebar.text_input("Target Sector", value="FinTech")
debug_mode = st.sidebar.checkbox("Enable Debug Mode", value=st.session_state.debug_mode)


if st.sidebar.button("Generate Report", type="primary"):
    if not startup_name_input:
        st.warning("Please enter a startup name.")
    else:
        st.session_state.debug_mode = debug_mode
        
        # Clear any cached data for this company to ensure a fresh run
        st.cache_data.clear()
        
        # Initialize data dictionaries
        company_data = {}
        investment_decision = {}
        rules_feedback = []

        with st.spinner(" Layer 1: Gathering and analyzing data..."):
            try:
                # This is the new combined function
                company_data = get_company_data_with_analysis(startup_name_input, sector_input)
                
                if debug_mode:
                    st.write("### Debug: Raw Company Data")
                    st.json(company_data)
                
                if company_data.get("error"):
                    st.error(f"Layer 1 (Data Gathering) Error: {company_data['error']}")
                    st.stop()
            except Exception as e:
                st.error(f"A critical error occurred during data gathering: {str(e)}")
                st.stop()

        # Validate with lenient checking
        is_valid, message = validate_company_data(company_data)
        if not is_valid:
            st.error(f"Cannot generate report: {message}")
            st.info("Try a different company name or check if it has public information available.")
            st.stop()
        else:
            st.success(f"✅ Data gathered: {message}")

        # Continue with analysis
        with st.spinner(" Layer 2: Generating investment decision..."):
            try:
                investment_decision = generate_investment_recommendation(company_data)
            except Exception as e:
                st.warning(f"Decision generation failed: {str(e)}")
                investment_decision = {"error": f"Failed to generate investment decision: {e}"}

        with st.spinner("✅ Applying investment rules..."):
            try:
                rules_feedback = apply_investment_rules(company_data, sector_input)
            except Exception as e:
                st.warning(f"Rules application failed: {str(e)}")
                rules_feedback = []
        
        # Store in session
        st.session_state.report_data = {
            'company_data': company_data,
            'investment_decision': investment_decision,
            'rules_feedback': rules_feedback,
            'startup_name': startup_name_input
        }

        # Debug output if enabled
        if debug_mode:
            st.write("### Debug: Complete Report Data")
            with st.expander("Company Data"):
                st.json(company_data)
            with st.expander("Investment Decision"):
                st.json(investment_decision)
            with st.expander("Rules Feedback"):
                st.json(rules_feedback)

# Display report if available
if st.session_state.report_data:
    display_report_ui(st.session_state.report_data)