import os
from dotenv import load_dotenv
from api_calls import _make_perplexity_request
from prompts import GET_TEAM_CULTURE_PROMPT_TEMPLATE

load_dotenv()

startup_name = "Intelligencia AI"
sector = "Healthtech"

print("Testing Perplexity API with team prompt...")
response = _make_perplexity_request(GET_TEAM_CULTURE_PROMPT_TEMPLATE, startup_name, sector)
print(response)
