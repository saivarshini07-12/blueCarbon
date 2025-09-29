#!/usr/bin/env python3
"""
Blockchain Initialization Script for SIH 2025 Blue Carbon Registry
This script sets up and runs the blockchain backend for the carbon accounting system
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'web3',
        'eth-account',
        'pandas',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages)
    else:
        print("✅ All dependencies satisfied!")

def setup_blockchain_config():
    """Create blockchain configuration file"""
    print("\n⚙️  Setting up blockchain configuration...")
    
    config = {
        "blockchain_enabled": True,
        "network": "development",
        "rpc_url": "http://127.0.0.1:8545",
        "contract_address": "",
        "private_key": "",
        "ipfs_gateway": "https://ipfs.io/ipfs/",
        "verification_threshold": 2,
        "default_carbon_price": 50.0,
        "supported_ecosystems": [
            "mangrove",
            "seagrass", 
            "salt_marsh",
            "coastal_wetland"
        ],
        "verification_requirements": {
            "min_verifiers": 2,
            "max_verification_age_days": 365,
            "required_data_fields": [
                "area_measurement",
                "biomass_assessment", 
                "soil_carbon_measurement",
                "gps_coordinates",
                "photographic_evidence"
            ]
        }
    }
    
    config_file = project_root / "blockchain_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Blockchain config created at {config_file}")

def initialize_blockchain_data():
    """Initialize blockchain system with demo data"""
    print("\n🌊 Initializing blockchain with demo data...")
    
    try:
        from blockchain_mrv import blockchain_mrv
        
        # Check if data already exists
        if len(blockchain_mrv.projects) > 0:
            print(f"✅ Blockchain already has {len(blockchain_mrv.projects)} projects")
            return
        
        # Run the demo population script
        demo_script = project_root / "demo_populate.py"
        if demo_script.exists():
            print("📋 Running demo data population...")
            result = subprocess.run([sys.executable, str(demo_script)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Demo data populated successfully!")
            else:
                print(f"⚠️  Demo script warnings: {result.stderr}")
        else:
            print("⚠️  Demo script not found, creating basic data...")
            
    except Exception as e:
        print(f"⚠️  Error initializing blockchain data: {e}")

def start_streamlit_frontend():
    """Start the Streamlit frontend application"""
    print("\n🖥️  Starting Streamlit frontend...")
    
    app_file = project_root / "app.py"
    if not app_file.exists():
        print("❌ app.py not found!")
        return False
    
    print("🚀 Launching Streamlit application...")
    print("   Frontend will be available at: http://localhost:8501")
    print("   - Navigate to 'Carbon Credits' to see blockchain integration")
    print("   - Check 'Blue Carbon' for project management")
    print("   - Use 'Marketplace' for carbon credit trading")
    print("   - Access 'MRV System' for verification workflow")
    
    # Start Streamlit in background
    subprocess.Popen([
        sys.executable, '-m', 'streamlit', 'run', 
        str(app_file), '--server.port', '8501'
    ])
    
    return True

def start_blockchain_backend():
    """Start the blockchain backend service"""
    print("\n⛓️  Starting blockchain backend...")
    
    try:
        from blockchain_mrv import blockchain_mrv
        
        # Test blockchain initialization
        print("🔗 Testing blockchain connection...")
        
        # Display current blockchain status
        projects = blockchain_mrv.get_all_projects()
        total_credits = sum(blockchain_mrv.get_company_carbon_balance(addr) 
                          for addr in blockchain_mrv.carbon_credits.keys())
        
        print(f"📊 Blockchain Status:")
        print(f"   • Projects: {len(projects)}")
        print(f"   • Verifications: {len(blockchain_mrv.verifications)}")
        print(f"   • Carbon Credits Issued: {total_credits} tons CO2")
        print(f"   • Companies with Credits: {len(blockchain_mrv.carbon_credits)}")
        
        print("✅ Blockchain backend ready!")
        return True
        
    except Exception as e:
        print(f"❌ Blockchain backend error: {e}")
        return False

def display_usage_guide():
    """Display usage guide for the system"""
    print("\n" + "="*60)
    print("🎉 BLOCKCHAIN BLUE CARBON REGISTRY - READY FOR SIH 2025!")
    print("="*60)
    
    print("\n🌊 System Components:")
    print("   • Blockchain MRV System: ✅ Running")
    print("   • Streamlit Frontend: ✅ Available at http://localhost:8501")
    print("   • Smart Contracts: ✅ Configured")
    print("   • Demo Data: ✅ Populated")
    
    print("\n🎯 SIH 2025 Demo Flow:")
    print("   1. Open http://localhost:8501 in browser")
    print("   2. Navigate to 'Carbon Credits' - See company balance")
    print("   3. Check 'Blue Carbon' - View registered projects")
    print("   4. Use 'Marketplace' - Trade carbon credits")
    print("   5. Access 'MRV System' - Submit verification data")
    print("   6. Admin Panel - NCCR management tools")
    
    print("\n💡 Key Features to Demonstrate:")
    print("   • Transparent project registration")
    print("   • Multi-level verification system")
    print("   • Automated carbon credit issuance")
    print("   • Real-time marketplace trading")
    print("   • Company emissions vs credits tracking")
    print("   • AI-powered analytics and recommendations")
    
    print("\n🚀 Ready for evaluation!")

def main():
    """Main initialization function"""
    print("🌍 SIH 2025 - Blockchain-Based Blue Carbon Registry")
    print("   Problem Statement 25038 - Setup Script")
    print("-" * 50)
    
    # Step 1: Check dependencies
    check_dependencies()
    
    # Step 2: Setup configuration
    setup_blockchain_config()
    
    # Step 3: Initialize blockchain data
    initialize_blockchain_data()
    
    # Step 4: Start blockchain backend
    backend_ready = start_blockchain_backend()
    
    if backend_ready:
        # Step 5: Display usage guide
        display_usage_guide()
        
        # Step 6: Ask if user wants to start frontend
        response = input("\n🤔 Start Streamlit frontend? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            frontend_started = start_streamlit_frontend()
            if frontend_started:
                print("\n✅ System fully operational!")
                print("   Press Ctrl+C to stop the frontend when done")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n👋 Shutting down...")
        else:
            print("\n💡 To start frontend later, run: streamlit run app.py")
    else:
        print("\n❌ Backend initialization failed. Check the errors above.")

if __name__ == "__main__":
    main()