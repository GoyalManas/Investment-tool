# new_prompts.py

# FOUNDERS ANALYSIS PROMPTS

FOUNDERS_ANALYSIS_SYSTEM_PROMPT = """You are a venture capital analyst specializing in founder and team assessment.
Your task is to provide a detailed analysis of the founding team based on the provided company data and stage.
Be critical and objective. Your analysis should be specific and actionable.
Return the analysis in a valid JSON format."""

# Stage-based prompts for Founders
FOUNDERS_PRESEED_SEED_PROMPT = """
Analyze the founders of this **Pre-seed/Seed** stage company:

{prompt_context}

Based on the data, comment on the following:
- **Mission Clarity:** Is their vision clear and compelling?
- **Domain Knowledge:** Do they have deep expertise in their sector?
- **Passion:** Is there evidence of strong commitment and passion?
- **Founding Team Chemistry:** Any insights into how they work together?
- **Early Entrepreneurial Grit:** Have they overcome any early challenges?
- **Technical Expertise:** Is the team technically strong enough to build the MVP?
- **Problem-Solution Fit:** Do they deeply understand the problem they are solving?
- **Early Product/Market Validation:** Any early signs of traction or user love?
- **Network Access:** Do they have access to relevant networks for hiring, sales, and funding?
- **Adaptability:** Have they shown an ability to pivot or adapt?

Return as JSON:
{{
  "mission_clarity": "analysis text",
  "domain_knowledge": "analysis text",
  "passion": "analysis text",
  "team_chemistry": "analysis text",
  "entrepreneurial_grit": "analysis text",
  "technical_expertise": "analysis text",
  "problem_solution_fit": "analysis text",
  "early_validation": "analysis text",
  "network_access": "analysis text",
  "adaptability": "analysis text"
}}
"""

FOUNDERS_EARLY_STAGE_PROMPT = """
Analyze the founders of this **Early Stage/Series A** company:

{prompt_context}

Based on the data, comment on the following:
- **Execution Capability:** Have they demonstrated an ability to execute on their vision?
- **Leadership Skills:** Are they effective leaders for a growing team?
- **Track Record:** What is their track record of success (or failure)?
- **Team-Building and Delegation:** Have they successfully built and delegated to a team?
- **Market Insight:** Do they have a deep understanding of the market dynamics?

Return as JSON:
{{
  "execution_capability": "analysis text",
  "leadership_skills": "analysis text",
  "track_record": "analysis text",
  "team_building": "analysis text",
  "market_insight": "analysis text"
}}
"""

FOUNDERS_GROWTH_STAGE_PROMPT = """
Analyze the founders of this **Growth Stage/Series B** company:

{prompt_context}

Based on the data, comment on the following:
- **Strategic Vision:** Do they have a clear and ambitious long-term vision?
- **Scalability Experience:** Have they successfully scaled a company before?
- **Fundraising Expertise:** What is their track record with fundraising?
- **Crisis Management:** Have they successfully navigated any major crises?

Return as JSON:
{{
  "strategic_vision": "analysis text",
  "scalability_experience": "analysis text",
  "fundraising_expertise": "analysis text",
  "crisis_management": "analysis text"
}}
"""

FOUNDERS_LATER_STAGE_PROMPT = """
Analyze the founders of this **Later Stage/Series C** company:

{prompt_context}

Based on the data, comment on the following:
- **Vision on Growth and Diversification:** What is their vision for future growth and diversification?
- **Scalability Experience:** Have they successfully scaled a company to a large size?
- **Fundraising Expertise:** What is their track record with late-stage fundraising?
- **Crisis Management:** Have they successfully navigated any major crises at scale?

Return as JSON:
{{
  "growth_vision": "analysis text",
  "scalability_experience": "analysis text",
  "fundraising_expertise": "analysis text",
  "crisis_management": "analysis text"
}}
"""

# Sector-based prompts for Founders
FOUNDERS_FINTECH_PROMPT = """
Analyze the founders of this **FinTech** company:

{prompt_context}

Based on the data, comment on the following:
- **Regulatory Understanding:** Do they have a deep understanding of financial regulations?
- **Financial Literacy:** Are they financially literate and credible?
- **Risk Management Mindset:** Do they have a strong risk management mindset?
- **Trust/Credibility with Financial Partners:** Have they built trust with financial partners?
- **Experience with Compliance and Cybersecurity:** Do they have experience with compliance and cybersecurity?
- **Connections to Financial Institutions:** Do they have strong connections to financial institutions?

Return as JSON:
{{
  "regulatory_understanding": "analysis text",
  "financial_literacy": "analysis text",
  "risk_management": "analysis text",
  "partner_trust": "analysis text",
  "compliance_experience": "analysis text",
  "financial_connections": "analysis text"
}}
"""

FOUNDERS_HEALTHTECH_PROMPT = """
Analyze the founders of this **HealthTech** company:

{prompt_context}

Based on the data, comment on the following:
- **Clinical/Medical Domain Expertise:** Do they have deep clinical or medical domain expertise?
- **Ethics and Regulatory Navigation:** Can they navigate the complex ethical and regulatory landscape?
- **User Empathy:** Do they have a deep empathy for patients and clinicians?
- **Partnerships with Health Systems:** Have they successfully partnered with health systems?
- **Proven Ability with Data Privacy and Sensitive Information:** Do they have a proven ability to handle sensitive health data?

Return as JSON:
{{
  "domain_expertise": "analysis text",
  "ethics_and_regulatory": "analysis text",
  "user_empathy": "analysis text",
  "health_system_partnerships": "analysis text",
  "data_privacy_ability": "analysis text"
}}
"""


