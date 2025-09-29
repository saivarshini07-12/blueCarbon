"""
Configuration settings for YourCarbonFootprint application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
APP_NAME = "YourCarbonFootprint"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A lightweight, multilingual carbon accounting and reporting tool for SMEs in Asia"

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Data settings
DATA_DIR = "data"
EMISSIONS_FILE = os.path.join(DATA_DIR, "emissions.json")
COMPANY_INFO_FILE = os.path.join(DATA_DIR, "company_info.json")

# Supported languages
SUPPORTED_LANGUAGES = ["English", "Hindi"]

# Emission scopes
EMISSION_SCOPES = ["Scope 1", "Scope 2", "Scope 3"]

# Scope descriptions
SCOPE_DESCRIPTIONS = {
    "Scope 1": "Direct emissions from owned or controlled sources",
    "Scope 2": "Indirect emissions from the generation of purchased energy",
    "Scope 3": "All other indirect emissions that occur in a company's value chain"
}

# Default units
DEFAULT_UNITS = [
    "kWh",
    "MWh",
    "liter",
    "kg",
    "tonne",
    "km",
    "passenger-km",
    "cubic meter",
    "square meter",
    "hour",
    "day",
    "piece",
    "USD"
]

# Regulatory frameworks
REGULATORY_FRAMEWORKS = {
    "EU CBAM": "EU Carbon Border Adjustment Mechanism",
    "Japan GX League": "Japan Green Transformation League",
    "Indonesia ETS/ETP": "Indonesia Emissions Trading System/Emissions Trading Program"
}

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)
