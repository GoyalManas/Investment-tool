# financial_analyzer.py
# Add this as a new module

import re
from typing import Dict, Any, Optional, Tuple

class FinancialAnalyzer:
    """Calculates critical financial metrics and flags problems."""
    
    @staticmethod
    def parse_currency(value: str) -> Optional[float]:
        """Parse currency strings like '$100M', '€50.5M', etc."""
        if not value or value.lower() == 'n/a':
            return None
        
        # Remove currency symbols and spaces
        value = re.sub(r'[€$£,\s]', '', value.lower())
        
        multipliers = {
            'b': 1_000_000_000,
            'billion': 1_000_000_000,
            'm': 1_000_000,
            'million': 1_000_000,
            'k': 1_000,
        }
        
        for suffix, multiplier in multipliers.items():
            if suffix in value:
                try:
                    num = float(value.replace(suffix, ''))
                    return num * multiplier
                except:
                    continue
        
        try:
            return float(value)
        except:
            return None
    
    @staticmethod
    def calculate_burn_multiple(net_burn: float, net_new_arr: float) -> Tuple[float, str]:
        """
        Burn Multiple = Net Burn / Net New ARR
        < 1.5x = Excellent
        1.5-3x = Good
        3-5x = Concerning
        > 5x = Red flag
        """
        if net_new_arr <= 0:
            return None, "Cannot calculate (no ARR growth)"
        
        burn_multiple = net_burn / net_new_arr
        
        if burn_multiple < 1.5:
            rating = "EXCELLENT - Very capital efficient"
        elif burn_multiple < 3:
            rating = "GOOD - Acceptable efficiency"
        elif burn_multiple < 5:
            rating = "CONCERNING - High burn relative to growth"
        else:
            rating = "RED FLAG - Burning cash too fast"
        
        return burn_multiple, rating
    
    @staticmethod
    def calculate_runway(cash_on_hand: float, monthly_burn: float) -> Tuple[int, str]:
        """Calculate months of runway."""
        if monthly_burn <= 0:
            return None, "N/A"
        
        months = cash_on_hand / monthly_burn
        
        if months > 24:
            health = "HEALTHY"
        elif months > 12:
            health = "ADEQUATE"
        elif months > 6:
            health = "CONCERNING - needs funding soon"
        else:
            health = "CRITICAL - immediate funding required"
        
        return int(months), health
    
    @staticmethod
    def analyze_unit_economics(cac: float, ltv: float, payback_months: float) -> Dict[str, Any]:
        """
        Analyze customer economics.
        LTV:CAC should be > 3x
        Payback should be < 12 months
        """
        analysis = {
            "ltv_cac_ratio": None,
            "ltv_cac_rating": "Unknown",
            "payback_rating": "Unknown",
            "problems": []
        }
        
        if cac and ltv:
            ratio = ltv / cac
            analysis["ltv_cac_ratio"] = round(ratio, 2)
            
            if ratio < 1:
                analysis["ltv_cac_rating"] = "CRITICAL - Losing money on customers"
                analysis["problems"].append("LTV < CAC means fundamentally broken economics")
            elif ratio < 3:
                analysis["ltv_cac_rating"] = "POOR - Marginal economics"
                analysis["problems"].append("LTV:CAC below 3x target")
            elif ratio < 5:
                analysis["ltv_cac_rating"] = "GOOD - Healthy economics"
            else:
                analysis["ltv_cac_rating"] = "EXCELLENT - Strong economics"
        
        if payback_months:
            if payback_months > 24:
                analysis["payback_rating"] = "POOR - Too long to recover CAC"
                analysis["problems"].append(f"{payback_months} month payback is concerning")
            elif payback_months > 12:
                analysis["payback_rating"] = "ACCEPTABLE - Could be better"
            else:
                analysis["payback_rating"] = "GOOD - Quick payback"
        
        return analysis
    
    @staticmethod
    def calculate_capital_efficiency(total_funding: float, arr: float) -> Tuple[float, str]:
        """
        Capital Efficiency = Total Funding / ARR
        < 2x = Excellent
        2-5x = Good  
        5-10x = Concerning
        > 10x = Red flag
        """
        if not arr or arr <= 0:
            return None, "Cannot calculate (no revenue)"
        
        ratio = total_funding / arr
        
        if ratio < 2:
            rating = "EXCELLENT - Very efficient"
        elif ratio < 5:
            rating = "GOOD - Reasonable efficiency"
        elif ratio < 10:
            rating = "CONCERNING - High funding vs revenue"
        else:
            rating = "RED FLAG - Poor capital efficiency"
        
        return round(ratio, 2), rating
    
    @staticmethod
    def analyze_growth_rate(current_arr: float, prior_arr: float, months: int = 12) -> Dict[str, Any]:
        """Analyze revenue growth."""
        if not prior_arr or prior_arr <= 0:
            return {"growth_rate": None, "rating": "Unknown"}
        
        growth_rate = ((current_arr - prior_arr) / prior_arr) * 100
        
        # Annualized if not yearly
        if months != 12:
            growth_rate = growth_rate * (12 / months)
        
        if growth_rate < 0:
            rating = "CRITICAL - Negative growth"
        elif growth_rate < 20:
            rating = "POOR - Below industry standard"
        elif growth_rate < 50:
            rating = "ACCEPTABLE - Steady growth"
        elif growth_rate < 100:
            rating = "GOOD - Strong growth"
        else:
            rating = "EXCELLENT - Hypergrowth"
        
        return {
            "growth_rate": round(growth_rate, 1),
            "rating": rating
        }
    
    @staticmethod
    def comprehensive_analysis(company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all financial analyses."""
        
        # Extract values
        arr = FinancialAnalyzer.parse_currency(company_data.get('revenue', ''))
        total_funding = FinancialAnalyzer.parse_currency(company_data.get('total_funding', ''))
        
        analysis = {
            "metrics": {},
            "red_flags": [],
            "positive_signals": [],
            "overall_score": 0  # 0-100
        }
        
        # Capital Efficiency
        if arr and total_funding:
            ratio, rating = FinancialAnalyzer.calculate_capital_efficiency(total_funding, arr)
            analysis["metrics"]["capital_efficiency"] = {
                "ratio": ratio,
                "rating": rating
            }
            
            if ratio > 10:
                analysis["red_flags"].append(
                    f"Capital efficiency {ratio}x is very poor - raised ${total_funding/1e6:.1f}M for ${arr/1e6:.1f}M ARR"
                )
            elif ratio < 2:
                analysis["positive_signals"].append(
                    f"Excellent capital efficiency {ratio}x"
                )
        
        # More analyses...
        # (Add burn multiple, runway, unit economics, etc.)
        
        # Calculate overall score
        score = 50  # Start neutral
        
        if analysis["metrics"].get("capital_efficiency"):
            ratio = analysis["metrics"]["capital_efficiency"]["ratio"]
            if ratio < 2:
                score += 20
            elif ratio > 10:
                score -= 30
        
        # Add more scoring logic...
        
        analysis["overall_score"] = max(0, min(100, score))
        
        return analysis


# Usage example
def enrich_company_data_with_analysis(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add financial analysis to company data."""
    analyzer = FinancialAnalyzer()
    
    financial_analysis = analyzer.comprehensive_analysis(company_data)
    company_data['financial_analysis'] = financial_analysis
    
    return company_data

