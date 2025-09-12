# api_calls.py
import os
import json
import requests
from groq import Groq

# --- KNOWLEDGE LAYER 1: LIVE WEB SEARCH VIA PERPLEXITY AI (Working) ---
def get_company_data(startup_name):
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return {"error": "Critical: PERPLEXITY_API_KEY environment variable not found."}

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    prompt = f"""
    Find factual information about the startup "{startup_name}". You must provide your response as a valid JSON object.
    The JSON object should have the following keys: "name", "description", "foundedYear", "domain", "geo" (an object with "city" and "country"), "metrics" (an object with "employees"), "category" (an object with "sector" and "industry"), "tags" (a list of relevant keywords), and also try to find "founders" (a list of founder names), and "business_model" (a short description).
    If you cannot find a specific piece of information, use "N/A" as the value. For lists like "founders", if none are found, use an empty list []. Do not add any text or explanation outside of the JSON object.
    """
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "You are an AI assistant that provides company data in a structured JSON format."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        response_json = response.json()
        raw_content = response_json['choices'][0]['message']['content']
        
        start_index = raw_content.find('{')
        end_index = raw_content.rfind('}')
        
        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_response_string = raw_content[start_index:end_index+1]
        else:
            return {"error": f"Could not find a valid JSON object in the model's response. Raw response: '{raw_content}'"}

        return json.loads(json_response_string)
    except Exception as e:
        return {"error": f"An unexpected error occurred with Perplexity: {e}"}


# --- KNOWLEDGE LAYER 2: DEEP ANALYSIS VIA GROQ (With Polished Prompt) ---
def generate_qualitative_analysis(company_data):
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    prompt_context = f"Company Name: {company_data.get('name', 'N/A')}\nDescription: {company_data.get('description', 'N/A')}\nSector: {company_data.get('category', {}).get('sector', 'N/A')}\nTags: {company_data.get('tags', [])}\nLocation: {company_data.get('geo', {}).get('city', 'N/A')}\nYear Founded: {company_data.get('foundedYear', 'N/A')}\nTeam Size: {company_data.get('metrics', {}).get('employees', 'N/A')}"
    system_prompt = "You are an expert VC analyst. You MUST respond with a valid JSON object and nothing else."
    
    # =================================================================
    # THIS IS THE CORRECTED, POLISHED PROMPT
    # =================================================================
    user_prompt = f"""
    Based on this data:\n{prompt_context}\n\nGenerate a concise analysis covering the keys: 'products_services', 'market_description', 'traction_analysis', and 'key_highlights'.
    The value for each key should be a simple string, and the value for 'key_highlights' should be a list of strings. Do not use nested dictionaries.
    """
    # =================================================================

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.7,
        )
        raw_content = response.choices[0].message.content
        
        start_index = raw_content.find('{')
        end_index = raw_content.rfind('}')
        
        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_response_string = raw_content[start_index:end_index+1]
        else:
            return {"error": f"Could not find a valid JSON object in the Groq model's response. Raw response: '{raw_content}'"}

        return json.loads(json_response_string)
    except Exception as e:
        return {"error": f"LLM generation failed with an unexpected error: {e}"}