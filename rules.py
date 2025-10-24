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
    # Perform any calculations required by the ruleset
    calculated_values = {}
    founded_year = company_data.get('foundedYear')
    if founded_year and isinstance(founded_year, int):
        calculated_values['age'] = datetime.now().year - founded_year

    # Parse numerical values for market_size and total_funding
    market_size_str = _get_nested_value(company_data, 'market_size')
    if market_size_str:
        calculated_values['parsed_market_size'] = _parse_numerical_value(market_size_str)

    total_funding_str = _get_nested_value(company_data, 'total_funding')
    if total_funding_str:
        calculated_values['parsed_total_funding'] = _parse_numerical_value(total_funding_str)

    # --- Rule Engine Logic ---
    for rule in rules.get('global_rules', []):
        field = rule['field_to_check']
        operator = rule['operator']
        rule_value = rule['value']

        # --- Condition Logic ---
        condition_met = True
        if "condition" in rule:
            condition = rule["condition"]
            condition_field = condition["field"]
            condition_operator = condition["operator"]
            condition_value = condition["value"]
            
            actual_condition_value = _get_nested_value(company_data, condition_field)
            
            if actual_condition_value is None:
                condition_met = False
            
            if condition_operator == "contains_any":
                if isinstance(actual_condition_value, str) and isinstance(condition_value, list):
                    condition_met = any(val.lower() in actual_condition_value.lower() for val in condition_value)
                else:
                    condition_met = False
        
        if not condition_met:
            continue

        # Get the actual value from company_data
        if field.startswith('calculated.'):
            actual_value = calculated_values.get(field.split('.')[1])
        else:
            actual_value = _get_nested_value(company_data, field)
        
        if actual_value is None:
            continue # Skip rule if data is missing

        # --- Operator Logic ---
        result = False
        if operator == 'contains':
            # Special handling for user input placeholder
            if rule_value == '{user_sector_input}':
                rule_value = user_sector_input
            if isinstance(actual_value, str):
                result = rule_value.lower() in actual_value.lower()
        
        elif operator == 'between':
            if isinstance(actual_value, (int, float)) and len(rule_value) == 2:
                result = rule_value[0] <= actual_value <= rule_value[1]
        
        elif operator == 'equals':
            result = actual_value == rule_value
            
        elif operator == 'is_empty_or_na':
            result = not actual_value or (isinstance(actual_value, str) and ('none' in actual_value.lower() or 'n/a' in actual_value.lower()))
        
        elif operator == 'is_not_empty':
            result = bool(actual_value)

        elif operator == 'length_gt':
            if isinstance(actual_value, str):
                result = len(actual_value) > rule_value
        
        elif operator == 'gt':
            if isinstance(actual_value, (int, float)):
                result = actual_value > rule_value

        elif operator == 'le':
            if isinstance(actual_value, (int, float)):
                result = actual_value <= rule_value

        elif operator == 'lt':
            if isinstance(actual_value, (int, float)):
                result = actual_value < rule_value
        
        elif operator == 'list_length_between':
            if isinstance(actual_value, list) and len(rule_value) == 2:
                result = rule_value[0] <= len(actual_value) <= rule_value[1]
        
        # --- Append Feedback ---
        template = rule['result_if_true'] if result else rule['result_if_false']
        
        # Prepare value for formatting
        display_value = actual_value
        if operator == 'list_length_between' and isinstance(actual_value, list):
            display_value = len(actual_value)

        text = template['text'].format(value=display_value)
        
        feedback.append({'text': text, 'type': template['type']})

    return feedback