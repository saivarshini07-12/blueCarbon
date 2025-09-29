#!/usr/bin/env python3
"""
Test script to verify all components are working correctly.
"""

import sys
import os
import traceback

def test_imports():
    """Test all important imports."""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✓ Streamlit")
    except ImportError as e:
        print(f"✗ Streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ Pandas")
    except ImportError as e:
        print(f"✗ Pandas: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✓ Plotly")
    except ImportError as e:
        print(f"✗ Plotly: {e}")
        return False
    
    try:
        from fpdf import FPDF
        print("✓ FPDF2")
    except ImportError as e:
        print(f"✗ FPDF2: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ Python-dotenv")
    except ImportError as e:
        print(f"✗ Python-dotenv: {e}")
        return False
    
    try:
        from crewai import Agent
        print("✓ CrewAI")
    except ImportError as e:
        print(f"✗ CrewAI: {e}")
        return False
    
    return True

def test_local_modules():
    """Test local module imports."""
    print("\nTesting local modules...")
    
    try:
        from emission_factors import get_emission_factor, get_categories, get_activities
        print("✓ emission_factors")
    except Exception as e:
        print(f"✗ emission_factors: {e}")
        return False
    
    try:
        from config import APP_NAME, EMISSION_SCOPES
        print("✓ config")
    except Exception as e:
        print(f"✗ config: {e}")
        return False
    
    try:
        from data_handler import DataHandler
        print("✓ data_handler")
    except Exception as e:
        print(f"✗ data_handler: {e}")
        return False
    
    try:
        from carbon_compliance import CarbonComplianceFramework
        print("✓ carbon_compliance")
    except Exception as e:
        print(f"✗ carbon_compliance: {e}")
        return False
    
    try:
        from report_generator import ReportGenerator
        print("✓ report_generator")
    except Exception as e:
        print(f"✗ report_generator: {e}")
        return False
    
    # Test ai_agents separately as it might need API key
    try:
        os.environ['GROQ_API_KEY'] = 'test_key'
        from ai_agents import CarbonFootprintAgents
        print("✓ ai_agents (structure)")
    except Exception as e:
        print(f"✗ ai_agents: {e}")
        return False
    
    return True

def test_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from emission_factors import get_emission_factor
        factor = get_emission_factor("Electricity", "India Grid")
        if factor and factor['factor'] == 0.82:
            print("✓ Emission factor lookup")
        else:
            print("✗ Emission factor lookup")
            return False
    except Exception as e:
        print(f"✗ Emission factor lookup: {e}")
        return False
    
    try:
        from data_handler import DataHandler
        handler = DataHandler()
        print("✓ DataHandler initialization")
    except Exception as e:
        print(f"✗ DataHandler initialization: {e}")
        return False
    
    try:
        from carbon_compliance import CarbonComplianceFramework
        framework = CarbonComplianceFramework()
        print("✓ CarbonComplianceFramework initialization")
    except Exception as e:
        print(f"✗ CarbonComplianceFramework initialization: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("Carbon Accounting Application - System Test")
    print("=" * 50)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
    
    if not test_local_modules():
        all_passed = False
    
    if not test_functionality():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The application should work correctly.")
        print("\nTo run the application:")
        print("streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
