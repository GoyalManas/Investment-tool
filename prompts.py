# prompts.py
# Complete prompts file for investment analysis tool

GET_COMPANY_DATA_SYSTEM_PROMPT = """You are a financial analyst gathering data for investment due diligence.

CRITICAL RULES:
1. Return ONLY factual, verifiable information with sources
2. Use EXACT numbers - never estimate or guess
3. If data is not publicly available, return "Not Disclosed" 
4. Prefer recent data (last 12 months) over older data
5. Always return valid JSON format
6. Be skeptical of marketing claims - verify with multiple sources

Format all responses as valid JSON."""

GET_COMPANY_PROFILE_PROMPT_TEMPLATE = """
Find detailed company profile information for {startup_name} in the {sector} sector.

Required Information:
1. Basic Details:
   - Official company name
   - Year founded (exact year)
   - Headquarters location (city, country, full address if available)
   - Website URL
   - Company description (concise, factual)
   - Current team size/employee count

2. Business Model:
   - Business model type (B2B, B2C, B2B2C, Marketplace)
   - Revenue model (SaaS, Transaction fees, Licensing, etc.)
   - Pricing model (Subscription, Usage-based, One-time, Freemium)
   - Revenue stream diversification (multiple products/services?)

3. Sector Classification:
   - Primary sector
   - Sub-sector
   - Industry
   - Specific activity/focus area

4. Social Media & Online Presence:
   - LinkedIn URL
   - Twitter/X URL
   - GitHub (if applicable)

Return as JSON with all fields filled or "Not Disclosed" if unavailable.
"""

GET_FINANCIALS_PROMPT_TEMPLATE = """
Find SPECIFIC FINANCIAL DATA for {startup_name} in {sector}.

CRITICAL: Return ONLY verified numbers with sources. NO estimates or ranges.

1. REVENUE METRICS:
   - Current Annual Recurring Revenue (ARR) or revenue (exact $ amount)
   - Revenue from 12 months ago (for growth calculation)
   - Year-over-year growth rate (%)

2. FUNDING & CAPITAL:
   - Total funding raised (exact $ amount)
   - Last funding round: Date, Amount, Round type, Valuation if disclosed
   - Key investors/VCs

3. UNIT ECONOMICS (if disclosed):
   - Average Contract Value (ACV)
   - Customer Acquisition Cost (CAC)
   - Lifetime Value (LTV)
   - Gross margin percentage
   - Net Dollar Retention (NDR)

4. PROFITABILITY:
   - Current profitability status

Return as JSON. Use "Not Disclosed" for unavailable data.
"""

GET_MARKET_COMPETITION_PROMPT_TEMPLATE = """
Analyze the market and competitive landscape for {startup_name} in {sector}.

1. MARKET SIZE & DYNAMICS:
   - Total Addressable Market (TAM) size ($ amount with year)
   - Market growth rate (CAGR %)
   - Market description

2. DIRECT COMPETITORS (Top 5):
   - Company names
   - Their key advantages

3. COMPETITIVE POSITIONING:
   - {startup_name}'s unique value proposition
   - Competitive advantages (specific, verifiable)
   - Product differentiation

4. PRODUCT VALIDATION:
   - Specific customer names (at least 3-5 if available)
   - Product validation evidence
   - Patents or IP if any

Return as JSON.
"""

GET_TEAM_CULTURE_PROMPT_TEMPLATE = """
Research the team, founders, and company culture for {startup_name}.

1. FOUNDERS (for EACH founder):
   - Full names of all founders
   - Current roles
   - Previous companies/roles
   - Previous startup experience (founded, sold, failed?)
   - Domain expertise
   - Any red flags

2. TEAM METRICS:
   - Current team size
   - Team size 1 year ago (for growth rate)

3. CULTURE:
   - Glassdoor rating (out of 5)
   - Number of reviews
   - Common themes in reviews

Return as JSON.
"""

QUALITATIVE_ANALYSIS_SYSTEM_PROMPT = """You are an experienced venture capital analyst performing qualitative analysis.

Be critical and analytical. Point out concerns as readily as positives.
Base all analysis on the provided data - do not make assumptions.
Return analysis in valid JSON format."""

QUALITATIVE_ANALYSIS_USER_PROMPT_TEMPLATE = """
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

INVESTMENT_THESIS_USER_PROMPT_TEMPLATE = """
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
