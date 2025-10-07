# test_perplexity_prompt.py
import os
import requests
import json
from dotenv import load_dotenv
from prompts import GET_COMPANY_DATA_SYSTEM_PROMPT, GET_COMPANY_DATA_USER_PROMPT_TEMPLATE

# --- SETUP ---
load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY")

# --- CONFIGURATION ---
STARTUP_NAME = "Paytm"
SECTOR = "FinTech"

# --- EXECUTION ---
print("--- Starting Perplexity Prompt Test ---")

if not API_KEY:
    print("\n❌ CRITICAL ERROR: PERPLEXITY_API_KEY not found in your .env file.")
    exit()

print(f"\n✅ API Key loaded. Testing with startup: '{STARTUP_NAME}'")

# --- API CALL ---
url = "https://api.perplexity.ai/chat/completions"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {API_KEY}"
}
prompt = GET_COMPANY_DATA_USER_PROMPT_TEMPLATE.format(startup_name=STARTUP_NAME, sector=SECTOR)
payload = {
    "model": "sonar",
    "messages": [
        {"role": "system", "content": GET_COMPANY_DATA_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=45)
    print(f"\nHTTP Status Code: {response.status_code}")

    if response.status_code == 200:
        raw_content = response.json()['choices'][0]['message']['content']
        print("\n--- RAW AI RESPONSE (before JSON parsing) ---")
        print(raw_content)
        print("------------------------------------------")
    else:
        print("\n--- ERROR RESPONSE ---")
        print(response.text)
        print("--------------------")

except Exception as e:
    print(f"\n--- A CRITICAL ERROR OCCURRED ---")
    print(e)
    print("---------------------------------")

print("\n--- Test Finished ---")