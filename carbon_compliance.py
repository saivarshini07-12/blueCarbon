"""
Carbon Compliance Framework for SME Carbon Accounting
Determines fines or credits based on emission performance against benchmarks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json

class ComplianceStatus(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class IndustryBenchmark:
    """Industry-specific emission benchmarks per employee or revenue"""
    industry: str
    emissions_per_employee_kg: float  # kgCO2e per employee per year
    emissions_per_revenue_kg: float   # kgCO2e per million INR revenue
    reduction_target_percent: float   # Annual reduction target
    countries: List[str]              # Applicable countries

@dataclass
class ComplianceResult:
    """Result of compliance assessment"""
    status: ComplianceStatus
    score: float  # 0-100 scale
    fine_amount: float
    credit_amount: float
    emissions_actual: float
    emissions_benchmark: float
    performance_ratio: float
    recommendations: List[str]
    next_review_date: datetime
    period_description: str  # Description of the actual assessment period
    actual_period_months: float  # Actual period covered by the data

class CarbonComplianceFramework:
    """
    Carbon compliance framework for SMEs that determines fines or credits
    based on emission performance against industry benchmarks and targets
    """
    
    def __init__(self):
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.compliance_rules = self._load_compliance_rules()
        
    def _load_industry_benchmarks(self) -> Dict[str, IndustryBenchmark]:
        """Load industry-specific emission benchmarks"""
        benchmarks = {
            "manufacturing": IndustryBenchmark(
                industry="Manufacturing",
                emissions_per_employee_kg=8500,  # kgCO2e per employee/year
                emissions_per_revenue_kg=37500,  # kgCO2e per million INR
                reduction_target_percent=5.0,   # 5% annual reduction
                countries=["India", "Indonesia", "Japan", "Global"]
            ),
            "technology": IndustryBenchmark(
                industry="Technology",
                emissions_per_employee_kg=3200,
                emissions_per_revenue_kg=15000,
                reduction_target_percent=7.0,
                countries=["India", "Indonesia", "Japan", "Global"]
            ),
            "services": IndustryBenchmark(
                industry="Services",
                emissions_per_employee_kg=2800,
                emissions_per_revenue_kg=12500,
                reduction_target_percent=6.0,
                countries=["India", "Indonesia", "Japan", "Global"]
            ),
            "retail": IndustryBenchmark(
                industry="Retail",
                emissions_per_employee_kg=4200,
                emissions_per_revenue_kg=23350,
                reduction_target_percent=4.5,
                countries=["India", "Indonesia", "Japan", "Global"]
            ),
            "transportation": IndustryBenchmark(
                industry="Transportation",
                emissions_per_employee_kg=12000,
                emissions_per_revenue_kg=62500,
                reduction_target_percent=3.5,
                countries=["India", "Indonesia", "Japan", "Global"]
            ),
            "agriculture": IndustryBenchmark(
                industry="Agriculture",
                emissions_per_employee_kg=6800,
                emissions_per_revenue_kg=43350,
                reduction_target_percent=4.0,
                countries=["India", "Indonesia", "Japan", "Global"]
            ),
            "energy": IndustryBenchmark(
                industry="Energy",
                emissions_per_employee_kg=15000,
                emissions_per_revenue_kg=75000,
                reduction_target_percent=8.0,
                countries=["India", "Indonesia", "Japan", "Global"]
            )
        }
        return benchmarks
    
    def _load_compliance_rules(self) -> Dict:
        """Load compliance rules for fines and credits"""
        return {
            "excellent": {  # 20%+ better than benchmark
                "score_range": (90, 100),
                "credit_rate": 4200,  # INR per tonne CO2e saved
                "fine_rate": 0,
                "description": "Outstanding performance - eligible for carbon credits"
            },
            "good": {  # 10-20% better than benchmark
                "score_range": (75, 89),
                "credit_rate": 2100,  # INR per tonne CO2e saved
                "fine_rate": 0,
                "description": "Good performance - eligible for reduced carbon credits"
            },
            "needs_improvement": {  # Within 10% of benchmark
                "score_range": (60, 74),
                "credit_rate": 0,
                "fine_rate": 0,
                "description": "Meets minimum standards - no penalty or credit"
            },
            "poor": {  # 10-25% worse than benchmark
                "score_range": (40, 59),
                "credit_rate": 0,
                "fine_rate": 1260,  # INR per tonne CO2e over benchmark
                "description": "Below standards - subject to carbon tax"
            },
            "critical": {  # 25%+ worse than benchmark
                "score_range": (0, 39),
                "credit_rate": 0,
                "fine_rate": 2520,  # INR per tonne CO2e over benchmark
                "description": "Critical non-compliance - subject to high carbon tax"
            }
        }
    
    def assess_compliance(
        self,
        emissions_data: pd.DataFrame,
        company_info: Dict,
        assessment_period_months: int = 12
    ) -> ComplianceResult:
        """
        Assess carbon compliance and determine fines or credits
        
        Args:
            emissions_data: DataFrame with emission records
            company_info: Dict with company details (industry, employees, revenue, country)
            assessment_period_months: Period for assessment (default 12 months)
        
        Returns:
            ComplianceResult with assessment details
        """
        
        # Calculate total emissions for assessment period
        # Use the user-specified assessment period to understand the data context
        
        # Convert dates to datetime for validation
        emissions_data_copy = emissions_data.copy()
        emissions_data_copy['date'] = pd.to_datetime(emissions_data_copy['date'], errors='coerce')
        
        # Remove rows with invalid dates
        valid_emissions = emissions_data_copy.dropna(subset=['date'])
        
        # Use all available data and treat it as representing the specified assessment period
        total_emissions_kg = emissions_data['emissions_kgCO2e'].sum()
        
        if len(valid_emissions) > 0:
            # Calculate the actual date range for information
            min_date = valid_emissions['date'].min()
            max_date = valid_emissions['date'].max()
            actual_days = (max_date - min_date).days + 1
            
            period_description = f"Assessment Period: {assessment_period_months} months (Data from {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}, {actual_days} days)"
        else:
            period_description = f"Assessment Period: {assessment_period_months} months (no valid dates in data)"
        
        # Use the user-specified assessment period for benchmark calculations
        actual_period_months = assessment_period_months
        
        total_emissions_tonnes = total_emissions_kg / 1000
        
        # Get industry benchmark
        industry_key = company_info.get('industry', 'services').lower()
        if industry_key not in self.industry_benchmarks:
            industry_key = 'services'  # Default fallback
        
        benchmark = self.industry_benchmarks[industry_key]
        
        # Calculate benchmark emissions based on company size and user-specified assessment period
        if 'employees' in company_info and company_info['employees'] > 0:
            benchmark_emissions_kg = (
                benchmark.emissions_per_employee_kg * 
                company_info['employees'] * 
                (assessment_period_months / 12)
            )
        elif 'revenue_million_inr' in company_info and company_info['revenue_million_inr'] > 0:
            benchmark_emissions_kg = (
                benchmark.emissions_per_revenue_kg * 
                company_info['revenue_million_inr'] * 
                (assessment_period_months / 12)
            )
        else:
            # Default benchmark for small companies (10 employees equivalent)
            benchmark_emissions_kg = (
                benchmark.emissions_per_employee_kg * 10 * 
                (assessment_period_months / 12)
            )
        
        benchmark_emissions_tonnes = benchmark_emissions_kg / 1000
        
        # Calculate performance ratio (lower is better)
        performance_ratio = total_emissions_tonnes / benchmark_emissions_tonnes
        
        # Calculate compliance score (0-100)
        if performance_ratio <= 0.8:  # 20% better than benchmark
            score = 90 + (10 * (0.8 - performance_ratio) / 0.8)
            status = ComplianceStatus.EXCELLENT
        elif performance_ratio <= 0.9:  # 10-20% better
            score = 75 + (15 * (0.9 - performance_ratio) / 0.1)
            status = ComplianceStatus.GOOD
        elif performance_ratio <= 1.1:  # Within 10% of benchmark
            score = 60 + (15 * (1.1 - performance_ratio) / 0.2)
            status = ComplianceStatus.NEEDS_IMPROVEMENT
        elif performance_ratio <= 1.25:  # 10-25% worse
            score = 40 + (20 * (1.25 - performance_ratio) / 0.15)
            status = ComplianceStatus.POOR
        else:  # 25%+ worse
            score = max(0, 40 * (1.5 - performance_ratio) / 0.25)
            status = ComplianceStatus.CRITICAL
        
        score = max(0, min(100, score))  # Ensure score is between 0-100
        
        # Calculate fines and credits
        emissions_difference_tonnes = total_emissions_tonnes - benchmark_emissions_tonnes
        
        rules = self.compliance_rules[status.value]
        
        if emissions_difference_tonnes < 0:  # Better than benchmark
            credit_amount = abs(emissions_difference_tonnes) * rules['credit_rate']
            fine_amount = 0
        else:  # Worse than benchmark
            credit_amount = 0
            fine_amount = emissions_difference_tonnes * rules['fine_rate']
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            status, performance_ratio, emissions_data, company_info
        )
        
        # Set next review date based on assessment period and data
        if len(emissions_data) > 0:
            # Convert date column to datetime
            emissions_data_copy = emissions_data.copy()
            emissions_data_copy['date'] = pd.to_datetime(emissions_data_copy['date'], errors='coerce')
            valid_dates = emissions_data_copy['date'].dropna()
            
            if len(valid_dates) > 0:
                # Calculate next review based on latest data date + assessment period
                latest_data_date = valid_dates.max()
                next_review_date = latest_data_date + timedelta(days=int(assessment_period_months * 30.44))  # Average month length
            else:
                # Fallback to current date + assessment period
                next_review_date = datetime.now() + timedelta(days=int(assessment_period_months * 30.44))
        else:
            # Fallback to current date + assessment period
            next_review_date = datetime.now() + timedelta(days=int(assessment_period_months * 30.44))
        
        return ComplianceResult(
            status=status,
            score=score,
            fine_amount=fine_amount,
            credit_amount=credit_amount,
            emissions_actual=total_emissions_tonnes,
            emissions_benchmark=benchmark_emissions_tonnes,
            performance_ratio=performance_ratio,
            recommendations=recommendations,
            next_review_date=next_review_date,
            period_description=period_description,
            actual_period_months=assessment_period_months
        )
    
    def _generate_recommendations(
        self,
        status: ComplianceStatus,
        performance_ratio: float,
        emissions_data: pd.DataFrame,
        company_info: Dict
    ) -> List[str]:
        """Generate personalized recommendations based on performance"""
        
        recommendations = []
        
        # Analyze emission sources
        if len(emissions_data) > 0:
            scope_emissions = emissions_data.groupby('scope')['emissions_kgCO2e'].sum()
            category_emissions = emissions_data.groupby('category')['emissions_kgCO2e'].sum().sort_values(ascending=False)
            
            top_categories = category_emissions.head(3).index.tolist()
            
            # General recommendations based on status
            if status in [ComplianceStatus.EXCELLENT, ComplianceStatus.GOOD]:
                recommendations.extend([
                    "🌟 Excellent performance! Consider sharing best practices with industry peers",
                    "💡 Explore additional renewable energy opportunities to maintain leadership",
                    "📊 Document your carbon reduction strategies for sustainability reporting"
                ])
            elif status == ComplianceStatus.NEEDS_IMPROVEMENT:
                recommendations.extend([
                    "⚡ Focus on energy efficiency improvements to reduce Scope 2 emissions",
                    "🚗 Implement employee commuting programs to reduce Scope 3 emissions",
                    "📈 Set more aggressive reduction targets for next assessment period"
                ])
            else:  # Poor or Critical
                recommendations.extend([
                    "🚨 Immediate action required to avoid higher penalties",
                    "⚡ Prioritize energy audit and efficiency upgrades",
                    "🌱 Consider renewable energy procurement to reduce emissions",
                    "👥 Engage employees in carbon reduction initiatives"
                ])
            
            # Specific recommendations based on top emission sources
            for category in top_categories:
                if category == "Electricity":
                    recommendations.append("💡 Switch to renewable electricity or improve energy efficiency")
                elif category == "Mobile Combustion":
                    recommendations.append("🚗 Consider electric vehicles or optimize fleet usage")
                elif category == "Business Travel":
                    recommendations.append("✈️ Implement virtual meeting policies and sustainable travel guidelines")
                elif category == "Stationary Combustion":
                    recommendations.append("🔥 Upgrade to more efficient heating systems or alternative fuels")
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    def generate_compliance_report(self, result: ComplianceResult, company_info: Dict) -> str:
        """Generate a formatted compliance report"""
        
        report = f"""
