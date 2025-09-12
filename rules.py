# rules.py
def apply_investment_rules(company_data, user_sector_input):
    """
    Applies a custom set of investment rules to the fetched data.
    """
    feedback = []
    
    # Rule 1: Sector Fit
    api_sector = company_data.get('category', {}).get('sector', '')
    if api_sector and user_sector_input.lower() in api_sector.lower():
        feedback.append("✅ **Sector Fit:** Aligns with the target sector.")
    else:
        feedback.append("⚠️ **Sector Mismatch:** Company sector does not align with our primary target.")
        
    # Rule 2: Stage Fit (using team size as a proxy)
    team_size = company_data.get('metrics', {}).get('employees')
    if team_size and isinstance(team_size, int):
        if 5 < team_size < 200:
            feedback.append(f"✅ **Stage Fit:** Team size of ~{team_size} is within our preferred Seed-to-Series-A range.")
        else:
            feedback.append(f"⚠️ **Stage Check:** Team size of ~{team_size} is outside our typical investment range.")
    else:
        feedback.append("ℹ️ **Stage Check:** Team size data unavailable to estimate stage.")
        
    return feedback