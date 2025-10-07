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
    """Extracts a JSON object from a raw string response with improved robustness."""
    
    # 1. Try to find JSON within ```json ... ```
    match = re.search(r'```json\s*(\{.*\})\s*```', raw_content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass  # Fall through to the next method

    # 2. Use a more robust regex to find a JSON object
    match = re.search(r'\{(?:[^\{}|\{[^\{}*\})*\}', raw_content)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass # Fall through to the next method

    # 3. Try to find the first '{' and the last '}'
    try:
        start = raw_content.find('{')
        end = raw_content.rfind('}')
        if start != -1 and end != -1:
            return json.loads(raw_content[start:end+1])
    except json.JSONDecodeError:
        pass # Fall through to the error

    # 4. If all else fails, return an error
    print(f"!!! FAILED TO EXTRACT JSON. Raw response was:\n{raw_content}")
    return {"error": "Could not find a valid JSON object in the model's response."}


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
        return _extract_json_from_response(raw_content)
    except Exception as e:
        print(f"!!! PERPLEXITY API ERROR: {e}") 
        return {"error": f"An unexpected error occurred with Perplexity: {e}"}


# --- KNOWLEDGE LAYER 1: LIVE WEB SEARCH VIA PERPLEXITY AI (Working) ---
@st.cache_data
def get_company_data(startup_name, sector):
    """
    Gathers company data from Perplexity AI by making parallel API calls.
    """
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
                company_data.update(data)
            except Exception as exc:
                print(f"{prompt_name} generated an exception: {exc}")

    return company_data


# --- KNOWLEDGE LAYER 2: DEEP ANALYSIS VIA GROQ (With Polished Prompt) ---
@st.cache_data
def generate_qualitative_analysis(company_data):
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    prompt_context = f"Company Name: {company_data.get('name', 'N/A')}\nDescription: {company_data.get('description', 'N/A')}\nSector: {company_data.get('category', {}).get('sector', 'N/A')}\nTags: {company_data.get('tags', [])}\nLocation: {company_data.get('geo', {}).get('city', 'N/A')}\nYear Founded: {company_data.get('foundedYear', 'N/A')}\nTeam Size: {company_data.get('metrics', {}).get('employees', 'N/A')}"
    
    user_prompt = QUALITATIVE_ANALYSIS_USER_PROMPT_TEMPLATE.format(prompt_context=prompt_context)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": QUALITATIVE_ANALYSIS_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
            temperature=0.7,
        )
        raw_content = response.choices[0].message.content
        return _extract_json_from_response(raw_content)
    except Exception as e:
        return {"error": f"LLM generation failed with an unexpected error: {e}"}

@st.cache_data
def generate_investment_thesis(company_data, llm_analysis):
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    
    prompt_context = f"Company Name: {company_data.get('name', 'N/A')}\nSWOT Analysis: {llm_analysis.get('swot_analysis', 'N/A')}\nCompetitive Landscape: {llm_analysis.get('competitive_landscape', 'N/A')}\nTAM Analysis: {llm_analysis.get('tam_analysis', 'N/A')}\nTeam: {company_data.get('founders_analysis', {})}\nKey Highlights: {llm_analysis.get('key_highlights', [])}"

    user_prompt = INVESTMENT_THESIS_USER_PROMPT_TEMPLATE.format(prompt_context=prompt_context)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": INVESTMENT_THESIS_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
            temperature=0.8,
        )
        raw_content = response.choices[0].message.content
        return _extract_json_from_response(raw_content)
    except Exception as e:
        return {"error": f"LLM generation failed for thesis with an unexpected error: {e}"}