"""
Emission factors database for YourCarbonFootprint application.
Based on DEFRA/IPCC datasets for common emission sources.
"""

# Emission factors by category (in kgCO2e per unit)
EMISSION_FACTORS = {
    # Scope 1 - Direct emissions
    "Stationary Combustion": {
        "Natural Gas": {"factor": 0.18316, "unit": "kWh"},
        "Diesel": {"factor": 2.68787, "unit": "liter"},
        "LPG": {"factor": 1.55537, "unit": "kg"},
        "Coal": {"factor": 2.42287, "unit": "kg"},
    },
    "Mobile Combustion": {
        "Petrol/Gasoline": {"factor": 2.31495, "unit": "liter"},
        "Diesel": {"factor": 2.70553, "unit": "liter"},
        "LPG": {"factor": 1.55537, "unit": "liter"},
        "CNG": {"factor": 2.53721, "unit": "kg"},
    },
    "Refrigerants": {
        "R-410A": {"factor": 2088.0, "unit": "kg"},
        "R-134a": {"factor": 1430.0, "unit": "kg"},
        "R-404A": {"factor": 3922.0, "unit": "kg"},
        "R-407C": {"factor": 1774.0, "unit": "kg"},
    },
    
    # Scope 2 - Indirect emissions from purchased energy
    "Electricity": {
        "India Grid": {"factor": 0.82, "unit": "kWh"},
        "Indonesia Grid": {"factor": 0.87, "unit": "kWh"},
        "Japan Grid": {"factor": 0.47, "unit": "kWh"},
        "Solar Power": {"factor": 0.041, "unit": "kWh"},
        "Wind Power": {"factor": 0.011, "unit": "kWh"},
    },
    "Steam": {
        "Purchased Steam": {"factor": 0.19, "unit": "kg"},
    },
    "District Cooling": {
        "District Cooling": {"factor": 0.12, "unit": "kWh"},
    },
    
    # Scope 3 - Other indirect emissions
    "Business Travel": {
        "Short-haul Flight": {"factor": 0.15298, "unit": "passenger-km"},
        "Long-haul Flight": {"factor": 0.19085, "unit": "passenger-km"},
        "Train": {"factor": 0.03694, "unit": "passenger-km"},
        "Bus": {"factor": 0.10471, "unit": "passenger-km"},
        "Taxi": {"factor": 0.14549, "unit": "km"},
    },
    "Employee Commuting": {
        "Car (Petrol/Gasoline)": {"factor": 0.17336, "unit": "km"},
        "Car (Diesel)": {"factor": 0.16844, "unit": "km"},
        "Motorcycle": {"factor": 0.11501, "unit": "km"},
        "Bus": {"factor": 0.10471, "unit": "passenger-km"},
        "Train/Metro": {"factor": 0.03694, "unit": "passenger-km"},
    },
    "Waste": {
        "Landfill": {"factor": 0.45727, "unit": "kg"},
        "Recycling": {"factor": 0.01042, "unit": "kg"},
        "Composting": {"factor": 0.01042, "unit": "kg"},
        "Incineration": {"factor": 0.01613, "unit": "kg"},
    },
    "Water": {
        "Water Supply": {"factor": 0.344, "unit": "cubic meter"},
        "Water Treatment": {"factor": 0.708, "unit": "cubic meter"},
    },
    "Purchased Goods & Services": {
        "Paper": {"factor": 0.919, "unit": "kg"},
        "Plastic": {"factor": 3.14, "unit": "kg"},
        "Glass": {"factor": 0.85, "unit": "kg"},
        "Metal": {"factor": 1.37, "unit": "kg"},
        "Food": {"factor": 3.59, "unit": "kg"},
    },
}

# Scope categories
SCOPE_CATEGORIES = {
    "Scope 1": [
        "Stationary Combustion",
        "Mobile Combustion",
        "Refrigerants",
        "Process Emissions",
        "Fugitive Emissions"
    ],
    "Scope 2": [
        "Electricity",
        "Steam",
        "District Cooling",
        "District Heating"
    ],
    "Scope 3": [
        "Business Travel",
        "Employee Commuting",
        "Waste",
        "Water",
        "Purchased Goods & Services",
        "Capital Goods",
        "Fuel and Energy-Related Activities",
        "Upstream Transportation & Distribution",
        "Downstream Transportation & Distribution",
        "Use of Sold Products",
        "End-of-Life Treatment of Sold Products",
        "Leased Assets",
        "Franchises",
        "Investments"
    ]
}

# Get emission factor for a specific activity
def get_emission_factor(category, activity):
    """
    Get the emission factor for a specific activity within a category.
    
    Args:
        category (str): The emission category
        activity (str): The specific activity
        
    Returns:
        dict: Dictionary containing factor and unit, or None if not found
    """
    if category in EMISSION_FACTORS and activity in EMISSION_FACTORS[category]:
        return EMISSION_FACTORS[category][activity]
    return None

# Get all activities for a category
def get_activities(category):
    """
    Get all activities for a specific category.
    
    Args:
        category (str): The emission category
        
    Returns:
        list: List of activities for the category, or empty list if category not found
    """
    if category in EMISSION_FACTORS:
        return list(EMISSION_FACTORS[category].keys())
    return []

# Get all categories for a scope
def get_categories(scope):
    """
    Get all categories for a specific scope.
    
    Args:
        scope (str): The scope (Scope 1, Scope 2, or Scope 3)
        
    Returns:
        list: List of categories for the scope, or empty list if scope not found
    """
    if scope in SCOPE_CATEGORIES:
        return SCOPE_CATEGORIES[scope]
    return []

# Get unit for a specific activity
def get_unit(category, activity):
    """
    Get the unit for a specific activity within a category.
    
    Args:
        category (str): The emission category
        activity (str): The specific activity
        
    Returns:
        str: Unit for the activity, or None if not found
    """
    ef = get_emission_factor(category, activity)
    if ef:
        return ef["unit"]
    return None