# Carbon Compliance Assessment Report

## Company Information
- **Company**: {company_info.get('name', 'N/A')}
- **Industry**: {company_info.get('industry', 'N/A')}
- **Assessment Date**: {datetime.now().strftime('%Y-%m-%d')}

## Compliance Results
- **Status**: {result.status.value.replace('_', ' ').title()}
- **Performance Ratio**: {result.performance_ratio:.2f} (vs industry benchmark)

## Emissions Summary
- **Actual Emissions**: {result.emissions_actual:.2f} tonnes CO2e
- **Benchmark Emissions**: {result.emissions_benchmark:.2f} tonnes CO2e
- **Difference**: {result.emissions_actual - result.emissions_benchmark:+.2f} tonnes CO2e

## Financial Impact
"""
        
        if result.credit_amount > 0:
            report += f"- **Carbon Credits Earned**: ₹{result.credit_amount:,.2f}\n"
            report += f"- **Status**: Eligible for carbon offset revenue\n"
        elif result.fine_amount > 0:
            report += f"- **Carbon Tax Due**: ₹{result.fine_amount:,.2f}\n"
            report += f"- **Status**: Subject to carbon penalty\n"
        else:
            report += f"- **Financial Impact**: No penalty or credit\n"
            report += f"- **Status**: Meets minimum compliance standards\n"
        
        report += f"\n## Recommendations\n"
        for i, rec in enumerate(result.recommendations, 1):
            report += f"{i}. {rec}\n"
        
        return report
    
    def get_industry_benchmark_info(self, industry: str) -> Optional[IndustryBenchmark]:
        """Get benchmark information for a specific industry"""
        industry_key = industry.lower()
        return self.industry_benchmarks.get(industry_key)
    
    def simulate_improvement_scenarios(
        self,
        current_result: ComplianceResult,
        reduction_percentages: List[float]
    ) -> List[Dict]:
        """Simulate different emission reduction scenarios"""
        
        scenarios = []
        for reduction_pct in reduction_percentages:
            new_emissions = current_result.emissions_actual * (1 - reduction_pct / 100)
            new_ratio = new_emissions / current_result.emissions_benchmark
            
            # Calculate new status and financial impact
            if new_ratio <= 0.8:
                new_status = ComplianceStatus.EXCELLENT
                new_credit = abs(new_emissions - current_result.emissions_benchmark) * 4200
                new_fine = 0
            elif new_ratio <= 0.9:
                new_status = ComplianceStatus.GOOD
                new_credit = abs(new_emissions - current_result.emissions_benchmark) * 2100
                new_fine = 0
            elif new_ratio <= 1.1:
                new_status = ComplianceStatus.NEEDS_IMPROVEMENT
                new_credit = 0
                new_fine = 0
            elif new_ratio <= 1.25:
                new_status = ComplianceStatus.POOR
                new_credit = 0
                new_fine = (new_emissions - current_result.emissions_benchmark) * 1260
            else:
                new_status = ComplianceStatus.CRITICAL
                new_credit = 0
                new_fine = (new_emissions - current_result.emissions_benchmark) * 2520
            
            scenarios.append({
                'reduction_percentage': reduction_pct,
                'new_emissions_tonnes': new_emissions,
                'new_status': new_status.value,
                'new_credit_amount': new_credit,
                'new_fine_amount': new_fine,
                'financial_improvement': (current_result.fine_amount - new_fine) + (new_credit - current_result.credit_amount)
            })
        
        return scenarios

# Example usage
if __name__ == "__main__":
    # Example company information
    company_info = {
        'name': 'Green Tech Solutions',
        'industry': 'technology',
        'employees': 50,
        'revenue_million_inr': 400.0,
        'country': 'India'
    }
    
    # Example emissions data (would come from your existing data)
    sample_data = pd.DataFrame([
        {'date': '2025-01-01', 'scope': 'Scope 2', 'category': 'Electricity', 'emissions_kgCO2e': 5000},
        {'date': '2025-02-01', 'scope': 'Scope 1', 'category': 'Mobile Combustion', 'emissions_kgCO2e': 2000},
        {'date': '2025-03-01', 'scope': 'Scope 3', 'category': 'Business Travel', 'emissions_kgCO2e': 1500}
    ])
    
    # Run compliance assessment
    framework = CarbonComplianceFramework()
    result = framework.assess_compliance(sample_data, company_info)
    
    print(framework.generate_compliance_report(result, company_info))
