# tests/test_rules.py
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rules import apply_investment_rules

def test_ideal_case():
    """Tests a comprehensive ideal case with all data available and positive."""
    company_data = {
        'category': {'sector': 'SaaS'},
        'metrics': {'employees': 50},
        'business_model': 'B2B',
        'foundedYear': datetime.now().year - 5,
        'founders': ['John Doe', 'Jane Doe'],
        'key_investors': ['VC Firm A', 'Angel B'],
        'funding_history': ['Seed round of $1M']
    }
    user_sector_input = 'SaaS'
    feedback = apply_investment_rules(company_data, user_sector_input)
    assert {'text': "Sector Fit: Aligns with the target sector.", 'type': 'positive'} in feedback
    assert {'text': "Stage Fit: Team size of ~50 is within the preferred Seed-to-Series-A range.", 'type': 'positive'} in feedback
    assert {'text': "Business Model: Appears to be a B2B or enterprise model.", 'type': 'positive'} in feedback
    assert {'text': "Company Age: Founded 5 years ago, which is a reasonable age.", 'type': 'positive'} in feedback
    assert {'text': "Founders: Founder information is available (2 found).", 'type': 'positive'} in feedback
    assert {'text': "Investors: Key investor information is available.", 'type': 'positive'} in feedback
    assert {'text': "Funding: The company has a known funding history.", 'type': 'positive'} in feedback

def test_sector_mismatch():
    """Tests when the company's sector does not match the target sector."""
    company_data = {'category': {'sector': 'Healthcare'}}
    user_sector_input = 'SaaS'
    feedback = apply_investment_rules(company_data, user_sector_input)
    assert {'text': "Sector Mismatch: Company's sector does not align with the primary target.", 'type': 'negative'} in feedback

def test_stage_fit_edge_cases():
    """Tests edge cases for team size."""
    company_data_small = {'metrics': {'employees': 3}}
    feedback_small = apply_investment_rules(company_data_small, 'SaaS')
    assert {'text': "Stage Check: Team size of ~3 is outside the typical investment range.", 'type': 'negative'} in feedback_small

    company_data_large = {'metrics': {'employees': 300}}
    feedback_large = apply_investment_rules(company_data_large, 'SaaS')
    assert {'text': "Stage Check: Team size of ~300 is outside the typical investment range.", 'type': 'negative'} in feedback_large

def test_missing_and_invalid_data():
    """Tests how rules handle missing or invalid data points."""
    company_data = {
        'category': {},
        'metrics': {'employees': 'N/A'},
        'business_model': 'n/a',
        'foundedYear': 'Unknown',
        'founders': [],
        'key_investors': [],
        'funding_history': []
    }
    user_sector_input = 'FinTech'
    feedback = apply_investment_rules(company_data, user_sector_input)
    assert {'text': "Sector Mismatch: Company's sector does not align with the primary target.", 'type': 'negative'} in feedback
    assert {'text': "Stage Check: Team size data is unavailable to estimate stage.", 'type': 'neutral'} in feedback
    assert {'text': "Business Model: The business model is unclear or not specified.", 'type': 'negative'} in feedback
    assert {'text': "Company Age: Founding year is not available.", 'type': 'neutral'} in feedback
    assert {'text': "Founders: No founder information was found.", 'type': 'negative'} in feedback
    assert {'text': "Investors: No key investor information was found. This may be expected for early-stage companies.", 'type': 'neutral'} in feedback
    assert {'text': "Funding: No funding history was found. This may be expected for seed-stage companies.", 'type': 'neutral'} in feedback

def test_business_model_informational():
    """Tests the informational feedback for a non-B2B business model."""
    company_data = {'business_model': 'Direct-to-Consumer (D2C)'}
    feedback = apply_investment_rules(company_data, 'e-commerce')
    assert {'text': "Business Model: The model is described as 'direct-to-consumer (d2c)'.", 'type': 'neutral'} in feedback

def test_company_age_outside_range():
    """Tests when the company age is outside the preferred 2-10 year range."""
    company_data_young = {'foundedYear': datetime.now().year - 1}
    feedback_young = apply_investment_rules(company_data_young, 'SaaS')
    assert {'text': "Company Age: Founded 1 years ago, which is outside the typical 2-10 year range.", 'type': 'negative'} in feedback_young

    company_data_old = {'foundedYear': datetime.now().year - 15}
    feedback_old = apply_investment_rules(company_data_old, 'SaaS')
    assert {'text': "Company Age: Founded 15 years ago, which is outside the typical 2-10 year range.", 'type': 'negative'} in feedback_old