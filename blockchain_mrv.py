"""
Blockchain integration module for Blue Carbon Registry and MRV System
Integrates with existing Carbon Accounting application for SIH 2025
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib
import requests
from dataclasses import dataclass, asdict

try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    print("Web3 not available. Install with: pip install web3 eth-account")

@dataclass
class BlueCarbonProject:
    """Blue Carbon Project data structure"""
    id: int
    name: str
    location: str
    area: float  # hectares
    ecosystem_type: str  # mangrove, seagrass, salt_marsh
    owner: str
    estimated_carbon_sequestration: float  # tons CO2/year
    created_at: datetime
    status: str
    ipfs_hash: str

@dataclass
class VerificationRecord:
    """Verification record for MRV system"""
    id: int
    project_id: int
    verifier: str
    verified_carbon_amount: float  # tons CO2
    verification_date: datetime
    verification_data_hash: str
    is_approved: bool
    comments: str

@dataclass
class CarbonCredit:
    """Carbon credit token"""
    project_id: int
    amount: float  # tons CO2
    price_per_ton: float  # USD
    seller: str
    is_active: bool
    created_at: datetime

class BlockchainMRVSystem:
    """Blockchain-based Monitoring, Reporting, and Verification System"""
    
    def __init__(self, config_file: str = "blockchain_config.json"):
        self.config = self._load_config(config_file)
        self.web3 = None
        self.contract = None
        self.account = None
        
        # In-memory storage for demo (replace with actual blockchain in production)
        self.projects: Dict[int, BlueCarbonProject] = {}
        self.verifications: Dict[int, VerificationRecord] = {}
        self.carbon_credits: Dict[str, List[CarbonCredit]] = {}  # company_address -> credits
        self.company_emissions: Dict[str, float] = {}
        self.next_project_id = 1
        self.next_verification_id = 1
        
        if WEB3_AVAILABLE and self.config.get('blockchain_enabled', False):
            self._initialize_blockchain()
    
    def _load_config(self, config_file: str) -> Dict:
        """Load blockchain configuration"""
        default_config = {
            "blockchain_enabled": False,
            "network": "ganache",  # or "sepolia", "mainnet"
            "rpc_url": "http://127.0.0.1:8545",
            "contract_address": "",
            "private_key": "",
            "ipfs_gateway": "https://ipfs.io/ipfs/",
            "verification_threshold": 2  # Number of verifiers required
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
        
        return default_config
    
    def _initialize_blockchain(self):
        """Initialize blockchain connection"""
        try:
            self.web3 = Web3(Web3.HTTPProvider(self.config['rpc_url']))
            if self.web3.is_connected():
                print("✅ Connected to blockchain network")
                
                # Initialize account
                if self.config.get('private_key'):
                    self.account = Account.from_key(self.config['private_key'])
                    print(f"Account address: {self.account.address}")
            else:
                print("❌ Failed to connect to blockchain")
        except Exception as e:
            print(f"Blockchain initialization error: {e}")
    
    def register_blue_carbon_project(self, 
                                   name: str,
                                   location: str,
                                   area: float,
                                   ecosystem_type: str,
                                   estimated_sequestration: float,
                                   owner: str,
                                   project_data: Dict) -> int:
        """Register a new blue carbon project"""
        
        # Create IPFS hash for project data
        ipfs_hash = self._store_to_ipfs(project_data)
        
        project = BlueCarbonProject(
            id=self.next_project_id,
            name=name,
            location=location,
            area=area,
            ecosystem_type=ecosystem_type,
            owner=owner,
            estimated_carbon_sequestration=estimated_sequestration,
            created_at=datetime.now(),
            status="PROPOSED",
            ipfs_hash=ipfs_hash
        )
        
        self.projects[self.next_project_id] = project
        project_id = self.next_project_id
        self.next_project_id += 1
        
        print(f"✅ Blue carbon project registered: {name} (ID: {project_id})")
        return project_id
    
    def submit_verification(self,
                          project_id: int,
                          verified_amount: float,
                          verifier: str,
                          verification_data: Dict,
                          comments: str = "") -> int:
        """Submit verification record for a project"""
        
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} does not exist")
        
        # Create hash for verification data
        data_hash = self._create_data_hash(verification_data)
        
        verification = VerificationRecord(
            id=self.next_verification_id,
            project_id=project_id,
            verifier=verifier,
            verified_carbon_amount=verified_amount,
            verification_date=datetime.now(),
            verification_data_hash=data_hash,
            is_approved=False,
            comments=comments
        )
        
        self.verifications[self.next_verification_id] = verification
        verification_id = self.next_verification_id
        self.next_verification_id += 1
        
        print(f"✅ Verification submitted for project {project_id} by {verifier}")
        return verification_id
    
    def approve_verification_and_issue_credits(self, verification_id: int) -> bool:
        """Approve verification and issue carbon credits"""
        
        if verification_id not in self.verifications:
            raise ValueError(f"Verification {verification_id} does not exist")
        
        verification = self.verifications[verification_id]
        if verification.is_approved:
            raise ValueError("Verification already approved")
        
        # Approve verification
        verification.is_approved = True
        
        # Issue carbon credits to project owner
        project = self.projects[verification.project_id]
        if project.owner not in self.carbon_credits:
            self.carbon_credits[project.owner] = []
        
        credit = CarbonCredit(
            project_id=verification.project_id,
            amount=verification.verified_carbon_amount,
            price_per_ton=50.0,  # Default price, can be updated
            seller=project.owner,
            is_active=True,
            created_at=datetime.now()
        )
        
        self.carbon_credits[project.owner].append(credit)
        
        print(f"✅ Verification approved and {verification.verified_carbon_amount} carbon credits issued to {project.owner}")
        return True
    
    def record_company_emissions(self, company_address: str, emissions: float):
        """Record company emissions for carbon accounting"""
        if company_address not in self.company_emissions:
            self.company_emissions[company_address] = 0
        
        self.company_emissions[company_address] += emissions
        print(f"📊 Recorded {emissions} tons CO2 emissions for {company_address}")
    
    def get_company_carbon_balance(self, company_address: str) -> float:
        """Get company's total carbon credits"""
        if company_address not in self.carbon_credits:
            return 0.0
        
        return sum(credit.amount for credit in self.carbon_credits[company_address] if credit.is_active)
    
    def get_company_emissions(self, company_address: str) -> float:
        """Get company's total emissions"""
        return self.company_emissions.get(company_address, 0.0)
    
    def get_company_net_balance(self, company_address: str) -> float:
        """Get company's net carbon balance (credits - emissions)"""
        credits = self.get_company_carbon_balance(company_address)
        emissions = self.get_company_emissions(company_address)
        return credits - emissions
    
    def purchase_carbon_credits(self, 
                              buyer: str, 
                              seller: str, 
                              amount: float, 
                              price_per_ton: float) -> bool:
        """Purchase carbon credits from marketplace"""
        
        # Check if seller has enough credits
        seller_credits = self.get_company_carbon_balance(seller)
        if seller_credits < amount:
            raise ValueError(f"Seller has insufficient credits. Available: {seller_credits}, Requested: {amount}")
        
        # Find and deactivate seller's credits
        credits_to_transfer = []
        remaining_amount = amount
        
        for credit in self.carbon_credits.get(seller, []):
            if credit.is_active and remaining_amount > 0:
                if credit.amount <= remaining_amount:
                    credits_to_transfer.append(credit)
                    remaining_amount -= credit.amount
                    credit.is_active = False
                else:
                    # Split the credit
                    new_credit = CarbonCredit(
                        project_id=credit.project_id,
                        amount=remaining_amount,
                        price_per_ton=price_per_ton,
                        seller=buyer,
                        is_active=True,
                        created_at=datetime.now()
                    )
                    credits_to_transfer.append(new_credit)
                    credit.amount -= remaining_amount
                    remaining_amount = 0
        
        # Transfer credits to buyer
        if buyer not in self.carbon_credits:
            self.carbon_credits[buyer] = []
        
        for credit in credits_to_transfer:
            credit.seller = buyer
            self.carbon_credits[buyer].append(credit)
        
        total_cost = amount * price_per_ton
        print(f"✅ Transferred {amount} carbon credits from {seller} to {buyer} for ${total_cost}")
        return True
    
    def get_project_details(self, project_id: int) -> Optional[BlueCarbonProject]:
        """Get project details"""
        return self.projects.get(project_id)
    
    def get_all_projects(self) -> List[BlueCarbonProject]:
        """Get all registered projects"""
        return list(self.projects.values())
    
    def get_verification_records(self, project_id: int) -> List[VerificationRecord]:
        """Get all verification records for a project"""
        return [v for v in self.verifications.values() if v.project_id == project_id]
    
    def _store_to_ipfs(self, data: Dict) -> str:
        """Store data to IPFS (mock implementation)"""
        # In production, this would upload to IPFS
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _create_data_hash(self, data: Dict) -> str:
        """Create hash for data integrity"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def get_marketplace_listings(self) -> List[Dict]:
        """Get available carbon credits in marketplace"""
        listings = []
        for seller, credits in self.carbon_credits.items():
            for credit in credits:
                if credit.is_active:
                    listings.append({
                        'seller': seller,
                        'project_id': credit.project_id,
                        'amount': credit.amount,
                        'price_per_ton': credit.price_per_ton,
                        'total_price': credit.amount * credit.price_per_ton,
                        'created_at': credit.created_at.isoformat()
                    })
        return listings
    
    def get_company_dashboard_data(self, company_address: str) -> Dict:
        """Get comprehensive dashboard data for a company"""
        return {
            'company_address': company_address,
            'carbon_credits': self.get_company_carbon_balance(company_address),
            'total_emissions': self.get_company_emissions(company_address),
            'net_balance': self.get_company_net_balance(company_address),
            'owned_projects': [p for p in self.projects.values() if p.owner == company_address],
            'verification_status': 'Carbon Positive' if self.get_company_net_balance(company_address) > 0 else 'Carbon Negative',
            'marketplace_listings': [l for l in self.get_marketplace_listings() if l['seller'] == company_address]
        }

# Global instance
blockchain_mrv = BlockchainMRVSystem()