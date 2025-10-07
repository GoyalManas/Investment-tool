# api_calls.py - Fixed with robust JSON extraction
import streamlit as st
import os
import json
import requests
import re
from groq import Groq
from prompts import (
    GET_COMPANY_DATA_SYSTEM_PROMPT,
    GET_COMPANY_PROFILE_PROMPT_TEMPLATE,
    GET_FINANCIALS_PROMPT_TEMPLATE,
    GET_MARKET_COMPETITION_PROMPT_TEMPLATE,
    GET_TEAM_CULTURE_PROMPT_TEMPLATE,
    QUALITATIVE_ANALYSIS_SYSTEM_PROMPT,
    QUALITATIVE_ANALYSIS_USER_PROMPT_TEMPLATE,
    INVESTMENT_THESIS_SYSTEM_PROMPT,
    INVESTMENT_THESIS_USER_PROMPT_TEMPLATE
)
import concurrent.futures

def _extract_json_from_response(raw_content):
    """Extracts a JSON object from a raw string response with MUCH better robustness."""
    
    # 1. Try to find JSON within ```json ... ```
    match = re.search(r'```json\s*(\{.*?\})\s*```', raw_content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 2. Try to parse the entire response as JSON
    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        pass

    # 3. Try to find a JSON object with better regex
    # This handles nested braces better
    brace_count = 0
    start_idx = -1
    
    for i, char in enumerate(raw_content):
        if char == '{':
            if brace_count == 0:
                start_idx = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx != -1:
                try:
                    potential_json = raw_content[start_idx:i+1]
                    # Fix common JSON issues
                    potential_json = _fix_json_formatting(potential_json)
                    return json.loads(potential_json)
                except json.JSONDecodeError:
                    continue

    # 4. Last resort: try to extract key-value pairs and build JSON
    print(f"!!! WARNING: Could not parse JSON properly. Attempting to extract fields...")
    return _extract_fields_from_text(raw_content)


def _fix_json_formatting(json_str):
    """Fix common JSON formatting issues."""
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix unquoted keys (common in malformed JSON)
    json_str = re.sub(r'(\w+):', r'"\1":', json_str)
    
    # Fix single quotes to double quotes
    json_str = json_str.replace("'", '"')
    
    return json_str


def _extract_fields_from_text(text):
    """Extract field values from poorly formatted text as fallback."""
    data = {}
    
    # Try to extract key patterns
    patterns = {
        'name': r'"name"\s*:\s*"([^"]+)"',
        'description': r'"description"\s*:\s*"([^"]+)"',
        'foundedYear': r'"foundedYear"\s*:\s*(\d+)',
        'revenue': r'"(?:revenue|current_annual_revenue[^"]*?)"\s*:\s*"([^"]+)"',
        'total_funding': r'"total_funding"\s*:\s*"([^"]+)"',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(1)
    
    return data if data else {"error": "Could not parse response"}


def _make_perplexity_request(prompt_template, startup_name, sector):
    """Makes a single request to the Perplexity API."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return {"error": "Critical: PERPLEXITY_API_KEY environment variable not found."}

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    
    prompt = prompt_template.format(startup_name=startup_name, sector=sector)
    
    # Add explicit JSON formatting instruction
    prompt += "\n\nIMPORTANT: Return ONLY valid JSON. Ensure all keys and string values are properly quoted with double quotes."
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": GET_COMPANY_DATA_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        raw_content = response.json()['choices'][0]['message']['content']
        
        # Debug: print raw content
        print(f"\n=== RAW RESPONSE for {prompt_template.__name__ if hasattr(prompt_template, '__name__') else 'prompt'} ===")
        print(raw_content[:500])  # First 500 chars
        print("===\n")
        
        return _extract_json_from_response(raw_content)
    except Exception as e:
        print(f"!!! PERPLEXITY API ERROR: {e}") 
        return {"error": f"An unexpected error occurred with Perplexity: {e}"}


def _parse_currency(value):
    """Parse currency strings including Indian format like '2,473,00,00,000'."""
    if not value or value == 'N/A' or value == 'Not Disclosed' or not isinstance(value, str):
        return None
    
    # Remove currency symbols, spaces, and convert to lowercase
    value = re.sub(r'[€$£₹,\s]', '', value.lower())
    
    # Handle 'crore' (Indian numbering - 1 crore = 10 million)
    if 'crore' in value or 'cr' in value:
        value = value.replace('crore', '').replace('cr', '')
        try:
            return float(value) * 10_000_000
        except:
            pass
    
    # Handle 'lakh' (Indian numbering - 1 lakh = 100 thousand)
    if 'lakh' in value or 'lac' in value:
        value = value.replace('lakh', '').replace('lac', '')
        try:
            return float(value) * 100_000
        except:
            pass
    
    multipliers = {
        'b': 1_000_000_000,
        'billion': 1_000_000_000,
        'm': 1_000_000,
        'million': 1_000_000,
        'k': 1_000,
        'thousand': 1_000,
    }
    
    for suffix, multiplier in multipliers.items():
        if suffix in value:
            try:
                num = float(value.replace(suffix, ''))
                return num * multiplier
            except:
                continue
    
    # Try to parse as plain number
    try:
        return float(value)
    except:
        return None


def _calculate_capital_efficiency(total_funding, arr):
    """Calculate funding-to-revenue ratio."""
    if not arr or arr <= 0:
        return None, "Cannot calculate (no revenue)"
    
    ratio = total_funding / arr
    
    if ratio < 2:
        rating = "EXCELLENT - Very capital efficient"
    elif ratio < 5:
        rating = "GOOD - Reasonable efficiency"
    elif ratio < 10:
        rating = "CONCERNING - High funding vs revenue"
    else:
        rating = "🚨 RED FLAG - Poor capital efficiency"
    
    return round(ratio, 2), rating


@st.cache_data
def get_company_data(startup_name, sector):
    """Gathers company data from Perplexity AI by making parallel API calls."""
    company_data = {}
    
    prompt_templates = {
        "profile": GET_COMPANY_PROFILE_PROMPT_TEMPLATE,
        "financials": GET_FINANCIALS_PROMPT_TEMPLATE,
        "market": GET_MARKET_COMPETITION_PROMPT_TEMPLATE,
        "team": GET_TEAM_CULTURE_PROMPT_TEMPLATE,
    }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_prompt = {
            executor.submit(_make_perplexity_request, template, startup_name, sector): name
            for name, template in prompt_templates.items()
        }
        for future in concurrent.futures.as_completed(future_to_prompt):
            prompt_name = future_to_prompt[future]
            try:
                data = future.result()
                if data.get("error"):
                    print(f"Error fetching {prompt_name} data: {data['error']}")
                    # Continue anyway - partial data is better than nothing
                company_data.update(data)
            except Exception as exc:
                print(f"{prompt_name} generated an exception: {exc}")

    # Ensure required fields exist with defaults
    if 'name' not in company_data or not company_data['name']:
        company_data['name'] = startup_name
    
    if 'description' not in company_data or not company_data['description']:
        company_data['description'] = f"{startup_name} is a company in the {sector} sector."
    
    if 'foundedYear' not in company_data or not company_data['foundedYear']:
        company_data['foundedYear'] = 2020  # Default placeholder
    
    # Add calculated metrics
    company_data['calculated'] = {}
    
    # Try multiple revenue field names
    revenue_fields = ['revenue', 'current_annual_revenue_in_usd', 'current_annual_revenue_in_inr', 
                     'annual_recurring_revenue', 'arr']
    arr_numeric = None
    for field in revenue_fields:
        if field in company_data:
            arr_numeric = _parse_currency(company_data[field])
            if arr_numeric:
                break
    
    # Try multiple funding field names
    funding_fields = ['total_funding', 'total_funding_raised', 'funding']
    total_funding_numeric = None
    for field in funding_fields:
        if field in company_data:
            total_funding_numeric = _parse_currency(company_data[field])
            if total_funding_numeric:
                break
    
    if arr_numeric:
        company_data['calculated']['arr_numeric'] = arr_numeric
        # Ensure revenue field exists for display
        if not company_data.get('revenue'):
            company_data['revenue'] = f"${arr_numeric/1e6:.1f}M"
    
    if total_funding_numeric:
        company_data['calculated']['total_funding_numeric'] = total_funding_numeric
        # Ensure total_funding field exists for display
        if not company_data.get('total_funding'):
            company_data['total_funding'] = f"${total_funding_numeric/1e6:.1f}M"
    
    # Calculate capital efficiency if we have both values
    if arr_numeric and total_funding_numeric:
        ratio, rating = _calculate_capital_efficiency(total_funding_numeric, arr_numeric)
        company_data['calculated']['capital_efficiency_ratio'] = ratio
        company_data['calculated']['capital_efficiency_rating'] = rating
        
        # Add warning if concerning
        if ratio and ratio > 10:
            company_data['capital_efficiency_warning'] = (
                f"⚠️ WARNING: Raised ${total_funding_numeric/1e6:.1f}M for only "
                f"${arr_numeric/1e6:.1f}M in revenue ({ratio}x ratio). This is very concerning."
            )
        elif ratio and ratio > 5:
            company_data['capital_efficiency_warning'] = (
                f"⚠️ WATCH: Raised ${total_funding_numeric/1e6:.1f}M for "
                f"${arr_numeric/1e6:.1f}M in revenue ({ratio}x ratio). Monitor efficiency."
            )

    return company_data


@st.cache_data
def generate_qualitative_analysis(company_data):
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    
    prompt_context = f"""Company Name: {company_data.get('name', 'N/A')}
Description: {company_data.get('description', 'N/A')}
Sector: {company_data.get('category', {}).get('sector', 'N/A')}
Location: {company_data.get('geo', {}).get('city', 'N/A')}
Year Founded: {company_data.get('foundedYear', 'N/A')}
Team Size: {company_data.get('metrics', {}).get('employees', 'N/A')}
Revenue: {company_data.get('revenue', 'N/A')}
Funding: {company_data.get('total_funding', 'N/A')}
Capital Efficiency: {company_data.get('calculated', {}).get('capital_efficiency_rating', 'N/A')}
Competitors: {', '.join(company_data.get('competitors', []))}
"""
    
    user_prompt = QUALITATIVE_ANALYSIS_USER_PROMPT_TEMPLATE.format(prompt_context=prompt_context)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": QUALITATIVE_ANALYSIS_SYSTEM_PROMPT}, 
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        raw_content = response.choices[0].message.content
        return _extract_json_from_response(raw_content)
    except Exception as e:
        return {"error": f"LLM generation failed with an unexpected error: {e}"}


def get_company_data_with_analysis(startup_name, sector):
    """
    Gathers company data, then runs qualitative analysis, and returns a combined dictionary.
    """
    company_data = get_company_data(startup_name, sector)
    if company_data.get("error"):
        return company_data # Return early if there was an error

    # Now, run the qualitative analysis
    llm_analysis = generate_qualitative_analysis(company_data)
    if llm_analysis.get("error"):
        # We can decide if we want to return an error or just the company_data
        # For now, let's add the error to the main dict and return
        company_data['analysis_error'] = llm_analysis['error']
    else:
        # Merge the analysis into the main company_data dictionary
        company_data['financial_analysis'] = llm_analysis

    return company_data


