# rules.py
from datetime import datetime

def apply_investment_rules(company_data, user_sector_input):
    """
    Applies a custom set of investment rules to the fetched data.
    Returns a list of dictionaries, each with 'text' and 'type' keys.
    """
    feedback = []
    
    # Rule 1: Sector Fit
    api_sector = company_data.get('category', {}).get('sector', '')
    if api_sector and user_sector_input.lower() in api_sector.lower():
        feedback.append({'text': "Sector Fit: Aligns with the target sector.", 'type': 'positive'})
    else:
        feedback.append({'text': "Sector Mismatch: Company's sector does not align with the primary target.", 'type': 'negative'})
        
    # Rule 2: Stage Fit (using team size as a proxy)
    team_size = company_data.get('metrics', {}).get('employees')
    if team_size and isinstance(team_size, int):
        if 5 < team_size < 200:
            feedback.append({'text': f"Stage Fit: Team size of ~{team_size} is within the preferred Seed-to-Series-A range.", 'type': 'positive'})
        else:
            feedback.append({'text': f"Stage Check: Team size of ~{team_size} is outside the typical investment range.", 'type': 'negative'})
    else:
        feedback.append({'text': "Stage Check: Team size data is unavailable to estimate stage.", 'type': 'neutral'})

    # Rule 3: Business Model
    business_model = company_data.get('business_model', '').lower()
    if 'b2b' in business_model or 'enterprise' in business_model:
        feedback.append({'text': "Business Model: Appears to be a B2B or enterprise model.", 'type': 'positive'})
    elif business_model and business_model != 'n/a':
        feedback.append({'text': f"Business Model: The model is described as '{business_model}'.", 'type': 'neutral'})
    else:
        feedback.append({'text': "Business Model: The business model is unclear or not specified.", 'type': 'negative'})

    # Rule 4: Company Age
    founded_year = company_data.get('foundedYear')
    if founded_year and isinstance(founded_year, int):
        current_year = datetime.now().year
        age = current_year - founded_year
        if 2 <= age <= 10:
            feedback.append({'text': f"Company Age: Founded {age} years ago, which is a reasonable age.", 'type': 'positive'})
        else:
            feedback.append({'text': f"Company Age: Founded {age} years ago, which is outside the typical 2-10 year range.", 'type': 'negative'})
    else:
        feedback.append({'text': "Company Age: Founding year is not available.", 'type': 'neutral'})

    # Rule 5: Founder Information
    founders = company_data.get('founders', [])
    if founders:
        feedback.append({'text': f"Founders: Founder information is available ({len(founders)} found).", 'type': 'positive'})
    else:
        feedback.append({'text': "Founders: No founder information was found.", 'type': 'negative'})

    # Rule 6: Key Investors
    key_investors = company_data.get('key_investors', [])
    if key_investors:
        feedback.append({'text': "Investors: Key investor information is available.", 'type': 'positive'})
    else:
        feedback.append({'text': "Investors: No key investor information was found. This may be expected for early-stage companies.", 'type': 'neutral'})

    # Rule 7: Funding History
    funding_history = company_data.get('funding_history', [])
    if funding_history:
        feedback.append({'text': "Funding: The company has a known funding history.", 'type': 'positive'})
    else:
        feedback.append({'text': "Funding: No funding history was found. This may be expected for seed-stage companies.", 'type': 'neutral'})
        
    return feedback
