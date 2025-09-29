"""
Company Management System for Carbon Accounting and Blockchain Integration
Handles company registration, authentication, and data management
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

class CompanyManager:
    """Manages company registration, authentication, and data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.companies_file = os.path.join(data_dir, "companies.json")
        self.ensure_data_dir()
        self.companies = self.load_companies()
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_companies(self) -> Dict:
        """Load companies from file"""
        try:
            if os.path.exists(self.companies_file):
                with open(self.companies_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading companies: {e}")
        return {}
    
    def save_companies(self):
        """Save companies to file"""
        try:
            with open(self.companies_file, 'w') as f:
                json.dump(self.companies, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving companies: {e}")
    
    def generate_company_id(self, company_name: str, email: str) -> str:
        """Generate unique company ID"""
        data = f"{company_name}_{email}_{datetime.now().timestamp()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def register_company(self, 
                        company_name: str,
                        email: str,
                        industry: str,
                        location: str,
                        size: str,
                        contact_person: str,
                        phone: str = "",
                        website: str = "") -> str:
        """Register a new company"""
        
        # Check if company already exists
        for comp_id, comp_data in self.companies.items():
            if comp_data['email'].lower() == email.lower():
                raise ValueError(f"Company with email {email} already registered")
        
        # Generate company ID
        company_id = self.generate_company_id(company_name, email)
        
        # Create company record
        company_data = {
            'company_id': company_id,
            'company_name': company_name,
            'email': email,
            'industry': industry,
            'location': location,
            'size': size,
            'contact_person': contact_person,
            'phone': phone,
            'website': website,
            'registration_date': datetime.now().isoformat(),
            'initial_carbon_credits': 0.0,
            'total_emissions': 0.0,
            'is_active': True,
            'blockchain_address': f"0x{company_id}",
            'verification_status': 'pending'
        }
        
        # Save company
        self.companies[company_id] = company_data
        self.save_companies()
        
        # Create company-specific data files
        self.create_company_data_files(company_id)
        
        return company_id
    
    def create_company_data_files(self, company_id: str):
        """Create company-specific data files"""
        company_dir = os.path.join(self.data_dir, f"company_{company_id}")
        os.makedirs(company_dir, exist_ok=True)
        
        # Create emissions file
        emissions_file = os.path.join(company_dir, "emissions.json")
        if not os.path.exists(emissions_file):
            with open(emissions_file, 'w') as f:
                json.dump([], f)
        
        # Create credits file
        credits_file = os.path.join(company_dir, "carbon_credits.json")
        if not os.path.exists(credits_file):
            initial_credits = {
                'credits_earned': 0.0,
                'credits_purchased': 0.0,
                'credits_used': 0.0,
                'credits_available': 0.0,
                'transactions': []
            }
            with open(credits_file, 'w') as f:
                json.dump(initial_credits, f, indent=2)
    
    def authenticate_company(self, company_id: str) -> Optional[Dict]:
        """Authenticate company by ID"""
        return self.companies.get(company_id)
    
    def get_company_by_email(self, email: str) -> Optional[Dict]:
        """Get company by email"""
        for comp_data in self.companies.values():
            if comp_data['email'].lower() == email.lower():
                return comp_data
        return None
    
    def get_all_companies(self) -> Dict:
        """Get all registered companies"""
        return self.companies
    
    def update_company_emissions(self, company_id: str, emissions: float):
        """Update company's total emissions"""
        if company_id in self.companies:
            self.companies[company_id]['total_emissions'] += emissions
            self.save_companies()
    
    def award_carbon_credits(self, company_id: str, credits: float, reason: str = ""):
        """Award carbon credits to a company"""
        if company_id in self.companies:
            # Update company record
            if 'carbon_credits' not in self.companies[company_id]:
                self.companies[company_id]['carbon_credits'] = 0.0
            
            self.companies[company_id]['carbon_credits'] += credits
            self.save_companies()
            
            # Update credits file
            credits_file = os.path.join(self.data_dir, f"company_{company_id}", "carbon_credits.json")
            try:
                with open(credits_file, 'r') as f:
                    credits_data = json.load(f)
                
                credits_data['credits_earned'] += credits
                credits_data['credits_available'] += credits
                credits_data['transactions'].append({
                    'type': 'earned',
                    'amount': credits,
                    'reason': reason,
                    'date': datetime.now().isoformat()
                })
                
                with open(credits_file, 'w') as f:
                    json.dump(credits_data, f, indent=2)
            except Exception as e:
                print(f"Error updating credits file: {e}")
    
    def get_company_emissions_data(self, company_id: str) -> List[Dict]:
        """Get company's emissions data"""
        emissions_file = os.path.join(self.data_dir, f"company_{company_id}", "emissions.json")
        try:
            if os.path.exists(emissions_file):
                with open(emissions_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading emissions data: {e}")
        return []
    
    def save_company_emissions_data(self, company_id: str, emissions_data: List[Dict]):
        """Save company's emissions data"""
        emissions_file = os.path.join(self.data_dir, f"company_{company_id}", "emissions.json")
        try:
            with open(emissions_file, 'w') as f:
                json.dump(emissions_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving emissions data: {e}")
    
    def get_company_carbon_summary(self, company_id: str) -> Dict:
        """Get comprehensive carbon summary for a company"""
        if company_id not in self.companies:
            return {}
        
        company = self.companies[company_id]
        
        # Get credits data
        credits_file = os.path.join(self.data_dir, f"company_{company_id}", "carbon_credits.json")
        credits_data = {'credits_available': 0.0, 'credits_earned': 0.0, 'credits_purchased': 0.0, 'credits_used': 0.0}
        
        try:
            if os.path.exists(credits_file):
                with open(credits_file, 'r') as f:
                    credits_data = json.load(f)
        except Exception as e:
            print(f"Error loading credits data: {e}")
        
        # Get emissions data
        emissions_data = self.get_company_emissions_data(company_id)
        total_emissions = sum(item.get('emissions_kgCO2e', 0) for item in emissions_data)
        
        # Calculate remaining credits
        remaining_credits = credits_data['credits_available'] - (total_emissions / 1000)  # Convert kg to tonnes
        
        return {
            'company_name': company['company_name'],
            'company_id': company_id,
            'total_carbon_credits': credits_data['credits_available'],
            'credits_earned': credits_data['credits_earned'],
            'credits_purchased': credits_data['credits_purchased'],
            'credits_used': credits_data['credits_used'],
            'total_emissions_kg': total_emissions,
            'total_emissions_tonnes': total_emissions / 1000,
            'remaining_credits': max(0, remaining_credits),
            'carbon_status': 'Carbon Positive' if remaining_credits > 0 else 'Carbon Negative',
            'emissions_count': len(emissions_data),
            'last_updated': datetime.now().isoformat()
        }

# Global instance
company_manager = CompanyManager()