# rules.py
import json
from datetime import datetime
import re

def _get_nested_value(data_dict, key_string):
    """Safely retrieves a value from a nested dictionary using a dot-separated string."""
    keys = key_string.split('.')
    value = data_dict
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value

def _parse_numerical_value(value_string):
    """
    Parses a string to extract a numerical value. Handles currency symbols,
    "billion", "million", and "N/A".
    """
    if not isinstance(value_string, str):
        return value_string

    value_string = value_string.lower().replace(",", "").strip()

    if "n/a" in value_string or not value_string:
        return None

    # Handle "billion" and "million"
    multiplier = 1
    if "billion" in value_string:
        multiplier = 1_000_000_000
        value_string = value_string.replace("billion", "")
    elif "million" in value_string:
        multiplier = 1_000_000
        value_string = value_string.replace("million", "")

    # Extract numbers using regex
    numbers = re.findall(r'\d+\.?\d*', value_string)
    if numbers:
        try:
            return float(numbers[0]) * multiplier
        except ValueError:
            return None
    return None

def check_critical_red_flags(company_data, rules):
    """Check for deal-breaker issues."""
    red_flags = []
    calculated_values = company_data.get('calculated', {})

    for flag in rules.get('critical_red_flags', []):
        check_type = flag['check']
        actual_value = _get_nested_value(company_data, check_type)
        
        # Special composite checks
        if check_type == 'revenue_exists_with_funding':
            funding = calculated_values.get('total_funding_numeric', 0)
            revenue = calculated_values.get('arr_numeric', 0)
            if funding > 1_000_000 and revenue == 0:
                 red_flags.append({
                    'text': flag['message'].format(total_funding=funding),
                    'type': 'negative'
                })
            continue

        if check_type == 'culture_red_flags':
            glassdoor = company_data.get('glassdoor_rating', 5.0) # Default high
            # This is a placeholder for a more complex check
            # e.g., check for executive departures from another data source
            if float(glassdoor) < 3.5:
                 red_flags.append({
                    'text': flag['message'],
                    'type': 'negative'
                })
            continue

        if actual_value is None:
            continue

        operator = flag.get('operator')
        if operator == 'gt' and actual_value > flag['threshold']:
            red_flags.append({
                'text': flag['message'].format(ratio=actual_value, total_funding=calculated_values.get('total_funding_numeric', 0), revenue=calculated_values.get('arr_numeric', 0)),
                'type': 'negative'
            })
        elif operator == 'lt' and actual_value < flag['threshold']:
            red_flags.append({
                'text': flag['message'].format(ratio=actual_value, months=actual_value),
                'type': 'negative'
            })
        elif operator == 'lte' and actual_value <= flag['threshold']:
            red_flags.append({
                'text': flag['message'],
                'type': 'negative'
            })
        elif operator == 'contains' and any(keyword in str(actual_value).lower() for keyword in flag['keywords']):
            red_flags.append({
                'text': flag['message'],
                'type': 'negative'
            })

    return red_flags


def apply_investment_rules(company_data, user_sector_input):
    """
    Applies a custom set of investment rules to the fetched data by loading
    rules from an external rules.json file.
    """
    feedback = []
    
    # Load the Knowledge Base
    try:
        with open('rules.json', 'r') as f:
            rules = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        feedback.append({'text': "Critical Error: Could not load or parse rules.json.", 'type': 'negative'})
        return feedback

    # --- Pre-calculations ---
    calculated_values = {}
    founded_year = company_data.get('foundedYear')
    if founded_year and isinstance(founded_year, int):
        calculated_values['age'] = datetime.now().year - founded_year

    market_size_str = _get_nested_value(company_data, 'market_size')
    if market_size_str:
        calculated_values['parsed_market_size'] = _parse_numerical_value(market_size_str)

    total_funding_str = _get_nested_value(company_data, 'total_funding')
    if total_funding_str:
        calculated_values['parsed_total_funding'] = _parse_numerical_value(total_funding_str)
    
    company_data['calculated'] = calculated_values

    # --- Run Checks ---
    critical_flags = check_critical_red_flags(company_data, rules)
    feedback.extend(critical_flags)

    # Process positive signals
    for signal in rules.get('positive_signals', []):
        actual_value = _get_nested_value(company_data, signal['check'])
        if actual_value is None:
            continue
        
        operator = signal.get('operator')
        if operator == 'lt' and actual_value < signal['threshold']:
            feedback.append({'text': signal['message'].format(ratio=actual_value, months=actual_value), 'type': 'positive'})
        elif operator == 'gt' and actual_value > signal['threshold']:
            feedback.append({'text': signal['message'].format(ratio=actual_value, rate=actual_value), 'type': 'positive'})
        elif operator == 'contains' and signal.get('contains') in str(actual_value):
             feedback.append({'text': signal['message'], 'type': 'positive'})
        elif operator == 'contains_any' and any(keyword in str(actual_value) for keyword in signal['contains_any']):
            feedback.append({'text': signal['message'], 'type': 'positive'})


    return feedback
