"""
Demo script to populate sample data for the Blockchain-based Blue Carbon Registry
This creates sample projects, verifications, and carbon credits for demonstration
"""

from blockchain_mrv import blockchain_mrv
from datetime import datetime, timedelta
import json

def populate_demo_data():
    """Populate the system with demonstration data"""
    
    print("🌊 Populating Blockchain Blue Carbon Registry with demo data...")
    
    # Sample blue carbon projects
    projects_data = [
        {
            "name": "Sundarbans Mangrove Restoration",
            "location": "West Bengal, India",
            "area": 150.0,
            "ecosystem_type": "mangrove",
            "estimated_sequestration": 75.0,
            "owner": "company_demo_001",
            "additional_data": {
                "biodiversity_impact": "Habitat restoration for Bengal tigers and 300+ bird species",
                "community_benefits": "Employment for 200+ local families in eco-tourism and conservation",
                "project_type": "blue_carbon_restoration",
                "funding_source": "Green Climate Fund"
            }
        },
        {
            "name": "Chilika Lake Seagrass Conservation",
            "location": "Odisha, India",
            "area": 85.0,
            "ecosystem_type": "seagrass",
            "estimated_sequestration": 42.5,
            "owner": "ngo_coastal_001",
            "additional_data": {
                "biodiversity_impact": "Critical habitat for migratory birds and marine species",
                "community_benefits": "Sustainable fishing practices for 150 fishing families",
                "project_type": "blue_carbon_restoration",
                "funding_source": "State Government Grant"
            }
        },
        {
            "name": "Kerala Backwaters Salt Marsh Restoration",
            "location": "Kerala, India",
            "area": 65.0,
            "ecosystem_type": "salt_marsh",
            "estimated_sequestration": 32.5,
            "owner": "company_demo_002",
            "additional_data": {
                "biodiversity_impact": "Restoration of endemic plant species and bird nesting sites",
                "community_benefits": "Water quality improvement and coastal protection",
                "project_type": "blue_carbon_restoration",
                "funding_source": "Corporate CSR Initiative"
            }
        },
        {
            "name": "Gujarat Coastal Wetland Project",
            "location": "Gujarat, India",
            "area": 120.0,
            "ecosystem_type": "coastal_wetland",
            "estimated_sequestration": 60.0,
            "owner": "panchayat_001",
            "additional_data": {
                "biodiversity_impact": "Flamingo breeding ground and migratory bird sanctuary",
                "community_benefits": "Salt production and sustainable tourism development",
                "project_type": "blue_carbon_restoration",
                "funding_source": "Community-based funding"
            }
        }
    ]
    
    # Register projects
    project_ids = []
    for project in projects_data:
        project_id = blockchain_mrv.register_blue_carbon_project(
            name=project["name"],
            location=project["location"],
            area=project["area"],
            ecosystem_type=project["ecosystem_type"],
            estimated_sequestration=project["estimated_sequestration"],
            owner=project["owner"],
            project_data=project["additional_data"]
        )
        project_ids.append(project_id)
        print(f"  ✅ Registered: {project['name']} (ID: {project_id})")
    
    print(f"\n📋 Registered {len(project_ids)} blue carbon projects")
    
    # Sample verification data
    verifiers = ["verifier_nccr_001", "verifier_icfre_001", "verifier_independent_001"]
    
    # Create verification records for some projects
    verification_data = [
        {
            "project_id": project_ids[0],  # Sundarbans
            "verified_amount": 68.5,
            "verifier": verifiers[0],
            "comments": "Field verification completed. Excellent mangrove growth and carbon sequestration rates confirmed.",
            "verification_data": {
                "area_measured": 148.5,
                "biomass_assessment": "High density mangrove forest with 85% survival rate",
                "soil_carbon_measurement": "152 tons C/hectare average",
                "gps_coordinates": "21.9497° N, 88.4931° E",
                "verification_method": "Field survey + drone mapping"
            }
        },
        {
            "project_id": project_ids[1],  # Chilika Lake
            "verified_amount": 38.2,
            "verifier": verifiers[1],
            "comments": "Seagrass restoration showing positive results. Marine biodiversity indicators improved.",
            "verification_data": {
                "area_measured": 82.3,
                "biomass_assessment": "Seagrass density 75% of target levels",
                "soil_carbon_measurement": "89 tons C/hectare average",
                "gps_coordinates": "19.7179° N, 85.3209° E",
                "verification_method": "Underwater survey + satellite imagery"
            }
        },
        {
            "project_id": project_ids[2],  # Kerala
            "verified_amount": 28.8,
            "verifier": verifiers[2],
            "comments": "Salt marsh restoration progressing well. Some areas need additional planting.",
            "verification_data": {
                "area_measured": 63.2,
                "biomass_assessment": "Native vegetation coverage at 70%",
                "soil_carbon_measurement": "95 tons C/hectare average",
                "gps_coordinates": "9.9312° N, 76.2673° E",
                "verification_method": "Ground truth + community monitoring"
            }
        }
    ]
    
    # Submit verifications
    verification_ids = []
    for verification in verification_data:
        verification_id = blockchain_mrv.submit_verification(
            project_id=verification["project_id"],
            verified_amount=verification["verified_amount"],
            verifier=verification["verifier"],
            verification_data=verification["verification_data"],
            comments=verification["comments"]
        )
        verification_ids.append(verification_id)
        print(f"  📋 Verification submitted for Project {verification['project_id']} by {verification['verifier']}")
    
    print(f"\n✅ Submitted {len(verification_ids)} verification records")
    
    # Approve some verifications and issue credits
    approved_count = 0
    for verification_id in verification_ids[:2]:  # Approve first 2 verifications
        try:
            blockchain_mrv.approve_verification_and_issue_credits(verification_id)
            approved_count += 1
            print(f"  💰 Verification {verification_id} approved and credits issued")
        except Exception as e:
            print(f"  ❌ Error approving verification {verification_id}: {e}")
    
    print(f"\n💰 Approved {approved_count} verifications and issued carbon credits")
    
    # Record some company emissions for demonstration
    company_emissions = [
        ("company_demo_001", 45.2),
        ("company_demo_002", 78.9),
        ("ngo_coastal_001", 12.3),
        ("panchayat_001", 23.7)
    ]
    
    for company, emissions in company_emissions:
        blockchain_mrv.record_company_emissions(company, emissions)
        print(f"  📊 Recorded {emissions} tons CO2 emissions for {company}")
    
    print(f"\n📊 Recorded emissions for {len(company_emissions)} organizations")
    
    # Print summary
    print("\n" + "="*50)
    print("🎉 DEMO DATA POPULATION COMPLETE!")
    print("="*50)
    
    # Show summary statistics
    total_projects = len(blockchain_mrv.projects)
    total_verifications = len(blockchain_mrv.verifications)
    total_credits_issued = sum(blockchain_mrv.get_company_carbon_balance(addr) for addr in blockchain_mrv.carbon_credits.keys())
    total_emissions = sum(blockchain_mrv.company_emissions.values())
    
    print(f"📊 Projects Registered: {total_projects}")
    print(f"📋 Verification Records: {total_verifications}")
    print(f"💰 Carbon Credits Issued: {total_credits_issued:.1f} tons CO2")
    print(f"📈 Total Emissions Recorded: {total_emissions:.1f} tons CO2")
    print(f"🏪 Companies with Credits: {len(blockchain_mrv.carbon_credits)}")
    
    print("\n🚀 Ready to explore the Blockchain Blue Carbon Registry!")
    print("   - Launch the Streamlit app to see the interactive dashboard")
    print("   - Explore Carbon Credits, Blue Carbon Projects, and MRV System pages")
    print("   - Test the marketplace functionality")
    
    return {
        "projects": total_projects,
        "verifications": total_verifications,
        "credits_issued": total_credits_issued,
        "total_emissions": total_emissions
    }

if __name__ == "__main__":
    summary = populate_demo_data()
    
    print(f"\n💡 Demo Summary:")
    print(f"   • Blue carbon projects can now earn verified carbon credits")
    print(f"   • Companies can offset their emissions by purchasing credits")
    print(f"   • MRV system ensures transparency and verification")
    print(f"   • Blockchain provides immutable record keeping")
    print(f"   • Ready for SIH 2025 demonstration!")