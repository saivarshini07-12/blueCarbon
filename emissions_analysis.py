import json
import pandas as pd
from datetime import datetime

# Load and analyze the emissions data
with open('data/emissions.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

print("=" * 60)
print("DETAILED EMISSIONS DATA ANALYSIS")
print("=" * 60)
print(f"Total records: {len(df)}")
print(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
print(f"Period: {(df['date'].max() - df['date'].min()).days} days")
print(f"Total emissions: {df['emissions_kgCO2e'].sum()/1000:.2f} tonnes CO2e")
print()

print("=" * 60)
print("BREAKDOWN BY SCOPE")
print("=" * 60)
scope_breakdown = df.groupby('scope').agg({
    'emissions_kgCO2e': 'sum',
    'activity': 'count'
}).round(2)
scope_breakdown.columns = ['Total_Emissions_kg', 'Activity_Count']
scope_breakdown['Emissions_tonnes'] = scope_breakdown['Total_Emissions_kg'] / 1000
scope_breakdown['Percentage'] = (scope_breakdown['Total_Emissions_kg'] / df['emissions_kgCO2e'].sum()) * 100

for scope in scope_breakdown.index:
    row = scope_breakdown.loc[scope]
    print(f"{scope}:")
    print(f"  - Emissions: {row['Emissions_tonnes']:.2f} tonnes ({row['Percentage']:.1f}%)")
    print(f"  - Activities: {row['Activity_Count']} entries")
    print()

print("=" * 60)
print("TOP 10 HIGHEST EMISSION ACTIVITIES")
print("=" * 60)
top_activities = df.nlargest(10, 'emissions_kgCO2e')
for idx, row in top_activities.iterrows():
    print(f"{row['activity']} ({row['scope']}):")
    print(f"  - Emissions: {row['emissions_kgCO2e']/1000:.2f} tonnes CO2e")
    print(f"  - Calculation: {row['quantity']:.0f} {row['unit']} × {row['emission_factor']:.2f} = {row['emissions_kgCO2e']:.0f} kg CO2e")
    print(f"  - Date: {row['date'].strftime('%Y-%m-%d')}")
    print(f"  - Facility: {row['facility']}")
    print(f"  - Notes: {row['notes']}")
    print()

print("=" * 60)
print("REALITY CHECK - QUESTIONABLE ACTIVITIES")
print("=" * 60)
print("Activities with emissions > 10 tonnes:")
high_emissions = df[df['emissions_kgCO2e'] > 10000]
if len(high_emissions) > 0:
    for idx, row in high_emissions.iterrows():
        print(f"⚠️  {row['activity']} = {row['emissions_kgCO2e']/1000:.1f} tonnes")
        print(f"    Calculation: {row['quantity']:.0f} {row['unit']} × {row['emission_factor']:.2f}")
        print(f"    Date: {row['date'].strftime('%Y-%m-%d')}")
        print(f"    Notes: {row['notes']}")
        print()
else:
    print("No activities with emissions > 10 tonnes found.")

print("=" * 60)
print("MONTHLY BREAKDOWN")
print("=" * 60)
df['month'] = df['date'].dt.strftime('%Y-%m')
monthly = df.groupby('month')['emissions_kgCO2e'].sum() / 1000
for month, emissions in monthly.items():
    print(f"{month}: {emissions:.2f} tonnes CO2e")

print()
print("=" * 60)
print("EMISSION FACTOR ANALYSIS")
print("=" * 60)
print("High emission factors (>100 kg CO2e per unit):")
high_factors = df[df['emission_factor'] > 100]
for idx, row in high_factors.iterrows():
    print(f"{row['activity']}: {row['emission_factor']:.0f} kg CO2e per {row['unit']}")
    print(f"  - Quantity: {row['quantity']:.0f} {row['unit']}")
    print(f"  - Total emissions: {row['emissions_kgCO2e']/1000:.2f} tonnes")
    print(f"  - Notes: {row['notes']}")
    print()

print("=" * 60)
print("SUMMARY FOR 1-MONTH PERIOD")
print("=" * 60)
print(f"Company: Manufacturing facility in Visakhapatnam")
print(f"Assessment Period: 1 month (January 2025)")
print(f"Total Emissions: {df['emissions_kgCO2e'].sum()/1000:.2f} tonnes CO2e")
print(f"Daily Average: {(df['emissions_kgCO2e'].sum()/1000)/28:.2f} tonnes CO2e per day")
print(f"Annual Projection: {(df['emissions_kgCO2e'].sum()/1000)*12:.2f} tonnes CO2e per year")
print()
print("Key Contributors:")
print(f"1. Manufacturing Electricity: {df[df['activity']=='Manufacturing Electricity']['emissions_kgCO2e'].sum()/1000:.2f} tonnes")
print(f"2. Refrigerant Leak: {df[df['activity']=='Refrigerant Leak']['emissions_kgCO2e'].sum()/1000:.2f} tonnes")
print(f"3. Raw Materials: {df[df['activity']=='Raw Materials']['emissions_kgCO2e'].sum()/1000:.2f} tonnes")
print(f"4. Boiler (Natural Gas): {df[df['activity']=='Boiler']['emissions_kgCO2e'].sum()/1000:.2f} tonnes")
print(f"5. Chemical Production: {df[df['activity']=='Chemical Production']['emissions_kgCO2e'].sum()/1000:.2f} tonnes")
