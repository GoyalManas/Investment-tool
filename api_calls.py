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
from new_prompts import (
    FOUNDERS_ANALYSIS_SYSTEM_PROMPT,
    FOUNDERS_PRESEED_SEED_PROMPT,
    FOUNDERS_EARLY_STAGE_PROMPT,
    FOUNDERS_GROWTH_STAGE_PROMPT,
    FOUNDERS_LATER_STAGE_PROMPT,
    FOUNDERS_FINTECH_PROMPT,
    FOUNDERS_HEALTHTECH_PROMPT,
    PRODUCT_ANALYSIS_SYSTEM_PROMPT,
    PRODUCT_PRESEED_SEED_PROMPT,
    PRODUCT_EARLY_STAGE_PROMPT,
    PRODUCT_GROWTH_STAGE_PROMPT,
    PRODUCT_LATER_STAGE_PROMPT,
    PRODUCT_FINTECH_PROMPT,
    PRODUCT_HEALTHTECH_PROMPT
)
import concurrent.futures

def _extract_json_from_response(raw_content):
    """Extracts and merges all JSON objects from a raw string response."""
    print(f"--- RAW CONTENT ---\n{raw_content}\n--- END RAW CONTENT ---")
    
    merged_json = {}
    
    # First, try to find JSON within ```json ... ``` blocks
    json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', raw_content, re.DOTALL)
    for block in json_blocks:
        try:
            merged_json.update(json.loads(block))
        except json.JSONDecodeError as e:
            print(f"!!! JSONDecodeError in json block: {e}")

    # Then, process the rest of the content
    content_without_blocks = re.sub(r'```json\s*(\{.*?\})\s*```', '', raw_content, flags=re.DOTALL)
    
    # Find all top-level JSON objects in the remaining content
    brace_level = 0
    start_index = -1
    
    for i, char in enumerate(content_without_blocks):
        if char == '{':
            if brace_level == 0:
                start_index = i
            brace_level += 1
        elif char == '}':
            if brace_level > 0:
                brace_level -= 1
                if brace_level == 0 and start_index != -1:
                    json_str = content_without_blocks[start_index:i+1]
                    try:
                        merged_json.update(json.loads(json_str))
                        start_index = -1
                    except json.JSONDecodeError as e:
                        print(f"!!! JSONDecodeError parsing object: {e}")

    if not merged_json:
        print(f"!!! FAILED TO EXTRACT JSON. Raw response was:\n{raw_content}")
        return {"error": "Could not find a valid JSON object in the model's response."}

    return merged_json

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

def get_stage_prompt(stage_str, prompt_map):
    if not isinstance(stage_str, str):
        return None
    stage_str = stage_str.lower()
    if "preseed" in stage_str or "seed" in stage_str:
        return prompt_map["preseed_seed"]
    elif "early" in stage_str or "series a" in stage_str:
        return prompt_map["early_stage"]
    elif "growth" in stage_str or "series b" in stage_str:
        return prompt_map["growth_stage"]
    elif "later" in stage_str or "series c" in stage_str or "series d" in stage_str:
        return prompt_map["later_stage"]
    return None

def get_sector_prompt(sector_str, prompt_map):
    if not isinstance(sector_str, str):
        return None
    sector_str = sector_str.lower()
    if "fintech" in sector_str:
        return prompt_map["fintech"]
    elif "healthtech" in sector_str:
        return prompt_map["healthtech"]
    return None

@st.cache_data
def generate_founders_analysis(company_data):
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    
    stage = company_data.get("stage", "N/A")
    sector = company_data.get("category", {}).get("sector", "N/A")
    
    stage_prompt_map = {
        "preseed_seed": FOUNDERS_PRESEED_SEED_PROMPT,
        "early_stage": FOUNDERS_EARLY_STAGE_PROMPT,
        "growth_stage": FOUNDERS_GROWTH_STAGE_PROMPT,
        "later_stage": FOUNDERS_LATER_STAGE_PROMPT
    }
    
    sector_prompt_map = {
        "fintech": FOUNDERS_FINTECH_PROMPT,
        "healthtech": FOUNDERS_HEALTHTECH_PROMPT
    }
    
    stage_prompt = get_stage_prompt(stage, stage_prompt_map)
    sector_prompt = get_sector_prompt(sector, sector_prompt_map)
    
    if not stage_prompt and not sector_prompt:
        return {"error": "Could not determine stage or sector for founders analysis."}
        
    prompt_context = f"Company Name: {company_data.get('name', 'N/A')}\nDescription: {company_data.get('description', 'N/A')}\nSector: {company_data.get('category', {}).get('sector', 'N/A')}\nStage: {stage}"
    
    user_prompt_parts = []
    if stage_prompt:
        user_prompt_parts.append(stage_prompt)
    if sector_prompt:
        user_prompt_parts.append(sector_prompt)
    
    user_prompt = "\n".join(user_prompt_parts)
        
    user_prompt = user_prompt.format(prompt_context=prompt_context)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": FOUNDERS_ANALYSIS_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
            temperature=0.7,
        )
        raw_content = response.choices[0].message.content
        return _extract_json_from_response(raw_content)
    except Exception as e:
        return {"error": f"LLM generation failed for founders analysis with an unexpected error: {e}"}

@st.cache_data
def generate_product_analysis(company_data):
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    
    stage = company_data.get("stage", "N/A")
    sector = company_data.get("category", {}).get("sector", "N/A")
    
    stage_prompt_map = {
        "preseed_seed": PRODUCT_PRESEED_SEED_PROMPT,
        "early_stage": PRODUCT_EARLY_STAGE_PROMPT,
        "growth_stage": PRODUCT_GROWTH_STAGE_PROMPT,
        "later_stage": PRODUCT_LATER_STAGE_PROMPT
    }
    
    sector_prompt_map = {
        "fintech": PRODUCT_FINTECH_PROMPT,
        "healthtech": PRODUCT_HEALTHTECH_PROMPT
    }
    
    stage_prompt = get_stage_prompt(stage, stage_prompt_map)
    sector_prompt = get_sector_prompt(sector, sector_prompt_map)
    
    if not stage_prompt and not sector_prompt:
        return {"error": "Could not determine stage or sector for product analysis."}
        
    prompt_context = f"Company Name: {company_data.get('name', 'N/A')}\nDescription: {company_data.get('description', 'N/A')}\nSector: {company_data.get('category', {}).get('sector', 'N/A')}\nStage: {stage}"
    
    user_prompt_parts = []
    if stage_prompt:
        user_prompt_parts.append(stage_prompt)
    if sector_prompt:
        user_prompt_parts.append(sector_prompt)
    
    user_prompt = "\n".join(user_prompt_parts)
        
    user_prompt = user_prompt.format(prompt_context=prompt_context)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": PRODUCT_ANALYSIS_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
            temperature=0.7,
        )
        raw_content = response.choices[0].message.content
        return _extract_json_from_response(raw_content)
    except Exception as e:
        return {"error": f"LLM generation failed for product analysis with an unexpected error: {e}"}