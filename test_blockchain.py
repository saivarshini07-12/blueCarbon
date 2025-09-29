#!/usr/bin/env python3
"""
Quick Blockchain Backend Test Script
Tests the blockchain integration and displays current status
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_blockchain_backend():
    """Test the blockchain backend functionality"""
    print("🔍 Testing Blockchain Backend...")
    print("-" * 40)
    
    try:
        # Import blockchain system
        from blockchain_mrv import blockchain_mrv
        print("✅ Blockchain MRV system imported successfully")
        
        # Test basic functionality
        print("\n📊 Current Blockchain Status:")
        
        # Get projects
        projects = blockchain_mrv.get_all_projects()
        print(f"   • Blue Carbon Projects: {len(projects)}")
        
        # Get verifications
        verifications = list(blockchain_mrv.verifications.values())
        approved_verifications = [v for v in verifications if v.is_approved]
        print(f"   • Verification Records: {len(verifications)}")
        print(f"   • Approved Verifications: {len(approved_verifications)}")
        
        # Get carbon credits
        total_credits = sum(blockchain_mrv.get_company_carbon_balance(addr) 
                          for addr in blockchain_mrv.carbon_credits.keys())
        total_emissions = sum(blockchain_mrv.company_emissions.values())
        print(f"   • Total Carbon Credits: {total_credits} tons CO2")
        print(f"   • Total Emissions Recorded: {total_emissions} tons CO2")
        print(f"   • Companies with Credits: {len(blockchain_mrv.carbon_credits)}")
        
        print("\n🌊 Project Details:")
        for project in projects:
            print(f"   • {project.name} ({project.ecosystem_type})")
            print(f"     Location: {project.location}, Area: {project.area} hectares")
        
        print("\n💰 Company Carbon Balances:")
        for company_addr in blockchain_mrv.carbon_credits.keys():
            credits = blockchain_mrv.get_company_carbon_balance(company_addr)
            emissions = blockchain_mrv.get_company_emissions(company_addr)
            net_balance = credits - emissions
            status = "🟢 Carbon Positive" if net_balance > 0 else "🔴 Carbon Negative"
            print(f"   • {company_addr}: {credits} credits - {emissions} emissions = {net_balance} net ({status})")
        
        print("\n🏪 Marketplace Status:")
        listings = blockchain_mrv.get_marketplace_listings()
        if listings:
            for listing in listings:
                print(f"   • {listing['amount']} tons @ ${listing['price_per_ton']}/ton from {listing['seller']}")
        else:
            print("   • No active marketplace listings")
        
        # Test a transaction
        print("\n🧪 Testing Blockchain Operations...")
        
        # Test emission recording
        test_company = "test_company_001"
        blockchain_mrv.record_company_emissions(test_company, 10.5)
        print(f"   ✅ Recorded test emissions for {test_company}")
        
        # Test credit balance retrieval
        balance = blockchain_mrv.get_company_carbon_balance(test_company)
        print(f"   ✅ Retrieved credit balance: {balance} tons")
        
        print("\n🎉 Blockchain Backend Test Complete!")
        print("✅ All systems operational and ready for SIH 2025 demo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing blockchain backend: {e}")
        import traceback
        traceback.print_exc()
        return False

def display_integration_status():
    """Display integration status with frontend"""
    print("\n🔗 Integration Status:")
    print("-" * 40)
    
    # Check if Streamlit app exists
    app_file = project_root / "app.py"
    if app_file.exists():
        print("✅ Streamlit frontend app found")
        
        # Check if blockchain imports are in the app
        with open(app_file, 'r') as f:
            app_content = f.read()
            if 'blockchain_mrv' in app_content:
                print("✅ Blockchain integration found in frontend")
            else:
                print("⚠️  Blockchain integration not found in frontend")
    else:
        print("❌ Streamlit frontend app not found")
    
    # Check configuration
    config_file = project_root / "blockchain_config.json"
    if config_file.exists():
        print("✅ Blockchain configuration file found")
    else:
        print("⚠️  Blockchain configuration file not found")

def main():
    print("🌍 SIH 2025 - Blockchain Backend Test")
    print("   Blue Carbon Registry MRV System")
    print("=" * 50)
    
    # Test blockchain backend
    backend_working = test_blockchain_backend()
    
    # Check integration status
    display_integration_status()
    
    if backend_working:
        print("\n🚀 Next Steps:")
        print("   1. Backend is working ✅")
        print("   2. Run 'streamlit run app.py' to start frontend")
        print("   3. Navigate to blockchain pages in the app:")
        print("      • Carbon Credits")
        print("      • Blue Carbon Projects") 
        print("      • Marketplace")
        print("      • MRV System")
        print("\n💡 Or run 'python run_blockchain.py' for full setup")
    else:
        print("\n❌ Backend issues detected. Check errors above.")

if __name__ == "__main__":
    main()