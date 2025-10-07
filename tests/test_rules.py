# tests/test_rules.py
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rules import apply_investment_rules

def test_sector_fit():
    """Tests the 'Sector Fit' rule (GLOBAL_01)."""
    # Case 1: Sector matches
    company_data = {'category': {'sector': 'FinTech'}}
    feedback = apply_investment_rules(company_data, 'FinTech')
    assert {'text': "Sector Fit: Aligns with the target sector.", 'type': 'positive'} in feedback

    # Case 2: Sector does not match
    company_data = {'category': {'sector': 'HealthTech'}}
    feedback = apply_investment_rules(company_data, 'FinTech')
    assert {'text': "Sector Mismatch: Company's sector does not align with the primary target.", 'type': 'negative'} in feedback

def test_stage_fit_team_size():
    """Tests the 'Stage Fit (Team Size)' rule (GLOBAL_02)."""
    # Case 1: Team size is within range
    company_data = {'metrics': {'employees': 50}}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Stage Fit: Team size of ~50 is within the preferred Seed-to-Series-A range.", 'type': 'positive'} in feedback

    # Case 2: Team size is outside range
    company_data = {'metrics': {'employees': 200}}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Stage Check: Team size of ~200 is outside the typical investment range.", 'type': 'negative'} in feedback

def test_company_age():
    """Tests the 'Company Age' rule (GLOBAL_03)."""
    # Case 1: Age is within range
    company_data = {'foundedYear': datetime.now().year - 5}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Company Age: Founded 5 years ago, which is a reasonable age.", 'type': 'positive'} in feedback

    # Case 2: Age is outside range
    company_data = {'foundedYear': datetime.now().year - 1}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Company Age: Founded 1 years ago, which is outside the typical 2-10 year range.", 'type': 'negative'} in feedback

def test_single_founder_risk():
    """Tests the 'Single Founder Risk' rule (GLOBAL_04)."""
    # Case 1: Single founder
    company_data = {'founders_analysis': {'number_of_founders': 1}}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Founder Risk: The company relies on a single founder, which can be a dependency risk.", 'type': 'negative'} in feedback

    # Case 2: Multiple founders
    company_data = {'founders_analysis': {'number_of_founders': 2}}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Founder Team: With 2 founders, the company has mitigated single-founder dependency risk.", 'type': 'positive'} in feedback

def test_founder_red_flags():
    """Tests the 'Founder Red Flags' rule (GLOBAL_05)."""
    # Case 1: No red flags
    company_data = {'founders_analysis': {'red_flags': 'None'}}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Founder Red Flags: No significant red flags were found for the founders.", 'type': 'positive'} in feedback

    # Case 2: Red flags exist
    company_data = {'founders_analysis': {'red_flags': 'Some controversy'}}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Founder Red Flags: Red flags were identified: Some controversy", 'type': 'negative'} in feedback

def test_key_investor_presence():
    """Tests the 'Key Investor Presence' rule (GLOBAL_06)."""
    # Case 1: Key investors are present
    company_data = {'key_investors': ['VC Firm A']}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Investors: Backed by key investors.", 'type': 'positive'} in feedback

    # Case 2: No key investors
    company_data = {'key_investors': []}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Investors: No key investor information was found. This may be expected for early-stage companies.", 'type': 'neutral'} in feedback

def test_product_description_clarity():
    """Tests the 'Product Description Clarity' rule (GLOBAL_07)."""
    # Case 1: Description is clear and long enough
    company_data = {'description': 'This is a long and detailed description of the product.'}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Product/Service: Clear description of the problem and solution.", 'type': 'positive'} in feedback

    # Case 2: Description is too short
    company_data = {'description': 'Short desc.'}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Product/Service: Description is not clear or too short.", 'type': 'negative'} in feedback

def test_market_size():
    """Tests the 'Market Size' rule (GLOBAL_08)."""
    # Case 1: Market size is large enough
    company_data = {'market_size': 'USD 2 billion'}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Market Size: The market size of $2,000,000,000 is large enough.", 'type': 'positive'} in feedback

    # Case 2: Market size is not specified or too small
    company_data = {'market_size': 'USD 500 million'}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Market Size: The market size is not specified or too small.", 'type': 'neutral'} in feedback

def test_total_funding():
    """Tests the 'Total Funding' rule (GLOBAL_09)."""
    # Case 1: Total funding is within the preferred range
    company_data = {'total_funding': '$10 million'}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Total Funding: The total funding of $10,000,000 is within the preferred range.", 'type': 'positive'} in feedback

    # Case 2: Total funding is outside the preferred range
    company_data = {'total_funding': '$60 million'}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Total Funding: The total funding is not specified or outside the preferred range.", 'type': 'neutral'} in feedback

def test_glassdoor_rating():
    """Tests the 'Glassdoor Rating' rule (GLOBAL_10)."""
    # Case 1: Glassdoor rating is good
    company_data = {'glassdoor_rating': 4.0}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Glassdoor Rating: The Glassdoor rating of 4.0 is good.", 'type': 'positive'} in feedback

    # Case 2: Glassdoor rating is not specified or low
    company_data = {'glassdoor_rating': 3.0}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Glassdoor Rating: The Glassdoor rating is not specified or low.", 'type': 'neutral'} in feedback

def test_number_of_competitors():
    """Tests the 'Number of Competitors' rule (GLOBAL_11)."""
    # Case 1: Number of competitors is reasonable
    company_data = {'competitors': ['Comp A', 'Comp B', 'Comp C']}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Competition: The number of competitors (3) is reasonable.", 'type': 'positive'} in feedback

    # Case 2: Number of competitors is not specified or too high
    company_data = {'competitors': ['Comp A', 'Comp B', 'Comp C', 'Comp D', 'Comp E', 'Comp F', 'Comp G', 'Comp H', 'Comp I', 'Comp J', 'Comp K']}
    feedback = apply_investment_rules(company_data, 'N/A')
    assert {'text': "Competition: The number of competitors is not specified or too high.", 'type': 'neutral'} in feedback
