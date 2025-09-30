#!/usr/bin/env python3
"""
Test script for Blue Carbon CO2 Sequestration Calculator
Demonstrates the automatic calculation feature
"""

from emission_factors import calculate_blue_carbon_sequestration, get_blue_carbon_rate_info

print("🌊 Blue Carbon CO2 Sequestration Calculator Test")
print("=" * 50)

# Test different ecosystem types and areas
test_scenarios = [
    {"area": 50, "ecosystem": "mangrove", "quality": 1.0, "description": "Average mangrove project"},
    {"area": 100, "ecosystem": "seagrass", "quality": 1.2, "description": "Good quality seagrass meadow"},
    {"area": 75, "ecosystem": "salt_marsh", "quality": 0.8, "description": "Degraded salt marsh restoration"},
    {"area": 200, "ecosystem": "coastal_wetland", "quality": 1.5, "description": "Excellent coastal wetland"}
]

for scenario in test_scenarios:
    print(f"\n📊 {scenario['description']}")
    print(f"   Area: {scenario['area']} hectares")
    print(f"   Ecosystem: {scenario['ecosystem']}")
    print(f"   Quality Factor: {scenario['quality']}x")
    
    result = calculate_blue_carbon_sequestration(
        scenario['area'], 
        scenario['ecosystem'], 
        scenario['quality']
    )
    
    if result:
        print(f"   ✅ Estimated Sequestration: {result['estimated_sequestration']} tons CO2/year")
        print(f"   📈 Range: {result['min_estimate']} - {result['max_estimate']} tons/year")
    else:
        print(f"   ❌ Error: Unknown ecosystem type")

# Show rate information
print("\n\n🔬 Sequestration Rate Database")
print("=" * 30)
ecosystems = ["mangrove", "seagrass", "salt_marsh", "coastal_wetland"]

for eco in ecosystems:
    info = get_blue_carbon_rate_info(eco)
    if info:
        print(f"\n🌱 {eco.replace('_', ' ').title()}:")
        print(f"   Base Rate: {info['rate']} tons CO2/hectare/year")
        print(f"   Range: {info['range'][0]} - {info['range'][1]} tons/hectare/year") 
        print(f"   Info: {info['description']}")

print("\n\n✨ The automatic calculation is now integrated into the Blue Carbon registration form!")
print("Users no longer need to manually input CO2 sequestration values.")