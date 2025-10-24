# prompts.py
# This file has been rewritten to align with the data requirements of app.py and api_calls.py.
# The prompts are now more specific about the JSON structure to ensure reliable data extraction.

GET_COMPANY_DATA_SYSTEM_PROMPT = """You are a financial analyst AI. Your task is to gather specific, factual data about a startup and return it in a structured JSON format.

**CRITICAL INSTRUCTIONS:**
1.  **JSON Only**: Your entire response must be a single, valid JSON object. Do not include any text before or after the JSON.
2.  **Factual Data**: Provide only verifiable, factual information. If you cannot find a specific piece of data, use "N/A" as the value. Do not make up or estimate data.
3.  **Exact Keys**: Use the exact JSON keys specified in the user prompt.
4.  **Be Concise**: Provide direct answers without additional commentary.
"""

GET_COMPANY_PROFILE_PROMPT_TEMPLATE = """**CRITICAL:** Your entire response must be a single, valid JSON object. Do not include any text, titles, or markdown before or after the JSON.

Gather profile and business model information for the startup "{startup_name}" in the {sector} sector.

Return the data in a JSON object with the following structure:
{{
    "name": "Official company name",
    "foundedYear": 20XX,
    "geo": {{
        "city": "City",
        "country": "Country",
        "address": "Full Address"
    }},
    "domain": "company.com",
    "description": "A concise, factual company description.",
    "metrics": {{
        "employees": 123
    }},
    "social_media": {{
        "linkedin": "linkedin.com/company/...",
        "twitter": "twitter.com/..."
    }},
    "category": {{
        "sector": "Primary Sector",
        "sub_sector": "Sub-sector",
        "industry": "Industry",
        "activity": "Specific activity"
    }},
    "business_model": "e.g., B2B, B2C, Marketplace",
    "revenue_model": "e.g., SaaS, Transactional, Licensing",
    "pricing_model": "e.g., Subscription, Usage-based, One-time",
    "revenue_stream_diversified": "Yes/No/Partially"
}}
"""

GET_FINANCIALS_PROMPT_TEMPLATE = """**CRITICAL:** Your entire response must be a single, valid JSON object. Do not include any text, titles, or markdown before or after the JSON.

Gather specific financial data for the startup "{startup_name}". This data is often private, but search diligently for any public announcements, funding rounds, or news articles that may disclose it.

Return the data in a JSON object with the following structure:
{{
    "total_funding": "e.g., $100M",
    "last_funding_round": "e.g., Series C, $50M, 2023-10-26",
    "valuation": "e.g., $1B",
    "revenue": "e.g., $20M ARR",
    "profitability": "e.g., Profitable, Unprofitable, Breakeven",
    "key_investors": [
        "Investor 1",
        "Investor 2"
    ],
    "stage": "e.g., Seed, Series A, Growth",
    "aggregate_founder_shareholding": "e.g., 40%"
}}
"""

GET_MARKET_COMPETITION_PROMPT_TEMPLATE = """**CRITICAL:** Your entire response must be a single, valid JSON object. Do not include any text, titles, or markdown before or after the JSON.

Analyze the market and competition for the startup "{startup_name}".

Return the data in a JSON object with the following structure:
{{
    "market_size": "e.g., $50B (2024)",
    "market_growth_rate": "e.g., 15% CAGR",
    "competitive_advantage": "What is their main sustainable advantage?",
    "product_differentiation": "How is their product different from competitors?",
    "innovative_solution": "Describe the core innovative solution or technology.",
    "technology_stack": "What are the key technologies, frameworks, or platforms they use?",
    "product_roadmap": "Are there any publicly mentioned future products or features?",
    "competitors": [
        "Competitor A",
        "Competitor B"
    ],
    "patents": [
        "Patent 1",
        "Patent 2"
    ],
    "product_validation": "Evidence of market fit (e.g., case studies, user testimonials, major client names)."
}}
"""

GET_TEAM_CULTURE_PROMPT_TEMPLATE = """**CRITICAL:** Your entire response must be a single, valid JSON object. Do not include any text, titles, or markdown before or after the JSON.

Analyze the team and culture of the startup "{startup_name}".

Return the data in a JSON object with the following structure:
{{
    "founders_analysis": {{
        "names_of_founders": ["Founder 1", "Founder 2"],
        "number_of_founders": 2,
        "complementarity": "Do the founders have complementary skills?",
        "key_competency": "What is the core competency of the founding team?",
        "prior_startup_experience": "e.g., First-time founders, one previous exit.",
        "red_flags": "Any controversies or concerns? (e.g., legal issues, high turnover)"
    }},
    "key_hires": [
        "Name/Role of a key non-founder employee"
    ],
    "employee_growth_rate": "e.g., 50% YoY",
    "glassdoor_rating": "Search for '{startup_name} Glassdoor rating' and return the score out of 5."
}}
"""

# Prompts for the second layer of AI analysis (Groq)
# These prompts are more open-ended and are designed for a more powerful model.
# They are generally well-structured, so we will keep them as they are.

QUALITATIVE_ANALYSIS_SYSTEM_PROMPT = """You are an experienced venture capital analyst performing qualitative analysis.

Be critical and analytical. Point out concerns as readily as positives.
Base all analysis on the provided data - do not make assumptions.
Avoid making overly confident statements without strong evidence.
Return analysis in valid JSON format."""

QUALITATIVE_ANALYSIS_USER_PROMPT_TEMPLATE = """**CRITICAL:** Your entire response must be a single, valid JSON object. Do not include any text, titles, or markdown before or after the JSON.

Analyze this company data and provide strategic insights:

{prompt_context}

Provide:
1. SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)
2. Competitive Landscape assessment
3. TAM Analysis (realistic market opportunity)
4. Key Highlights (5-7 bullet points, mix of positive and concerning)

Return as JSON:
{{
  "swot_analysis": "comprehensive text",
  "competitive_landscape": "comprehensive text",
  "tam_analysis": "comprehensive text",
  "key_highlights": ["point 1", "point 2", ...]
}}
"""

INVESTMENT_THESIS_SYSTEM_PROMPT = """You are a venture capital partner making investment recommendations.

Be brutally honest. If data suggests problems, say so clearly.
Focus on metrics and evidence, not marketing language.
Return in valid JSON format."""

INVESTMENT_THESIS_USER_PROMPT_TEMPLATE = """**CRITICAL:** Your entire response must be a single, valid JSON object. Do not include any text, titles, or markdown before or after the JSON.

Based on this company analysis, provide an investment thesis:

{prompt_context}

Provide:
1. Investment Summary (2-3 paragraphs)
2. Key Risks (be specific)
3. Investment Recommendation (INVEST, PASS, or NEEDS MORE INFO with reasoning)

Return as JSON:
{{
  "investment_summary": "detailed summary",
  "key_risks": "detailed risk analysis",
  "investment_recommendation": "clear recommendation with reasoning"
}}
"""