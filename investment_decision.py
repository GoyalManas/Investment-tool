# investment_decision.py

from typing import Dict, List, Any
from enum import Enum

class InvestmentDecision(Enum):
    STRONG_PASS = "STRONG_PASS"
    PASS = "PASS"
    MAYBE = "MAYBE"
    INVEST = "INVEST"
    STRONG_INVEST = "STRONG_INVEST"

class InvestmentScorer:
    """
    Scores investment opportunities based on hard metrics,
    not feelings or marketing fluff.
    """
    
    def __init__(self):
        self.score = 0
        self.max_score = 100
        self.reasons_to_invest = []
        self.reasons_to_pass = []
        self.critical_questions = []
        
    def score_market_opportunity(self, company_data: Dict) -> int:
        """Score: 0-25 points"""
        score = 0
        
        # Market size (0-10 points)
        market_size = company_data.get('calculated', {}).get('market_size_numeric', 0)
        if market_size > 50_000_000_000:  # $50B+
            score += 10
            self.reasons_to_invest.append("Very large addressable market")
        elif market_size > 10_000_000_000:  # $10B+
            score += 7
        elif market_size > 1_000_000_000:  # $1B+
            score += 4
        else:
            score += 0
            self.reasons_to_pass.append("Market may be too small")
            
        # Market growth (0-10 points)
        growth_rate = company_data.get('calculated', {}).get('market_growth_rate', 0)
        if growth_rate > 20:
            score += 10
            self.reasons_to_invest.append(f"Fast-growing market ({growth_rate}% CAGR)")
        elif growth_rate > 10:
            score += 6
        elif growth_rate < 5:
            score += 0
            self.reasons_to_pass.append("Slow-growing market")
            
        # Competitive position (0-5 points)
        competitors = len(company_data.get('competitors', []))
        if competitors < 3:
            score += 5
            self.reasons_to_invest.append("Limited direct competition")
        elif competitors > 10:
            score += 0
            self.critical_questions.append("How will they differentiate in crowded market?")
            
        return score
    
    def score_team(self, company_data: Dict) -> int:
        """Score: 0-20 points"""
        score = 10  # Start with baseline
        
        founders = company_data.get('founders_analysis', {})
        
        # Prior startup experience (0-5 points)
        experience = founders.get('prior_startup_experience', '').lower()
        if 'exit' in experience or 'acquired' in experience:
            score += 5
            self.reasons_to_invest.append("Founders have successful exits")
        elif 'failed' in experience or 'shut down' in experience:
            score += 2  # Failure can be educational
            self.critical_questions.append("What did founders learn from previous failure?")
        elif 'none' in experience or not experience:
            score += 0
            self.critical_questions.append("First-time founders - execution risk")
            
        # Domain expertise (0-5 points)
        key_competency = founders.get('key_competency', '')
        if key_competency and len(key_competency) > 100:  # Substantial domain knowledge
            score += 5
        else:
            score += 2
            
        # Team size appropriate for stage (0-5 points)
        employees = company_data.get('metrics', {}).get('employees', 0)
        funding = company_data.get('calculated', {}).get('total_funding_numeric', 0)
        
        if funding > 50_000_000 and employees < 50:
            score += 5
            self.reasons_to_invest.append("Lean team despite significant funding")
        elif funding > 50_000_000 and employees > 200:
            score += 0
            self.reasons_to_pass.append("Large team may indicate inefficiency")
            
        # Red flags (-10 points)
        red_flags = founders.get('red_flags', '').lower()
        if red_flags and 'none' not in red_flags:
            score -= 10
            self.reasons_to_pass.append(f"Founder red flags: {red_flags}")
            
        # Culture (0-5 points)
        glassdoor = company_data.get('glassdoor_rating', 0)
        try:
            glassdoor_float = float(glassdoor) if glassdoor else 0
            if glassdoor_float >= 4.0:
                score += 5
                self.reasons_to_invest.append(f"Strong culture (Glassdoor: {glassdoor_float})")
            elif glassdoor_float < 3.0:
                score -= 5
                self.reasons_to_pass.append(f"Poor culture (Glassdoor: {glassdoor_float})")
        except:
            pass
            
        return min(score, 20)
    
    def score_traction(self, company_data: Dict) -> int:
        """Score: 0-30 points - MOST IMPORTANT SECTION"""
        score = 0
        
        # Revenue growth (0-15 points)
        growth_rate = company_data.get('calculated', {}).get('revenue_growth_rate', 0)
        arr = company_data.get('calculated', {}).get('arr_numeric', 0)
        
        if arr > 10_000_000 and growth_rate > 100:
            score += 15
            self.reasons_to_invest.append(f"Hypergrowth at scale: ${arr/1e6:.1f}M ARR, {growth_rate}% growth")
        elif arr > 5_000_000 and growth_rate > 50:
            score += 12
            self.reasons_to_invest.append(f"Strong traction: ${arr/1e6:.1f}M ARR growing {growth_rate}%")
        elif arr > 1_000_000:
            score += 8
        elif arr > 0:
            score += 4
        else:
            score += 0
            self.reasons_to_pass.append("No revenue disclosed - very risky")
            self.critical_questions.append("Why no revenue? When will revenue start?")
        
        # Customer validation (0-10 points)
        customers = company_data.get('calculated', {}).get('customer_count', 0)
        top_customers = company_data.get('top_customers', [])
        
        # Check for enterprise logos
        enterprise_names = ['google', 'microsoft', 'amazon', 'apple', 'meta', 'salesforce', 
                           'oracle', 'ibm', 'netflix', 'uber', 'airbnb']
        has_enterprise = any(any(name in str(customer).lower() for name in enterprise_names) 
                           for customer in top_customers)
        
        if has_enterprise:
            score += 10
            self.reasons_to_invest.append("Blue-chip enterprise customers provide validation")
        elif customers > 100:
            score += 7
        elif customers > 10:
            score += 4
        else:
            self.critical_questions.append("How many paying customers? What's customer quality?")
        
        # Product-market fit signals (0-5 points)
        ndr = company_data.get('calculated', {}).get('net_dollar_retention', 0)
        if ndr > 120:
            score += 5
            self.reasons_to_invest.append(f"Strong expansion: {ndr}% NDR")
        elif ndr > 100:
            score += 3
        elif ndr > 0 and ndr < 90:
            score -= 5
            self.reasons_to_pass.append(f"Poor retention: {ndr}% NDR")
            
        return score
    
    def score_financial_health(self, company_data: Dict) -> int:
        """Score: 0-25 points"""
        score = 0
        
        # Capital efficiency (0-10 points)
        cap_efficiency = company_data.get('calculated', {}).get('capital_efficiency_ratio', None)
        if cap_efficiency:
            if cap_efficiency < 2:
                score += 10
                self.reasons_to_invest.append(f"Excellent capital efficiency: {cap_efficiency}x")
            elif cap_efficiency < 5:
                score += 6
            elif cap_efficiency < 10:
                score += 2
                self.critical_questions.append(f"Why raised {cap_efficiency}x more than revenue?")
            else:
                score -= 10
                self.reasons_to_pass.append(f"TERRIBLE capital efficiency: {cap_efficiency}x funding-to-revenue")
                self.critical_questions.append("Is this fundamentally broken or just very early?")
        
        # Unit economics (0-10 points)
        ltv_cac = company_data.get('calculated', {}).get('ltv_cac_ratio', None)
        if ltv_cac:
            if ltv_cac > 5:
                score += 10
                self.reasons_to_invest.append(f"Excellent unit economics: {ltv_cac}x LTV:CAC")
            elif ltv_cac > 3:
                score += 7
            elif ltv_cac > 1:
                score += 3
            else:
                score -= 10
                self.reasons_to_pass.append(f"Broken economics: {ltv_cac}x LTV:CAC")
        else:
            self.critical_questions.append("What are the unit economics (CAC, LTV, payback)?")
        
        # Runway (0-5 points)
        runway = company_data.get('calculated', {}).get('runway_months', None)
        if runway:
            if runway > 18:
                score += 5
            elif runway > 12:
                score += 3
            elif runway < 6:
                score -= 5
                self.reasons_to_pass.append(f"Only {runway} months runway - desperate for capital")
        else:
            self.critical_questions.append("What's the burn rate and runway?")
            
        return score
    
    def calculate_decision(self, company_data: Dict) -> Dict[str, Any]:
        """Generate final investment decision."""
        
        # Calculate scores
        market_score = self.score_market_opportunity(company_data)
        team_score = self.score_team(company_data)
        traction_score = self.score_traction(company_data)
        financial_score = self.score_financial_health(company_data)
        
        total_score = market_score + team_score + traction_score + financial_score
        
        # Determine decision
        if total_score >= 80:
            decision = InvestmentDecision.STRONG_INVEST
            recommendation = "STRONG INVEST - Exceptional opportunity across all dimensions"
        elif total_score >= 65:
            decision = InvestmentDecision.INVEST
            recommendation = "INVEST - Strong fundamentals with manageable risks"
        elif total_score >= 50:
            decision = InvestmentDecision.MAYBE
            recommendation = "MAYBE - Promising but needs deeper diligence on key questions"
        elif total_score >= 35:
            decision = InvestmentDecision.PASS
            recommendation = "PASS - Too many concerns relative to upside"
        else:
            decision = InvestmentDecision.STRONG_PASS
            recommendation = "STRONG PASS - Fundamental issues that disqualify investment"
        
        return {
            "decision": decision.value,
            "recommendation": recommendation,
            "total_score": total_score,
            "breakdown": {
                "market": market_score,
                "team": team_score,
                "traction": traction_score,
                "financial_health": financial_score
            },
            "reasons_to_invest": self.reasons_to_invest,
            "reasons_to_pass": self.reasons_to_pass,
            "critical_questions": self.critical_questions,
            "next_steps": self._generate_next_steps(decision, total_score)
        }
    
    def _generate_next_steps(self, decision: InvestmentDecision, score: int) -> List[str]:
        """Generate actionable next steps based on decision."""
        
        if decision == InvestmentDecision.STRONG_INVEST:
            return [
                "Schedule meeting with founders ASAP",
                "Request detailed financial model",
                "Conduct customer reference calls (at least 3)",
                "Perform technical diligence",
                "Review cap table and prior round terms",
                "Prepare term sheet"
            ]
        elif decision == InvestmentDecision.INVEST:
            return [
                "Deep dive on critical questions listed above",
                "Customer reference calls",
                "Competitive analysis deep dive",
                "Financial model review",
                "Second partner review meeting"
            ]
        elif decision == InvestmentDecision.MAYBE:
            return [
                "Get answers to all critical questions",
                "Request more detailed metrics",
                "Understand path to next milestone",
                "Assess if concerns are addressable",
                "Consider smaller check or wait for next round"
            ]
        else:  # PASS or STRONG_PASS
            return [
                "Politely decline",
                "Provide constructive feedback if appropriate",
                "Stay in touch if there's founder potential",
                "Revisit in 6-12 months if fundamentals improve"
            ]


# Usage in your app
def generate_investment_recommendation(company_data: Dict) -> Dict[str, Any]:
    """
    Replace your existing investment thesis generation with this.
    This uses HARD METRICS instead of LLM vibes.
    """
    scorer = InvestmentScorer()
    decision = scorer.calculate_decision(company_data)
    
    # Add qualitative context if you want LLM enhancement
    # But the decision should be driven by metrics
    
    return decision