# PRODUCT/SERVICE ANALYSIS PROMPTS

PRODUCT_ANALYSIS_SYSTEM_PROMPT = """You are a venture capital analyst specializing in product and technology assessment.
Your task is to provide a detailed analysis of the company's product/service based on the provided company data and stage.
Be critical and objective. Your analysis should be specific and actionable.
Return the analysis in a valid JSON format."""

# Stage-based prompts for Product/Service
PRODUCT_PRESEED_SEED_PROMPT = """
Analyze the product/service of this **Pre-seed/Seed** stage company:

{prompt_context}

Based on the data, comment on the following:
- **Clear Value Proposition:** Is the value proposition clear and compelling for a defined target customer?
- **Validated Pain Point:** Have they validated the pain point they are solving?
- **Prototype or MVP:** Is there a prototype or MVP that demonstrates the core use case and technical viability?
- **Usability and Desirability:** How is the usability and desirability measured with first users/partners?
- **Initial Compliance Checks:** Have they performed initial compliance checks for sector-specific rules?

Return as JSON:
{{
  "value_proposition": "analysis text",
  "pain_point_validation": "analysis text",
  "mvp_quality": "analysis text",
  "usability_and_desirability": "analysis text",
  "initial_compliance": "analysis text"
}}
"""

PRODUCT_EARLY_STAGE_PROMPT = """
Analyze the product/service of this **Early Stage/Series A** company:

{prompt_context}

Based on the data, comment on the following:
- **User Traction and Engagement:** What is the evidence of user traction, feedback cycles, renewals, and engagement?
- **Readiness for Scaling:** Is the product ready for the first scaling challenges?
- **Regulatory Needs:** What are the regulatory needs and have they been addressed?
- **Real-World Adoption:** What is the evidence of real-world adoption in different customer segments?

Return as JSON:
{{
  "user_traction": "analysis text",
  "scalability_readiness": "analysis text",
  "regulatory_needs": "analysis text",
  "real_world_adoption": "analysis text"
}}
"""

PRODUCT_GROWTH_STAGE_PROMPT = """
Analyze the product/service of this **Growth Stage/Series B** company:

{prompt_context}

Based on the data, comment on the following:
- **Reliability Under Load:** Is the product reliable under increased loads and users?
- **Automated Operations:** Are onboarding, operations, and customer support automated?
- **Compliance and Data Privacy:** Is the product ready for compliance and data privacy at scale?

Return as JSON:
{{
  "reliability_under_load": "analysis text",
  "automated_operations": "analysis text",
  "compliance_at_scale": "analysis text"
}}
"""

PRODUCT_LATER_STAGE_PROMPT = """
Analyze the product/service of this **Later Stage/Series C** company:

{prompt_context}

Based on the data, comment on the following:
- **Expansion and Innovation:** What is the strategy for expansion, innovation, and new products?
- **Adaptation for New Markets:** How is the product adapted for new jurisdictions, languages, and regulatory climates?
- **End-to-End Security & Compliance:** Is there end-to-end security and compliance?
- **Industry Reputation:** What is the industry reputation for innovation, reliability, and user trust?

Return as JSON:
{{
  "expansion_and_innovation": "analysis text",
  "market_adaptation": "analysis text",
  "security_and_compliance": "analysis text",
  "industry_reputation": "analysis text"
}}
"""

# Sector-based prompts for Product/Service
PRODUCT_FINTECH_PROMPT = """
Analyze the product/service of this **FinTech** company:

{prompt_context}

Based on the data, comment on the following:
- **Scalability of Business Model:** Is the business model scalable?
- **Regulatory Compliance:** Is the product compliant with financial regulations?
- **Cybersecurity:** Is the product secure from cyber threats?
- **Secure Transaction:** Are transactions secure?
- **Data Integration, Interoperability, and Automation:** How does the product handle data integration, interoperability, and automation?
- **Integration with Banks/APIs:** How is the product integrated with banks and APIs?

Return as JSON:
{{
  "business_model_scalability": "analysis text",
  "regulatory_compliance": "analysis text",
  "cybersecurity": "analysis text",
  "secure_transaction": "analysis text",
  "data_integration": "analysis text",
  "bank_integration": "analysis text"
}}
"""

PRODUCT_HEALTHTECH_PROMPT = """
Analyze the product/service of this **HealthTech** company:

{prompt_context}

Based on the data, comment on the following:
- **Involvement of Healthcare Experts and Clinical Validation:** Is there involvement of healthcare experts and clinical validation?
- **Regulatory Approval:** Does the product have regulatory approval (e.g., FDA, HIPAA, GDPR compliance)?
- **Feedback Loop with Patients/Clinicians:** Is there a feedback loop with patients and clinicians?
- **Technological Innovation:** What is the technological innovation (e.g., AI, data-driven diagnostics, telemedicine)?
- **Ease of Use and Accessibility:** Is the product easy to use and accessible for practitioners and patients?
- **Evidence Base for Efficacy:** Is there an evidence base for efficacy (e.g., clinical trials, endorsement from health systems)?

Return as JSON:
{{
  "expert_involvement": "analysis text",
  "regulatory_approval": "analysis text",
  "feedback_loop": "analysis text",
  "technological_innovation": "analysis text",
  "ease_of_use": "analysis text",
  "efficacy_evidence": "analysis text"
}}
"""
