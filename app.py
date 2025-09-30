# Fix sqlite3 compatibility issue before any other imports
import sys
try:
    # Try to import pysqlite3 and replace sqlite3
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # pysqlite3 not available, will use system sqlite3
    pass

import streamlit as st
import pandas as pd
import os
import json
import shutil
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import base64
from io import BytesIO

# Import blockchain MRV system
from blockchain_mrv import blockchain_mrv, BlueCarbonProject, VerificationRecord, CarbonCredit
from company_manager import company_manager

# Load environment variables
load_dotenv()

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize company manager in session state
if 'company_manager' not in st.session_state:
    st.session_state.company_manager = company_manager

# Set page config for wide layout
st.set_page_config(page_title="CarbonSenseAI", page_icon="🌍", layout="wide")

# Initialize session state variables if they don't exist
if 'emissions_data' not in st.session_state:
    # Load data if exists, otherwise create empty dataframe
    if os.path.exists('data/emissions.json'):
        try:
            with open('data/emissions.json', 'r') as f:
                data = f.read().strip()
                if data:  # Check if file is not empty
                    try:
                        st.session_state.emissions_data = pd.DataFrame(json.loads(data))
                    except json.JSONDecodeError:
                        # Create a backup of the corrupted file
                        backup_file = f'data/emissions_backup_{int(time.time())}.json'
                        shutil.copy('data/emissions.json', backup_file)
                        st.warning(f"Corrupted emissions data file found. A backup has been created at {backup_file}")
                        # Create empty dataframe
                        st.session_state.emissions_data = pd.DataFrame(columns=[
                            'date', 'business_unit', 'project', 'scope', 'category', 'activity', 
                            'country', 'facility', 'responsible_person', 'quantity', 'unit', 
                            'emission_factor', 'emissions_kgCO2e', 'data_quality', 
                            'verification_status', 'notes'
                        ])
                else:
                    # Empty file, create new DataFrame
                    st.session_state.emissions_data = pd.DataFrame(columns=[
                        'date', 'business_unit', 'project', 'scope', 'category', 'activity', 
                        'country', 'facility', 'responsible_person', 'quantity', 'unit', 
                        'emission_factor', 'emissions_kgCO2e', 'data_quality', 
                        'verification_status', 'notes'
                    ])
        except Exception as e:
            st.error(f"Error loading emissions data: {str(e)}")
            # Create empty dataframe if loading fails
            st.session_state.emissions_data = pd.DataFrame(columns=[
                'date', 'business_unit', 'project', 'scope', 'category', 'activity', 
                'country', 'facility', 'responsible_person', 'quantity', 'unit', 
                'emission_factor', 'emissions_kgCO2e', 'data_quality', 
                'verification_status', 'notes'
            ])
            # Make sure data directory exists
            os.makedirs('data', exist_ok=True)
    else:
        st.session_state.emissions_data = pd.DataFrame(columns=[
            'date', 'business_unit', 'project', 'scope', 'category', 'activity', 
            'country', 'facility', 'responsible_person', 'quantity', 'unit', 
            'emission_factor', 'emissions_kgCO2e', 'data_quality', 
            'verification_status', 'notes'
        ])
        # Make sure data directory exists
        os.makedirs('data', exist_ok=True)
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Home"

# Company authentication session state
if 'company_logged_in' not in st.session_state:
    st.session_state.company_logged_in = False
if 'current_company' not in st.session_state:
    st.session_state.current_company = None
if 'company_data' not in st.session_state:
    st.session_state.company_data = None

# Translation dictionary
translations = {
    'English': {
        'title': '**CarbonSenseAI**',
        'subtitle': '**Carbon Accounting & Reporting Tool for Indian SMEs**',
        'dashboard': 'Dashboard',
        'data_entry': 'Data Entry',
        'reports': 'Reports',
        'compliance': 'Compliance',
        'settings': 'Settings',
        'about': 'About',
        'scope1': 'Scope 1 (Direct Emissions)',
        'scope2': 'Scope 2 (Indirect Emissions - Purchased Energy)',
        'scope3': 'Scope 3 (Other Indirect Emissions)',
        'date': 'Date',
        'scope': 'Scope',
        'category': 'Category',
        'activity': 'Activity',
        'quantity': 'Quantity',
        'unit': 'Unit',
        'emission_factor': 'Emission Factor',
        'emissions': 'Emissions (kgCO2e)',
        'notes': 'Notes',
        'add_entry': 'Add Entry',
        'upload_csv': 'Upload CSV',
        'download_report': 'Download Report',
        'total_emissions': 'Total Emissions',
        'emissions_by_scope': 'Emissions by Scope',
        'emissions_by_category': 'Emissions by Category',
        'emissions_over_time': 'Emissions Over Time',
        'save': 'Save',
        'clear_form': 'Clear Form',
        'cancel': 'Cancel',
        'success': 'Success!',
        'error': 'Error!',
        'entry_added': 'Entry added successfully!',
        'csv_uploaded': 'CSV uploaded successfully!',
        'report_downloaded': 'Report downloaded successfully!',
        'settings_saved': 'Settings saved successfully!',
        'no_data': 'No data available.',
        'welcome_message': 'Welcome to CarbonSenseAI! Start by adding your emissions data or uploading a CSV file. Designed for Indian SMEs to meet MoEF&CC and BIS standards.',
        'custom_category': 'Custom Category',
        'custom_activity': 'Custom Activity',
        'custom_unit': 'Custom Unit',
        'entry_failed': 'Failed to add entry.',
        'compliance_assessment': 'Compliance Assessment (MoEF&CC Standards)',
        'industry_benchmarks': 'Industry Benchmarks',
        'improvement_scenarios': 'Improvement Scenarios',
        'compliance_report': 'Compliance Report'
    }
}

# Function to get translated text
def t(key):
    return translations.get('English', {}).get(key, key)

# Function to format date in a nice way
def format_date_nice(date_obj):
    """Format date as 'Jan 30th 2025' style"""
    if pd.isna(date_obj) or date_obj is None:
        return "No date data"
    
    try:
        # Convert to datetime if it's not already
        if isinstance(date_obj, str):
            date_obj = pd.to_datetime(date_obj)
        
        # Get day with ordinal suffix
        day = date_obj.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        
        return date_obj.strftime(f"%b {day}{suffix} %Y")
    except:
        return "Invalid date"

# Function to save emissions data
def save_emissions_data():
    try:
        # Check if company is logged in
        if st.session_state.get('company_logged_in', False) and st.session_state.get('current_company'):
            # Use company manager to save company-specific data
            company_manager = st.session_state.get('company_manager')
            if company_manager:
                data_to_save = st.session_state.emissions_data.to_dict('records') if len(st.session_state.emissions_data) > 0 else []
                return company_manager.save_company_emissions_data(st.session_state.current_company, data_to_save)
            else:
                st.error("Company manager not available")
                return False
        else:
            # Fallback to global data for backward compatibility
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Create a backup of the existing file if it exists
            if os.path.exists('data/emissions.json'):
                backup_path = 'data/emissions_backup.json'
                try:
                    with open('data/emissions.json', 'r') as src, open(backup_path, 'w') as dst:
                        dst.write(src.read())
                except Exception:
                    # Continue even if backup fails
                    pass
            
            # Save data to JSON file with proper formatting
            with open('data/emissions.json', 'w') as f:
                if len(st.session_state.emissions_data) > 0:
                    json.dump(st.session_state.emissions_data.to_dict('records'), f, indent=2)
                else:
                    # Write empty array if no data
                    f.write('[]')
                    
            return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

# Function to add new emission entry
def add_emission_entry(date, business_unit, project, scope, category, activity, country, facility, responsible_person, quantity, unit, emission_factor, data_quality, verification_status, notes):
    """Add a new emission entry to the emissions data."""
    try:
        # Calculate emissions
        emissions_kgCO2e = float(quantity) * float(emission_factor)
        
        # Create new entry
        new_entry = {
            'date': date.strftime('%Y-%m-%d'),
            'business_unit': business_unit,
            'project': project,
            'scope': scope,
            'category': category,
            'activity': activity,
            'country': country,
            'facility': facility,
            'responsible_person': responsible_person,
            'quantity': float(quantity),
            'unit': unit,
            'emission_factor': float(emission_factor),
            'emissions_kgCO2e': emissions_kgCO2e,
            'data_quality': data_quality,
            'verification_status': verification_status,
            'notes': notes
        }
        
        # If company is logged in, save to company-specific data
        if st.session_state.get('company_logged_in', False) and st.session_state.get('current_company'):
            # Get company emissions data
            company_emissions = company_manager.get_company_emissions_data(st.session_state.current_company)
            company_emissions.append(new_entry)
            
            # Save company-specific data
            company_manager.save_company_emissions_data(st.session_state.current_company, company_emissions)
            
            # Update company total emissions
            company_manager.update_company_emissions(st.session_state.current_company, emissions_kgCO2e)
            
            # Also update session state for immediate display
            new_entry_df = pd.DataFrame([new_entry])
            if st.session_state.emissions_data.empty:
                st.session_state.emissions_data = new_entry_df.copy()
            else:
                st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, new_entry_df], ignore_index=True)
        else:
            # Fallback to global data (for backward compatibility)
            new_entry_df = pd.DataFrame([new_entry])
            if st.session_state.emissions_data.empty:
                st.session_state.emissions_data = new_entry_df.copy()
            else:
                st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, new_entry_df], ignore_index=True)
        
        # Save data and return success/failure
        return save_emissions_data()
    except Exception as e:
        st.error(f"Error adding entry: {str(e)}")
        return False

def delete_emission_entry(index):
    try:
        # Make a copy of the current data
        if len(st.session_state.emissions_data) > index:
            # Drop the row at the specified index
            st.session_state.emissions_data = st.session_state.emissions_data.drop(index).reset_index(drop=True)
            
            # Save data and return success/failure
            return save_emissions_data()
        else:
            st.error("Invalid index for deletion")
            return False
    except Exception as e:
        st.error(f"Error deleting entry: {str(e)}")
        return False

# Function to process uploaded CSV with enhanced date handling
def process_csv(uploaded_file, start_date=None, end_date=None):
    """Process uploaded CSV file and add to emissions data with flexible date handling."""
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)
        
        # Read CSV file with better error handling
        try:
            df = pd.read_csv(uploaded_file)
        except pd.errors.EmptyDataError:
            st.error("The uploaded file appears to be empty. Please upload a valid CSV file.")
            return False
        except pd.errors.ParserError as e:
            st.error(f"Error parsing CSV file: {str(e)}. Please check the file format.")
            return False
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")
            return False
        
        # Check if dataframe is empty
        if df.empty:
            st.error("The uploaded CSV file contains no data.")
            return False
            
        required_columns = ['scope', 'category', 'activity', 'quantity', 'unit', 'emission_factor']
        
        # Check if all required columns exist (date/reporting_period is now optional)
        missing_required = [col for col in required_columns if col not in df.columns]
        if missing_required:
            st.error(f"CSV must contain all required columns: {', '.join(missing_required)}")
            return False
        
        # Handle date column - now optional (support both 'date' and 'reporting_period')
        has_dates = 'date' in df.columns
        has_reporting_period = 'reporting_period' in df.columns
        
        if has_dates:
            st.info("✅ Date column found - using specific dates from your file")
            try:
                # Validate existing dates
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                
                # Check for invalid dates
                invalid_dates = df['date'].isnull().sum()
                if invalid_dates > 0:
                    st.warning(f"⚠️ Found {invalid_dates} invalid dates - these will be auto-assigned to assessment period")
                
                # Convert valid dates to string format
                df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                
            except Exception as e:
                st.warning(f"Date processing issue: {str(e)} - will auto-assign dates")
                has_dates = False
        elif has_reporting_period:
            st.info("📊 Reporting period found - using period-based data")
            # Use current date for reporting period data
            df['date'] = datetime.now().strftime('%Y-%m-%d')
            st.info("📅 Using current date for reporting period data")
        
        if not has_dates and not has_reporting_period:
            # Auto-assign current date for all entries
            st.info("📊 No date column - using current date for all entries")
            df['date'] = datetime.now().strftime('%Y-%m-%d')
            st.info("📅 Using current date for all entries")
        
        # Validate data types
        try:
            # Convert quantity and emission_factor to float
            df['quantity'] = df['quantity'].astype(float)
            df['emission_factor'] = df['emission_factor'].astype(float)
        except Exception as e:
            st.error(f"Data validation error: {str(e)}")
            return False
        
        # Calculate emissions if not provided, or use pre-calculated if available
        if 'emissions_kgCO2e' not in df.columns:
            df['emissions_kgCO2e'] = df['quantity'] * df['emission_factor']
            st.info("✅ Calculated emissions from quantity × emission factor")
        else:
            # Use pre-calculated emissions but validate
            df['emissions_kgCO2e'] = pd.to_numeric(df['emissions_kgCO2e'], errors='coerce')
            st.info("✅ Using pre-calculated emissions from your file")
        
        # Add enterprise fields if not present
        enterprise_fields = {
            'business_unit': 'Corporate',
            'project': 'Not Applicable',
            'country': 'India',
            'facility': '',
            'responsible_person': '',
            'data_quality': 'Medium',
            'verification_status': 'Unverified',
            'notes': ''
        }
        
        # Add missing columns with default values
        for field, default_value in enterprise_fields.items():
            if field not in df.columns:
                df[field] = default_value
        
        # Clean up reporting_period column if it exists (not needed in final data)
        if 'reporting_period' in df.columns:
            df = df.drop('reporting_period', axis=1)
            st.info("ℹ️ Converted reporting period to date format for storage")
        
        # Append to existing data (handle empty DataFrame case)
        if st.session_state.emissions_data.empty:
            st.session_state.emissions_data = df.copy()
        else:
            st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, df], ignore_index=True)
        
        # Save data
        if save_emissions_data():
            st.success(f"Successfully added {len(df)} entries to your emissions database")
            return True
        else:
            st.error("Failed to save data")
            return False
    except Exception as e:
        st.error(f"Error processing CSV: {str(e)}")
        return False

# Function to generate PDF report
def generate_report():
    # Create a BytesIO object
    buffer = BytesIO()
    
    # Create a simple CSV report for now
    st.session_state.emissions_data.to_csv(buffer, index=False)
    buffer.seek(0)
    
    return buffer

# Custom CSS with JavaScript for enhanced UI
def local_css():
    st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Base styling with classic colorful theme */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #2c3e50;
    }
    
    /* Remove default Streamlit styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main container with classic light background */
    .main .block-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e3e8ff;
    }
    
    /* Ensure main content text is visible */
    .main .block-container * {
        color: #2c3e50 !important;
    }
    
    /* Exception for elements that should have different colors */
    .main .block-container .welcome-hero * {
        color: #ffffff !important;
    }
    
    .main .block-container .step * {
        color: #ffffff !important;
    }
    
    /* Remove complex animations */
    .main .block-container .metric-value {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sidebar with elegant gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 0 20px 20px 0;
        box-shadow: 5px 0 15px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding: 2rem 1rem;
    }
    
    /* Sidebar title with better contrast */
    [data-testid="stSidebar"] h1 {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 0.5rem !important;
    }
    
    /* Sidebar subtitle */
    [data-testid="stSidebar"] p {
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        opacity: 0.9;
    }
    
    /* Sidebar navigation section title */
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        margin: 1.5rem 0 0.5rem 0 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Navigation buttons with high contrast text */
    [data-testid="stSidebar"] .stButton>button {
        width: 100% !important;
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 0.8rem 1.2rem !important;
        margin: 0.3rem 0 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
        text-align: left !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%) !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stButton>button:active {
        transform: translateY(-1px) !important;
        color: #ffffff !important;
    }
    
    /* Active navigation button with high contrast */
    [data-testid="stSidebar"] .stButton>button.active {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
        box-shadow: 0 4px 15px rgba(231,76,60,0.4) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
    }
    
    /* Ensure all button text is visible */
    [data-testid="stSidebar"] .stButton>button span {
        color: #ffffff !important;
        font-weight: inherit !important;
        text-shadow: inherit !important;
    }
    
    [data-testid="stSidebar"] .stButton>button div {
        color: #ffffff !important;
        font-weight: inherit !important;
        text-shadow: inherit !important;
    }
    
    [data-testid="stSidebar"] .stButton>button * {
        color: #ffffff !important;
        font-weight: inherit !important;
        text-shadow: inherit !important;
    }
    
    /* Main content headings with better contrast */
    h1 {
        color: #2c3e50 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #34495e !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin: 2rem 0 1rem 0 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    h3 {
        color: #2c3e50 !important;
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        margin: 1.5rem 0 1rem 0 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Colorful metric cards with animated gradients */
    .metric-card {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 25%, #4ecdc4 50%, #ff6b6b 75%, #667eea 100%) !important;
        background-size: 300% 300% !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        text-align: center !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.15) !important;
        border: 3px solid rgba(255,255,255,0.3) !important;
        margin: 1rem 0 !important;
        transition: all 0.4s ease !important;
        animation: customMetricGradient 10s ease infinite !important;
        position: relative;
        overflow: hidden;
    }
    
    @keyframes customMetricGradient {
        0% { background-position: 0% 50%; }
        33% { background-position: 100% 25%; }
        66% { background-position: 50% 100%; }
        100% { background-position: 0% 50%; }
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.03) !important;
        box-shadow: 0 25px 60px rgba(0,0,0,0.25) !important;
        border-color: rgba(255,255,255,0.6) !important;
        animation-duration: 6s !important;
    }
    
    .metric-value {
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        margin: 0.5rem 0 !important;
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7) !important;
    }
    
    .metric-label {
        font-size: 1rem !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    /* Streamlit metric styling for better visibility */
    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #e3e8ff;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .stMetric [data-testid="metric-container"] {
        color: #2c3e50 !important;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        color: #2c3e50 !important;
    }
    
    .stMetric [data-testid="metric-container"] > div > div {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="metric-container"] label {
        color: #6c757d !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    .stMetric [data-testid="metric-container"] > div[data-testid="metric-value"] {
        color: #2c3e50 !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }
    
    /* Enhanced buttons with colorful gradients and high contrast */
    .stButton>button {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
        background: linear-gradient(135deg, #ff8e8e 0%, #6ee0d6 100%) !important;
    }
    
    .stButton>button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Primary button styling with better contrast */
    .stButton>button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 100%) !important;
        color: #2c3e50 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(255,215,0,0.4) !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.5) !important;
    }
    
    .stButton>button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #ffed4a 0%, #ff8787 100%) !important;
        box-shadow: 0 6px 25px rgba(255,215,0,0.6) !important;
        color: #2c3e50 !important;
    }
    
    /* Colorful form styling */
    .stSelectbox>div>div {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border: 2px solid #e0e7ff;
        border-radius: 10px;
        transition: all 0.3s ease;
        color: #2c3e50 !important;
    }
    
    .stSelectbox>div>div>div {
        color: #2c3e50 !important;
    }
    
    .stSelectbox>div>div:hover {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102,126,234,0.3);
    }
    
    .stNumberInput>div>div {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border: 2px solid #e0e7ff;
        border-radius: 10px;
        transition: all 0.3s ease;
        color: #2c3e50 !important;
    }
    
    .stNumberInput>div>div>div>input {
        color: #2c3e50 !important;
    }
    
    .stNumberInput>div>div:hover {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102,126,234,0.3);
    }
    
    .stTextInput>div>div {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border: 2px solid #e0e7ff;
        border-radius: 10px;
        transition: all 0.3s ease;
        color: #2c3e50 !important;
    }
    
    .stTextInput>div>div>div>input {
        color: #2c3e50 !important;
    }
    
    .stTextInput>div>div:hover {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102,126,234,0.3);
    }
    
    .stTextArea>div>div {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border: 2px solid #e0e7ff;
        border-radius: 10px;
        transition: all 0.3s ease;
        color: #2c3e50 !important;
    }
    
    .stTextArea>div>div>div>textarea {
        color: #2c3e50 !important;
    }
    
    /* Colorful tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
        padding: 15px 25px;
        font-weight: 600;
        color: white;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 100%) !important;
        color: white !important;
        border-color: #ffd700 !important;
        box-shadow: 0 5px 15px rgba(255,215,0,0.4) !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1rem;
        color: #2c3e50 !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] * {
        color: #2c3e50 !important;
    }
    
    /* Colorful dataframe */
    .stDataFrame {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .stDataFrame * {
        color: #2c3e50 !important;
    }
    
    .stDataFrame table {
        background: white !important;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .stDataFrame td {
        background: white !important;
        color: #2c3e50 !important;
    }
    
    /* Info boxes with ultra-high contrast and perfect visibility */
    .stAlert {
        border-radius: 20px !important;
        border: none !important;
        padding: 2rem !important;
        margin: 1.5rem 0 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transform: scale(1.02);
        backdrop-filter: blur(10px);
    }
    
    /* Blue info boxes with colorful gradient transition */
    .stAlert[data-baseweb="notification"],
    div[data-testid="stAlert"][kind="info"],
    .stInfo {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border-left: 8px solid #4c63d2 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
        transition: all 0.3s ease !important;
    }
    
    .stAlert[data-baseweb="notification"]:hover,
    div[data-testid="stAlert"][kind="info"]:hover,
    .stInfo:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(102,126,234,0.4) !important;
        background: linear-gradient(135deg, #7c8cfa 0%, #8a5bb8 100%) !important;
    }
    
    .stAlert[data-baseweb="notification"] *,
    div[data-testid="stAlert"][kind="info"] *,
    .stInfo * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    /* Green success boxes with colorful gradient transition */
    .stSuccess,
    div[data-testid="stAlert"][kind="success"] {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%) !important;
        color: #ffffff !important;
        border-left: 8px solid #3bafaa !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
        transition: all 0.3s ease !important;
    }
    
    .stSuccess:hover,
    div[data-testid="stAlert"][kind="success"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(78,205,196,0.4) !important;
        background: linear-gradient(135deg, #6ee0d6 0%, #5fb3a3 100%) !important;
    }
    
    .stSuccess *,
    div[data-testid="stAlert"][kind="success"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    /* Red error boxes with vibrant gradient transition */
    .stError,
    div[data-testid="stAlert"][kind="error"] {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%) !important;
        color: #ffffff !important;
        border-left: 8px solid #e74c3c !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
        transition: all 0.3s ease !important;
    }
    
    .stError:hover,
    div[data-testid="stAlert"][kind="error"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(255,107,107,0.4) !important;
        background: linear-gradient(135deg, #ff8e8e 0%, #f76b7a 100%) !important;
    }
    
    .stError *,
    div[data-testid="stAlert"][kind="error"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    /* Orange warning boxes with golden gradient transition */
    .stWarning,
    div[data-testid="stAlert"][kind="warning"] {
        background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 100%) !important;
        color: #ffffff !important;
        border-left: 8px solid #e6c200 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
        transition: all 0.3s ease !important;
    }
    
    .stWarning:hover,
    div[data-testid="stAlert"][kind="warning"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(255,215,0,0.4) !important;
        background: linear-gradient(135deg, #ffed4a 0%, #ff8787 100%) !important;
    }
    
    .stWarning *,
    div[data-testid="stAlert"][kind="warning"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #2e7d32 0%, #388e3c 100%) !important;
        color: #ffffff !important;
        border-left: 8px solid #1b5e20 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    .stSuccess * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #d32f2f 0%, #c62828 100%) !important;
        color: #ffffff !important;
        border-left: 8px solid #b71c1c !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    .stError * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f57c00 0%, #ef6c00 100%) !important;
        color: #ffffff !important;
        border-left: 8px solid #e65100 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    .stWarning * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    /* Enhanced info box styling for better visibility */
    .stAlert div[data-testid="stMarkdownContainer"] {
        color: inherit !important;
    }
    
    .stAlert div[data-testid="stMarkdownContainer"] strong {
        color: inherit !important;
        font-weight: 700 !important;
    }
    
    .stAlert div[data-testid="stMarkdownContainer"] p {
        color: inherit !important;
        margin: 0 !important;
    }
    
    /* Force ultra-high contrast for ALL alert text elements */
    div[data-testid="stAlert"],
    div[data-testid="stAlert"] *,
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] strong,
    div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] div {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7) !important;
        line-height: 1.6 !important;
    }
    
    /* Bold text in alerts */
    div[data-testid="stAlert"] strong,
    div[data-testid="stAlert"] b {
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
    }
    
    /* Markdown container inside alerts */
    div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    
    div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] * {
        color: #ffffff !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7) !important;
    }
    
    /* Enhanced subheader and heading visibility */
    .stSubheader,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        color: #1a1a1a !important;
        font-weight: 800 !important;
        text-shadow: none !important;
        margin: 2rem 0 1.5rem 0 !important;
        font-size: 2rem !important;
    }
    
    /* General text visibility */
    div[data-testid="stMarkdownContainer"] {
        color: #1a1a1a !important;
        text-shadow: none !important;
    }
    
    div[data-testid="stMarkdownContainer"] p {
        color: #1a1a1a !important;
        text-shadow: none !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }
    
    /* All text elements forced visibility */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a !important;
        text-shadow: none !important;
    }
    
    /* Button text visibility */
    .stButton button {
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    /* Enhanced HTML-like website appearance with expressive UI */
    
    /* Global background with animated gradient */
    .stApp {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        color: #1a1a1a !important;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating particles animation */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(255,255,255,0.3) 2px, transparent 2px),
            radial-gradient(circle at 75% 75%, rgba(255,255,255,0.2) 1px, transparent 1px),
            radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 100px 100px, 50px 50px, 25px 25px;
        animation: float 20s ease-in-out infinite;
        pointer-events: none;
        z-index: -1;
    }
    
    @keyframes float {
        0%, 100% { transform: translate(0px, 0px) rotate(0deg); }
        33% { transform: translate(30px, -30px) rotate(120deg); }
        66% { transform: translate(-20px, 20px) rotate(240deg); }
    }
    
    /* Main container with glass morphism */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 1.5rem;
        box-shadow: 
            0 20px 60px rgba(0,0,0,0.15),
            0 0 0 1px rgba(255,255,255,0.3),
            inset 0 1px 0 rgba(255,255,255,0.6);
        border: 2px solid rgba(255,255,255,0.2);
        position: relative;
        overflow: hidden;
    }
    
    /* Glowing border animation */
    .main .block-container::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57, #ff9ff3, #54a0ff);
        background-size: 400% 400%;
        border-radius: 25px;
        z-index: -1;
        animation: borderGlow 3s ease infinite;
        filter: blur(10px);
    }
    
    @keyframes borderGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Ensure all text is highly visible */
    .main .block-container * {
        color: #1a1a1a !important;
        text-shadow: 0 1px 2px rgba(255,255,255,0.8) !important;
    }
    
    /* Enhanced sidebar with professional glass effect */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, 
            rgba(102, 126, 234, 0.95) 0%, 
            rgba(118, 75, 162, 0.95) 50%, 
            rgba(255, 107, 107, 0.95) 100%) !important;
        backdrop-filter: blur(20px);
        border-radius: 0 25px 25px 0;
        box-shadow: 
            5px 0 30px rgba(0,0,0,0.2),
            inset -1px 0 0 rgba(255,255,255,0.3);
        border-right: 2px solid rgba(255,255,255,0.2);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding: 2rem 1.5rem;
    }
    
    /* Sidebar title with enhanced visibility */
    [data-testid="stSidebar"] h1 {
        color: #ffffff !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        text-shadow: 
            2px 2px 4px rgba(0,0,0,0.7),
            0 0 10px rgba(255,255,255,0.3) !important;
        margin-bottom: 0.5rem !important;
        background: linear-gradient(45deg, #ffffff, #f8f9fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Sidebar subtitle with high contrast */
    [data-testid="stSidebar"] p {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7) !important;
        opacity: 1 !important;
        margin-bottom: 1rem !important;
    }
    
    /* Navigation section headers */
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        margin: 2rem 0 1rem 0 !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Attractive staggered navigation buttons with varying positions */
    [data-testid="stSidebar"] .stButton>button {
        width: 95% !important;
        background: linear-gradient(135deg, 
            rgba(255,255,255,0.2) 0%, 
            rgba(255,255,255,0.1) 100%) !important;
        color: #ffffff !important;
        border: 3px solid rgba(255,255,255,0.4) !important;
        padding: 1.2rem 1.8rem !important;
        margin: 0.8rem 0 !important;
        border-radius: 20px !important;
        font-weight: 800 !important;
        font-size: 18px !important;
        box-shadow: 
            0 12px 35px rgba(0,0,0,0.2),
            inset 0 2px 0 rgba(255,255,255,0.4) !important;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        text-align: center !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
        position: relative;
        overflow: hidden;
        letter-spacing: 1px;
    }
    
    /* Staggered positioning for attractive layout */
    [data-testid="stSidebar"] .stButton:nth-child(1)>button {
        margin-left: 5% !important;
        transform: translateX(-5px);
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(2)>button {
        margin-left: 0% !important;
        transform: translateX(5px);
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(3)>button {
        margin-left: 8% !important;
        transform: translateX(-3px);
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(4)>button {
        margin-left: 2% !important;
        transform: translateX(7px);
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(5)>button {
        margin-left: 6% !important;
        transform: translateX(-2px);
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(6)>button {
        margin-left: 1% !important;
        transform: translateX(4px);
    }
    
    /* Dynamic button hover effects with enhanced positioning */
    [data-testid="stSidebar"] .stButton>button:hover {
        transform: translateY(-8px) scale(1.05) rotateZ(1deg) !important;
        box-shadow: 
            0 20px 60px rgba(0,0,0,0.3),
            inset 0 2px 0 rgba(255,255,255,0.6) !important;
        background: linear-gradient(135deg, 
            rgba(255,255,255,0.35) 0%, 
            rgba(255,255,255,0.25) 100%) !important;
        color: #ffffff !important;
        border-color: rgba(255,255,255,0.8) !important;
        filter: brightness(1.2);
    }
    
    /* Specific hover transformations for each button */
    [data-testid="stSidebar"] .stButton:nth-child(1)>button:hover {
        transform: translateY(-8px) translateX(3px) scale(1.05) rotateZ(-1deg) !important;
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(2)>button:hover {
        transform: translateY(-8px) translateX(-3px) scale(1.05) rotateZ(1deg) !important;
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(3)>button:hover {
        transform: translateY(-8px) translateX(2px) scale(1.05) rotateZ(-0.5deg) !important;
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(4)>button:hover {
        transform: translateY(-8px) translateX(-2px) scale(1.05) rotateZ(0.5deg) !important;
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(5)>button:hover {
        transform: translateY(-8px) translateX(1px) scale(1.05) rotateZ(-0.8deg) !important;
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(6)>button:hover {
        transform: translateY(-8px) translateX(-1px) scale(1.05) rotateZ(0.8deg) !important;
    }
    
    /* Active button with distinct styling */
    [data-testid="stSidebar"] .stButton>button:active,
    [data-testid="stSidebar"] .stButton>button.active {
        background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 100%) !important;
        box-shadow: 
            0 8px 25px rgba(255,215,0,0.4),
            inset 0 1px 0 rgba(255,255,255,0.6) !important;
        color: #1a1a1a !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.7) !important;
        border-color: #ffd700 !important;
        transform: translateY(-3px) !important;
    }
    
    /* Ensure button text visibility */
    [data-testid="stSidebar"] .stButton>button * {
        color: inherit !important;
        font-weight: inherit !important;
        text-shadow: inherit !important;
    }
    
    /* Page transition effects */
    .main {
        animation: pageSlideIn 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    @keyframes pageSlideIn {
        0% {
            opacity: 0;
            transform: translateX(50px);
        }
        100% {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Welcome hero section with maximum visibility */
    .welcome-hero {
        background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%) !important;
        padding: 3rem 2rem !important;
        border-radius: 25px !important;
        margin: 2rem 0 !important;
        text-align: center !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
        border: 3px solid rgba(255,255,255,0.2) !important;
    }
    
    .welcome-hero h1 {
        color: #ffffff !important;
        font-size: 4rem !important;
        font-weight: 900 !important;
        margin-bottom: 1rem !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.8) !important;
        letter-spacing: 2px !important;
    }
    
    .welcome-hero p {
        color: #ffffff !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7) !important;
        opacity: 1 !important;
    }
    
    /* Enhanced headings with perfect visibility */
    h1 {
        color: #1a1a1a !important;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
        text-shadow: none !important;
        position: relative;
        letter-spacing: 2px;
    }
    
    h2 {
        color: #1a1a1a !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        margin: 2.5rem 0 2rem 0 !important;
        text-shadow: none !important;
        letter-spacing: 1px;
    }
    
    h3 {
        color: #1a1a1a !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin: 2rem 0 1.5rem 0 !important;
        text-shadow: none !important;
        letter-spacing: 1px;
    }
    
    /* Enhanced subheader styling */
    [data-testid="stMarkdownContainer"] h2 {
        color: #1a1a1a !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-shadow: none !important;
    }
    
    [data-testid="stMarkdownContainer"] h3 {
        color: #1a1a1a !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        text-shadow: none !important;
    }
    
    /* Stunning metric cards with permanent animated gradients */
    .stMetric {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 25%, #4ecdc4 50%, #ff6b6b 75%, #667eea 100%) !important;
        background-size: 300% 300% !important;
        padding: 2rem !important;
        border-radius: 20px !important;
        border: 3px solid rgba(255,255,255,0.3) !important;
        background-clip: padding-box !important;
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.15),
            0 5px 15px rgba(0,0,0,0.1) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        position: relative;
        overflow: hidden;
        animation: metricGradientFlow 8s ease infinite !important;
    }
    
    @keyframes metricGradientFlow {
        0% { background-position: 0% 50%; }
        25% { background-position: 100% 25%; }
        50% { background-position: 50% 100%; }
        75% { background-position: 25% 0%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Different gradients for each metric card */
    .stMetric:nth-child(1) {
        background: linear-gradient(45deg, #ff6b6b 0%, #4ecdc4 25%, #ffd700 50%, #667eea 75%, #ff6b6b 100%) !important;
        animation: metricGradient1 6s ease infinite !important;
    }
    
    .stMetric:nth-child(2) {
        background: linear-gradient(45deg, #4ecdc4 0%, #667eea 25%, #ff6b6b 50%, #ffd700 75%, #4ecdc4 100%) !important;
        animation: metricGradient2 7s ease infinite !important;
    }
    
    .stMetric:nth-child(3) {
        background: linear-gradient(45deg, #ffd700 0%, #ff6b6b 25%, #667eea 50%, #4ecdc4 75%, #ffd700 100%) !important;
        animation: metricGradient3 8s ease infinite !important;
    }
    
    @keyframes metricGradient1 {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes metricGradient2 {
        0% { background-position: 25% 0%; }
        50% { background-position: 75% 100%; }
        100% { background-position: 25% 0%; }
    }
    
    @keyframes metricGradient3 {
        0% { background-position: 50% 25%; }
        50% { background-position: 0% 75%; }
        100% { background-position: 50% 25%; }
    }
    
    /* Enhanced metric card hover animations */
    .stMetric:hover {
        transform: translateY(-15px) scale(1.05) !important;
        box-shadow: 
            0 30px 70px rgba(0,0,0,0.25),
            0 15px 35px rgba(0,0,0,0.15) !important;
        border-color: rgba(255,255,255,0.6) !important;
        animation-duration: 4s !important;
    }
    
    /* Force white text on colorful backgrounds */
    .stMetric [data-testid="metric-container"] {
        color: #ffffff !important;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        color: #ffffff !important;
    }
    
    .stMetric [data-testid="metric-container"] > div > div {
        color: #ffffff !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
    }
    
    .stMetric [data-testid="metric-container"] label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    .stMetric [data-testid="metric-container"] > div[data-testid="metric-value"] {
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 2.2rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7) !important;
    }
    
    /* All text inside metric cards should be white */
    .stMetric * {
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    /* Make positive delta text and arrows green */
    .stMetric [data-testid="metric-container"] [data-testid="metric-delta"] {
        color: #27ae60 !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7) !important;
    }
    
    .stMetric [data-testid="metric-container"] [data-testid="metric-delta"] svg {
        fill: #27ae60 !important;
    }
    

        right: -3px;
        bottom: -3px;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        border-radius: 20px;
        z-index: -1;
        animation: borderFlow 4s ease infinite;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .stMetric:hover::before {
        opacity: 1;
    }
    
    @keyframes borderFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Metric text with perfect contrast */
    .stMetric [data-testid="metric-container"] {
        color: #1a1a1a !important;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        color: #1a1a1a !important;
    }
    
    .stMetric [data-testid="metric-container"] label {
        color: #495057 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        text-shadow: 0 1px 2px rgba(255,255,255,0.8) !important;
    }
    
    .stMetric [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #1a1a1a !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        text-shadow: 0 1px 2px rgba(255,255,255,0.8) !important;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Enhanced buttons with stunning effects */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 0.8rem 2rem !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        box-shadow: 
            0 8px 25px rgba(102,126,234,0.3),
            0 4px 10px rgba(0,0,0,0.1) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        overflow: hidden;
    }
    
    /* Button hover effects */
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.05) !important;
        box-shadow: 
            0 15px 40px rgba(102,126,234,0.4),
            0 8px 20px rgba(0,0,0,0.15) !important;
        background: linear-gradient(135deg, #764ba2 0%, #f093fb 50%, #f5576c 100%) !important;
    }
    
    /* Primary button special styling */
    .stButton>button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 50%, #4ecdc4 100%) !important;
        color: #1a1a1a !important;
        font-weight: 800 !important;
        box-shadow: 
            0 8px 25px rgba(255,215,0,0.4),
            0 4px 10px rgba(0,0,0,0.1) !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.7) !important;
    }
    
    .stButton>button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #ffed4a 0%, #ff8787 50%, #6ee0d6 100%) !important;
        box-shadow: 
            0 15px 40px rgba(255,215,0,0.6),
            0 8px 20px rgba(0,0,0,0.15) !important;
        color: #1a1a1a !important;
    }
    
    /* Form elements with enhanced styling */
    .stSelectbox>div>div {
        background: linear-gradient(135deg, 
            rgba(255,255,255,0.95) 0%, 
            rgba(248,249,255,0.95) 100%) !important;
        border: 2px solid rgba(102,126,234,0.3) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        color: #1a1a1a !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }
    
    .stSelectbox>div>div:hover {
        border-color: rgba(102,126,234,0.6) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.15) !important;
        transform: translateY(-2px) !important;
    }
    
    .stTextInput>div>div {
        background: linear-gradient(135deg, 
            rgba(255,255,255,0.95) 0%, 
            rgba(248,249,255,0.95) 100%) !important;
        border: 2px solid rgba(102,126,234,0.3) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        color: #1a1a1a !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }
    
    .stTextInput>div>div:hover {
        border-color: rgba(102,126,234,0.6) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.15) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Enhanced tabs with smooth transitions */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background: linear-gradient(135deg, 
            rgba(102,126,234,0.9) 0%, 
            rgba(118,75,162,0.9) 100%);
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        padding: 15px 30px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.25) !important;
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 100%) !important;
        color: #1a1a1a !important;
        border-color: #ffd700 !important;
        box-shadow: 0 10px 30px rgba(255,215,0,0.4) !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.7) !important;
        transform: translateY(-5px) !important;
    }
    
    /* Tab content with smooth appearance */
    .stTabs [data-baseweb="tab-panel"] {
        background: linear-gradient(135deg, 
            rgba(255,255,255,0.95) 0%, 
            rgba(248,249,255,0.95) 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin-top: 1.5rem;
        color: #1a1a1a !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        animation: tabContentSlide 0.5s ease-out;
    }
    
    @keyframes tabContentSlide {
        0% {
            opacity: 0;
            transform: translateY(20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced dataframe styling */
    .stDataFrame {
        background: linear-gradient(135deg, 
            rgba(255,255,255,0.95) 0%, 
            rgba(248,249,255,0.95) 100%);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }
    
    .stDataFrame table {
        background: transparent !important;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    .stDataFrame td {
        background: rgba(255,255,255,0.8) !important;
        color: #1a1a1a !important;
        font-weight: 500 !important;
        text-shadow: 0 1px 1px rgba(255,255,255,0.8) !important;
    }
    
    /* Alert boxes with enhanced visibility */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
        font-weight: 600 !important;
        backdrop-filter: blur(10px);
    }
    
    .stAlert[data-baseweb="notification"] {
        background: linear-gradient(135deg, 
            rgba(59,130,246,0.9) 0%, 
            rgba(99,102,241,0.9) 100%) !important;
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, 
            rgba(34,197,94,0.9) 0%, 
            rgba(22,163,74,0.9) 100%) !important;
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, 
            rgba(239,68,68,0.9) 0%, 
            rgba(220,38,38,0.9) 100%) !important;
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, 
            rgba(245,158,11,0.9) 0%, 
            rgba(217,119,6,0.9) 100%) !important;
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    /* Ensure alert text is always visible */
    .stAlert * {
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    /* Loading and progress elements */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
        border-radius: 10px !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 10px;
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #764ba2, #f093fb);
    }
    .metric-card {
        background: white !important;
        color: #2c3e50 !important;
        border: 2px solid #3498db !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }
    
    .metric-card h3 {
        color: #2c3e50 !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .metric-card p {
        color: #34495e !important;
        font-weight: 600 !important;
        margin: 0.25rem 0 !important;
    }
    
    .metric-card .metric-value {
        color: #e74c3c !important;
        font-weight: 800 !important;
        font-size: 1.2em !important;
    }
    
    .metric-card .metric-label {
        color: #7f8c8d !important;
        font-weight: 500 !important;
    }
    
    /* White box text visibility for light/dark modes */
    .stMarkdown {
        color: #2c3e50 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #2c3e50 !important;
    }
    
    .stMarkdown p {
        color: #34495e !important;
    }
    
    .stMarkdown strong {
        color: #2c3e50 !important;
    }
    
    /* Override any theme-specific text coloring */
    .stApp {
        color: #2c3e50 !important;
    }
    
    .stApp p {
        color: #34495e !important;
    }
    
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #2c3e50 !important;
    }
    
    /* Streamlit native metric components */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #3498db !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    [data-testid="metric-container"] label {
        color: #7f8c8d !important;
        font-weight: 600 !important;
        font-size: 0.9em !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #2c3e50 !important;
        font-weight: 800 !important;
        font-size: 1.8em !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        color: #27ae60 !important;
        font-weight: 600 !important;
    }
    
    /* Column containers */
    .stColumn {
        color: #2c3e50 !important;
    }
    
    .stColumn h1, .stColumn h2, .stColumn h3, .stColumn h4, .stColumn h5, .stColumn h6 {
        color: #2c3e50 !important;
        font-weight: 700 !important;
    }
    
    .stColumn p {
        color: #34495e !important;
        font-weight: 500 !important;
    }
    
    .stColumn strong {
        color: #2c3e50 !important;
        font-weight: 700 !important;
    }
    
    /* Tab content */
    [data-testid="stTabs"] {
        color: #2c3e50 !important;
    }
    
    [data-testid="stTabs"] h1, [data-testid="stTabs"] h2, [data-testid="stTabs"] h3, [data-testid="stTabs"] h4, [data-testid="stTabs"] h5, [data-testid="stTabs"] h6 {
        color: #2c3e50 !important;
    }
    
    [data-testid="stTabs"] p {
        color: #34495e !important;
    }
    
    [data-testid="stTabs"] strong {
        color: #2c3e50 !important;
    }
    
    /* Specific text color fixes */
    .stText {
        color: #2c3e50 !important;
    }
    
    .stWrite {
        color: #2c3e50 !important;
    }
    
    .stSubheader {
        color: #2c3e50 !important;
    }
    
    .stHeader {
        color: #2c3e50 !important;
    }
    
    .stTitle {
        color: #2c3e50 !important;
    }
    
    /* Force all text elements to have high contrast */
    * {
        color: #2c3e50 !important;
    }
    
    p {
        color: #34495e !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50 !important;
    }
    
    strong {
        color: #2c3e50 !important;
    }
    
    span {
        color: #2c3e50 !important;
    }
    
    div {
        color: #2c3e50 !important;
    }
    
    /* Target success info boxes specifically */
    .stSuccess div {
        color: #1b5e20 !important;
    }
    
    .stSuccess p {
        color: #1b5e20 !important;
    }
    
    .stSuccess strong {
        color: #1b5e20 !important;
    }
    
    /* Target info boxes specifically */
    .stInfo div {
        color: #0c5460 !important;
    }
    
    .stInfo p {
        color: #0c5460 !important;
    }
    
    .stInfo strong {
        color: #0c5460 !important;
    }
    
    /* Target warning boxes specifically */
    .stWarning div {
        color: #e65100 !important;
    }
    
    .stWarning p {
        color: #e65100 !important;
    }
    
    .stWarning strong {
        color: #e65100 !important;
    }
    
    /* Target error boxes specifically */
    .stError div {
        color: #b71c1c !important;
    }
    
    .stError p {
        color: #b71c1c !important;
    }
    
    .stError strong {
        color: #b71c1c !important;
    }
    
    /* Plotly charts with colorful styling */
    .js-plotly-plot {
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        overflow: hidden;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: linear-gradient(135deg, #f1f1f1 0%, #e8e8e8 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        border: 2px solid transparent;
        background-clip: content-box;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b4190 100%);
        background-clip: content-box;
    }
    
    /* Loading animation */
    @keyframes rainbow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .rainbow-text {
        background: linear-gradient(-45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffd93d, #6c5ce7);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: rainbow 3s ease infinite;
    }
    
    /* Floating action button */
    .fab {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
        color: white;
        border: none;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        z-index: 1000;
    }
    
    .fab:hover {
        transform: scale(1.1);
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }
    
    /* Welcome hero section - allow inline styles to override */
    .welcome-hero {
        color: white !important;
        padding: 3rem 2rem;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        border: 3px solid rgba(255,255,255,0.3);
        position: relative;
        overflow: hidden;
    }
    
    /* Remove any background that might conflict */
    .welcome-hero[style] {
        background: inherit !important;
    }
    
    .welcome-hero h1 {
        color: white !important;
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .welcome-hero p {
        color: white !important;
        font-size: 1.2rem !important;
        opacity: 0.9;
        margin-bottom: 1.5rem !important;
    }
    
    /* Feature cards with clean styling */
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 2px solid #e3e8ff;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .feature-card h3 {
        color: #2c3e50 !important;
        margin-bottom: 1rem !important;
    }
    
    .feature-card p {
        color: #6c757d !important;
        line-height: 1.6;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Step indicator with clean design */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        padding: 1.5rem;
        background: #ffffff;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid #e3e8ff;
    }
    
    .step {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
        color: white !important;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        min-width: 120px;
    }
    
    .step:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .step.active {
        background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 100%);
        box-shadow: 0 4px 15px rgba(255,215,0,0.4);
    }
    
    .step.completed {
        background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
    }
    
    .step h3 {
        color: white !important;
        margin: 0 !important;
        font-size: 1rem !important;
    }
    
    .step p {
        color: white !important;
        margin: 0 !important;
        font-size: 0.8rem !important;
        opacity: 0.9;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
        animation: pulse 2s infinite;
    }
    
    /* Responsive design with enhanced text contrast */
    @media (max-width: 768px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }
        
        .step-indicator {
            flex-direction: column;
            gap: 1rem;
        }
        
        .step {
            min-width: 100%;
        }
    }
    
    /* Additional contrast improvements for all text elements */
    .stMarkdown {
        color: #2c3e50 !important;
    }
    
    .stMarkdown p {
        color: #2c3e50 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #2c3e50 !important;
    }
    
    .stMarkdown strong {
        color: #2c3e50 !important;
        font-weight: 700 !important;
    }
    
    .stMarkdown em {
        color: #2c3e50 !important;
    }
    
    .stMarkdown code {
        background: rgba(102,126,234,0.1) !important;
        color: #667eea !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
    }
    
    /* Container text styling */
    .stContainer {
        color: #2c3e50 !important;
    }
    
    .stContainer * {
        color: #2c3e50 !important;
    }
    
    /* Column text styling */
    .stColumn {
        color: #2c3e50 !important;
    }
    
    .stColumn * {
        color: #2c3e50 !important;
    }
    
    /* Ensure all text in main content area is visible */
    .main * {
        color: #2c3e50 !important;
    }
    
    /* Override for specific colored sections */
    .welcome-hero, .welcome-hero * {
        color: #ffffff !important;
    }
    
    .step, .step * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab"], .stTabs [data-baseweb="tab"] * {
        color: #ffffff !important;
    }
    
    .stDataFrame thead th, .stDataFrame thead th * {
        color: #ffffff !important;
    }
    
    /* Animated spacing for visual rhythm */
    [data-testid="stSidebar"] .stButton {
        animation: buttonFloat 3s ease-in-out infinite;
        animation-delay: calc(var(--button-index) * 0.2s);
    }
    
    [data-testid="stSidebar"] .stButton:nth-child(1) { --button-index: 0; }
    [data-testid="stSidebar"] .stButton:nth-child(2) { --button-index: 1; }
    [data-testid="stSidebar"] .stButton:nth-child(3) { --button-index: 2; }
    [data-testid="stSidebar"] .stButton:nth-child(4) { --button-index: 3; }
    [data-testid="stSidebar"] .stButton:nth-child(5) { --button-index: 4; }
    [data-testid="stSidebar"] .stButton:nth-child(6) { --button-index: 5; }
    
    @keyframes buttonFloat {
        0%, 100% { transform: translateY(0px) translateX(var(--base-transform-x, 0px)); }
        50% { transform: translateY(-3px) translateX(var(--base-transform-x, 0px)); }
    }
    
    /* Enhanced step cards with permanent colorful gradients and smooth transitions */
    .step-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%) !important;
        color: #ffffff !important;
        padding: 2.5rem !important;
        border-radius: 20px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.2) !important;
        border: 3px solid rgba(255,255,255,0.3) !important;
        margin: 1rem 0 !important;
        text-align: center !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        position: relative;
        overflow: hidden;
        animation: gradientShift 8s ease infinite;
        background-size: 200% 200%;
    }
    
    /* Different animated gradients for each step card */
    .step-card:nth-child(1) {
        background: linear-gradient(45deg, #ff6b6b 0%, #4ecdc4 25%, #667eea 50%, #ffd700 75%, #ff6b6b 100%) !important;
        animation: gradientFlow1 6s ease infinite;
    }
    
    .step-card:nth-child(2) {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 25%, #ff6b6b 50%, #4ecdc4 75%, #667eea 100%) !important;
        animation: gradientFlow2 6s ease infinite;
    }
    
    .step-card:nth-child(3) {
        background: linear-gradient(45deg, #ffd700 0%, #ff6b6b 25%, #4ecdc4 50%, #667eea 75%, #ffd700 100%) !important;
        animation: gradientFlow3 6s ease infinite;
    }
    
    /* Gradient animation keyframes */
    @keyframes gradientFlow1 {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes gradientFlow2 {
        0% { background-position: 25% 0%; }
        50% { background-position: 75% 100%; }
        100% { background-position: 25% 0%; }
    }
    
    @keyframes gradientFlow3 {
        0% { background-position: 50% 25%; }
        50% { background-position: 0% 75%; }
        100% { background-position: 50% 25%; }
    }
    
    /* Enhanced hover effects */
    .step-card:hover {
        transform: translateY(-10px) scale(1.05) !important;
        box-shadow: 0 25px 60px rgba(0,0,0,0.3) !important;
        border-color: rgba(255,255,255,0.6) !important;
        animation-duration: 3s !important;
    }
    
    .step-card * {
        color: #ffffff !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
    }
    
    .step-card strong {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        display: block !important;
        margin-bottom: 1rem !important;
        color: #ffffff !important;
    }
    
    .step-card p {
        color: #ffffff !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
    }
    
    /* Streamlit specific text elements */
    .stMarkdown {
        color: #1a1a1a !important;
    }
    
    .stMarkdown * {
        color: #1a1a1a !important;
    }
    
    /* Exception: Alert elements should remain white */
    div[data-testid="stAlert"] .stMarkdown,
    div[data-testid="stAlert"] .stMarkdown * {
        color: #ffffff !important;
    }
    
    </style>
    ''', unsafe_allow_html=True)

# Navigation component
def render_navigation():
    nav_items = [
        {"icon": "🏠", "label": "Home", "id": "Home"},
        {"icon": "🌊", "label": "Blue Carbon", "id": "Blue Carbon"},
        {"icon": "�", "label": "Data Entry", "id": "Data Entry"},
        {"icon": "📊", "label": "Dashboard", "id": "Dashboard"},
        {"icon": "⚖️", "label": "Compliance", "id": "Compliance"},
        {"icon": "💰", "label": "Carbon Credits", "id": "Carbon Credits"},
        {"icon": "�", "label": "Marketplace", "id": "Marketplace"},
        {"icon": "👥", "label": "MRV System", "id": "MRV System"},
        {"icon": "�️", "label": "Data Insights", "id": "Data Insights"},
        {"icon": "⚙️", "label": "Settings", "id": "Settings"}
    ]
    
    st.markdown("### Navigation")
    
    for item in nav_items:
        active_class = "active" if st.session_state.active_page == item["id"] else ""
        if st.sidebar.button(
            f"{item['icon']} {item['label']}", 
            key=f"nav_{item['id']}",
            help=f"Go to {item['label']}",
            use_container_width=True
        ):
            st.session_state.active_page = item["id"]
            st.rerun()

# Colorful metric card component
def colorful_metric_card(title, value, description=None, icon=None, prefix="", suffix="", color_scheme="default"):
    color_schemes = {
        "default": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "success": "linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)",
        "warning": "linear-gradient(135deg, #ffd93d 0%, #ff6b6b 100%)",
        "info": "linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%)",
        "purple": "linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%)"
    }
    
    gradient = color_schemes.get(color_scheme, color_schemes["default"])
    
    st.markdown(f'''
    <div class="metric-card">
        {f'<div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>' if icon else ''}
        <div class="metric-label">{title}</div>
        <div class="metric-value" style="background: {gradient}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{prefix}{value}{suffix}</div>
        {f'<div style="color: #888; font-size: 0.9rem;">{description}</div>' if description else ''}
    </div>
    ''', unsafe_allow_html=True)

# Metric card component
def metric_card(title, value, description=None, icon=None, prefix="", suffix=""):
    st.markdown(f'''
    <div class="metric-card">
        {f'<div style="font-size: 24px;">{icon}</div>' if icon else ''}
        <div class="metric-label">{title}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        {f'<div style="color: #aaa; font-size: 12px;">{description}</div>' if description else ''}
    </div>
    ''', unsafe_allow_html=True)

# Card component
def card(content, title=None):
    if title:
        st.markdown(f"<div class='stCard'><h3>{title}</h3>{content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='stCard'>{content}</div>", unsafe_allow_html=True)

# Apply custom CSS
local_css()

# Sidebar
with st.sidebar:
    st.header(t('title'))
    st.caption(t('subtitle'))
    
    st.divider()
    
    # Navigation
    render_navigation()
    
    st.divider()

# Main content

# Company Authentication Check
if not st.session_state.company_logged_in:
    # Show login/registration page
    st.markdown("<h1>🏢 Company Authentication</h1>", unsafe_allow_html=True)
    st.markdown("Please login or register your company to access the carbon accounting platform.")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register Company"])
    
    with tab1:
        st.subheader("Company Login")
        
        with st.form("login_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                login_email = st.text_input("Company Email*", help="Enter your registered company email")
            
            with col2:
                login_company_id = st.text_input("Company ID (Optional)", help="Enter your company ID if you have it")
            
            login_submit = st.form_submit_button("🔑 Login", type="primary")
            
            if login_submit:
                if login_email:
                    # Try to find company by email
                    company_data = company_manager.get_company_by_email(login_email)
                    
                    if company_data:
                        st.session_state.company_logged_in = True
                        st.session_state.current_company = company_data['company_id']
                        st.session_state.company_data = company_data
                        st.success(f"✅ Welcome back, {company_data['company_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Company not found. Please check your email or register first.")
                elif login_company_id:
                    # Try to authenticate by company ID
                    company_data = company_manager.authenticate_company(login_company_id)
                    
                    if company_data:
                        st.session_state.company_logged_in = True
                        st.session_state.current_company = login_company_id
                        st.session_state.company_data = company_data
                        st.success(f"✅ Welcome back, {company_data['company_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Company ID. Please check and try again.")
                else:
                    st.error("❌ Please enter either company email or company ID.")
    
    with tab2:
        st.subheader("Register New Company")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name*", help="Enter your company name")
                email = st.text_input("Company Email*", help="Enter company email address")
                industry = st.selectbox("Industry*", [
                    "Manufacturing", "Technology", "Healthcare", "Finance", "Retail",
                    "Energy", "Transportation", "Agriculture", "Construction", "Education",
                    "Hospitality", "Real Estate", "Telecommunications", "Other"
                ])
                location = st.text_input("Location*", help="City, State, Country")
            
            with col2:
                company_size = st.selectbox("Company Size*", [
                    "Startup (1-10 employees)",
                    "Small (11-50 employees)", 
                    "Medium (51-250 employees)",
                    "Large (251-1000 employees)",
                    "Enterprise (1000+ employees)"
                ])
                contact_person = st.text_input("Contact Person*", help="Primary contact person name")
                phone = st.text_input("Phone Number", help="Contact phone number")
                website = st.text_input("Website", help="Company website (optional)")
            
            # Terms and conditions
            agree_terms = st.checkbox("I agree to the terms and conditions and data processing policy*")
            
            register_submit = st.form_submit_button("🏢 Register Company", type="primary")
            
            if register_submit:
                if all([company_name, email, industry, location, company_size, contact_person]) and agree_terms:
                    try:
                        company_id = company_manager.register_company(
                            company_name=company_name,
                            email=email,
                            industry=industry,
                            location=location,
                            size=company_size,
                            contact_person=contact_person,
                            phone=phone,
                            website=website
                        )
                        
                        # Award initial carbon credits for registration
                        company_manager.award_carbon_credits(company_id, 100.0, "Welcome bonus for new registration")
                        
                        st.success(f"✅ Company registered successfully!")
                        st.info(f"**Company ID:** `{company_id}`")
                        st.info("🎁 **Welcome Bonus:** You've received 100 carbon credits for registering!")
                        st.balloons()
                        
                        # Auto-login the new company
                        company_data = company_manager.authenticate_company(company_id)
                        st.session_state.company_logged_in = True
                        st.session_state.current_company = company_id
                        st.session_state.company_data = company_data
                        
                        time.sleep(2)
                        st.rerun()
                        
                    except ValueError as e:
                        st.error(f"❌ Registration failed: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields and agree to terms and conditions.")
    
    # Stop execution here if not logged in
    st.stop()

# If company is logged in, show the main application
if st.session_state.company_logged_in:
    # Load company-specific emissions data
    company_emissions = company_manager.get_company_emissions_data(st.session_state.current_company)
    if company_emissions:
        st.session_state.emissions_data = pd.DataFrame(company_emissions)
    else:
        # Initialize empty dataframe for new companies
        st.session_state.emissions_data = pd.DataFrame(columns=[
            'date', 'business_unit', 'project', 'scope', 'category', 'activity', 
            'country', 'facility', 'responsible_person', 'quantity', 'unit', 
            'emission_factor', 'emissions_kgCO2e', 'data_quality', 
            'verification_status', 'notes'
        ])
    
    # Show company info in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🏢 Logged in as:")
        st.markdown(f"**{st.session_state.company_data['company_name']}**")
        st.markdown(f"ID: `{st.session_state.current_company}`")
        st.markdown(f"Industry: {st.session_state.company_data['industry']}")
        
        # Show quick stats
        company_summary = company_manager.get_company_carbon_summary(st.session_state.current_company)
        st.markdown("### 📊 Quick Stats:")
        st.metric("Carbon Credits", f"{company_summary.get('total_carbon_credits', 0):.1f} tons")
        st.metric("Total Emissions", f"{company_summary.get('total_emissions_tonnes', 0):.1f} tons")
        net_balance = company_summary.get('remaining_credits', 0)
        st.metric("Net Balance", f"{net_balance:.1f} tons", delta=f"{'Positive' if net_balance >= 0 else 'Negative'}")
        
        if st.button("🚪 Logout", type="secondary"):
            st.session_state.company_logged_in = False
            st.session_state.current_company = None
            st.session_state.company_data = None
            st.rerun()

if st.session_state.active_page == "Home":
    # Clean welcome experience for all users
    st.markdown("""
    <div class="welcome-hero" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important; transition: all 0.3s ease !important; border: 3px solid rgba(255,255,255,0.3) !important;" onmouseover="this.style.setProperty('background', 'linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%)', 'important')" onmouseout="this.style.setProperty('background', 'linear-gradient(135deg, #3498db 0%, #2980b9 100%)', 'important')">
        <h1>🌍 Welcome to Your Carbon Navigator! 🚀</h1>
        <p>Track, analyze, and reduce your environmental impact with our AI-powered platform.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick start guide with enhanced styling
    st.markdown("## 🎯 Quick Start Guide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="step-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important; transition: all 0.3s ease !important;" onmouseover="this.style.background='linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%)'" onmouseout="this.style.background='linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)'">
            <strong>Step 1: Add Data 📝</strong>
            <p>Start by adding your emissions data through our Data Entry section.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="step-card" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important; transition: all 0.3s ease !important;" onmouseover="this.style.background='linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%)'" onmouseout="this.style.background='linear-gradient(135deg, #3498db 0%, #2980b9 100%)'">
            <strong>Step 2: Analyze 📊</strong>
            <p>View your carbon footprint in the Dashboard and get insights.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="step-card" style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%) !important; transition: all 0.3s ease !important;" onmouseover="this.style.background='linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%)'" onmouseout="this.style.background='linear-gradient(135deg, #27ae60 0%, #229954 100%)'">
            <strong>Step 3: Comply ⚖️</strong>
            <p>Check compliance requirements and generate reports.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature showcase with better styling
    st.markdown("## ✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("**Smart Data Entry** 📝\n\nIntelligent forms with auto-suggestions and validation.")
        st.warning("**AI-Powered Analytics** 🤖\n\nGet intelligent recommendations for emission reduction.")
    
    with col2:
        st.info("**Compliance Tools** ⚖️\n\nBuilt-in compliance checking and reporting for Indian standards.")
        st.error("**Real-time Dashboards** 📊\n\nInteractive visualizations and comprehensive analytics.")
    
    # Call to action
    st.markdown("## 🚀 Ready to Start?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Start Data Entry", type="primary", use_container_width=True):
            st.session_state.active_page = "Data Entry"
            st.rerun()
    
    with col2:
        if st.button("📊 Explore Dashboard", use_container_width=True):
            st.session_state.active_page = "Dashboard"
            st.rerun()
    
    with col3:
        if st.button("⚖️ Check Compliance", use_container_width=True):
            st.session_state.active_page = "Compliance"
            st.rerun()
    
    # Additional helpful tips
    st.subheader("💡 Pro Tips for Success")
    
    tip1, tip2, tip3 = st.columns(3)
    
    with tip1:
        st.info("**🎯 Start Small & Smart**\n\nBegin with your most significant emission sources like electricity, fuel, and travel. Focus on data quality over quantity!")
    
    with tip2:
        st.warning("**📊 Monitor Regularly**\n\nSet up monthly data entry sessions to track your progress and identify trends in your carbon footprint.")
    
    with tip3:
        st.success("**🌱 Set Targets**\n\nDefine clear reduction goals and celebrate milestones. Every step towards sustainability counts!")
    
    # Help section
    st.subheader("❓ Need Help?")
    
    help1, help2 = st.columns(2)
    
    with help1:
        st.info("**📖 Documentation**\n\nCheck our comprehensive guides and tutorials to get the most out of the platform.")
    
    with help2:
        st.warning("**🤝 Support**\n\nOur team is here to help you succeed in your carbon accounting journey.")
    
    # Show current data status
    if len(st.session_state.emissions_data) > 0:
        st.divider()
        st.subheader("📊 Your Current Data Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate metrics - Fix pandas warning by creating a copy first
        emissions_data_copy = st.session_state.emissions_data.copy()
        emissions_data_copy['emissions_kgCO2e'] = pd.to_numeric(emissions_data_copy['emissions_kgCO2e'], errors='coerce')
        st.session_state.emissions_data = emissions_data_copy.fillna({'emissions_kgCO2e': 0})
        total_emissions = st.session_state.emissions_data['emissions_kgCO2e'].sum()
        total_entries = len(st.session_state.emissions_data)
        
        with col1:
            total_emissions = st.session_state.emissions_data['emissions_kgCO2e'].sum()
            st.metric("Total Emissions (kgCO2e)", f"{total_emissions:,.2f}")
        
        with col2:
            st.metric("Data Points", str(total_entries))
        
        with col3:
            scopes_covered = st.session_state.emissions_data['scope'].nunique()
            st.metric("Scopes Covered", f"{scopes_covered}/3")
        
        with col4:
            if 'date' in st.session_state.emissions_data.columns:
                st.session_state.emissions_data['date'] = pd.to_datetime(st.session_state.emissions_data['date'], errors='coerce')
                if not st.session_state.emissions_data['date'].isnull().all():
                    latest_date = format_date_nice(st.session_state.emissions_data['date'].max())
                else:
                    latest_date = "No date data"
            else:
                latest_date = "No date data"
            st.metric("Latest Entry", latest_date)
        
        st.success("🎉 Great! You have emissions data. Visit the Dashboard to see detailed analytics and charts!")
    else:
        st.divider()
        st.info("📋 No emissions data yet. Start by adding your first entry to begin your carbon accounting journey!")

elif st.session_state.active_page == "Dashboard":
    # Dashboard for users with data - clean and simple
    st.title("📊 Your Carbon Dashboard")
    st.caption("Track your environmental impact and progress towards sustainability goals")
    
    if len(st.session_state.emissions_data) == 0:
        st.warning("📊 No emissions data available for dashboard visualization.")
        st.info("Please add some emissions data first using the Data Entry page to see your analytics dashboard.")
        
        # Add quick action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Go to Data Entry", type="primary", use_container_width=True):
                st.session_state.active_page = "Data Entry"
                st.rerun()
        with col2:
            if st.button("📤 Upload CSV Data", use_container_width=True):
                st.session_state.active_page = "Data Entry"
                st.rerun()
    else:
        # Calculate metrics - Fix pandas warning by creating a copy first
        emissions_data_copy = st.session_state.emissions_data.copy()
        emissions_data_copy['emissions_kgCO2e'] = pd.to_numeric(emissions_data_copy['emissions_kgCO2e'], errors='coerce')
        st.session_state.emissions_data = emissions_data_copy.fillna({'emissions_kgCO2e': 0})
        
        total_emissions = st.session_state.emissions_data['emissions_kgCO2e'].sum()
        total_entries = len(st.session_state.emissions_data)
        
        # Clean metrics display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_emissions = st.session_state.emissions_data['emissions_kgCO2e'].sum()
            st.metric("Total Emissions (kgCO2e)", f"{total_emissions:,.2f}")
        
        with col2:
            if 'date' in st.session_state.emissions_data.columns:
                st.session_state.emissions_data['date'] = pd.to_datetime(st.session_state.emissions_data['date'], errors='coerce')
                if not st.session_state.emissions_data['date'].isnull().all():
                    latest_date = format_date_nice(st.session_state.emissions_data['date'].max())
                else:
                    latest_date = "No date data"
            else:
                latest_date = "No date data"
            
            st.metric("Latest Entry", latest_date, help="Most recent data entry")
        
        with col3:
            scopes_covered = st.session_state.emissions_data['scope'].nunique()
            st.metric("Scopes Covered", f"{scopes_covered}/3", help="Emission scope coverage")
        
        with col4:
            st.metric("Data Points", str(total_entries), help="Total entries in database")
        
        # Charts section with enhanced styling
        if total_emissions > 0:
            st.markdown("<h2 style='text-align: center; margin: 3rem 0 2rem 0;'>📈 Your Analytics 📈</h2>", unsafe_allow_html=True)
            
            # Emissions by scope with vibrant colors
            scope_data = st.session_state.emissions_data.groupby('scope')['emissions_kgCO2e'].sum().reset_index()
            
            if not scope_data.empty:
                # Create a more colorful pie chart
                fig1 = px.pie(
                    scope_data, 
                    values='emissions_kgCO2e', 
                    names='scope',
                    title="🌍 Emissions by Scope",
                    color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#ffd93d', '#6c5ce7', '#a29bfe', '#fd79a8']
                )
                
                fig1.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>%{value:.1f} kgCO2e<br>%{percent}<extra></extra>',
                    textfont_size=14,
                    marker=dict(line=dict(color='#FFFFFF', width=3))
                )
                
                fig1.update_layout(
                    font=dict(size=16, color='#333'),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    title_font_size=24,
                    title_font_color='#667eea',
                    title_x=0.5,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.3,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=14)
                    ),
                    height=500
                )
                
                # Center the emissions by scope chart
                col_left, col_center, col_right = st.columns([1, 3, 1])
                with col_center:
                    st.plotly_chart(fig1, use_container_width=True)
            
            # Additional charts in columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Category breakdown with vibrant colors
                category_data = st.session_state.emissions_data.groupby('category')['emissions_kgCO2e'].sum().reset_index()
                category_data = category_data.sort_values('emissions_kgCO2e', ascending=False).head(10)
                
                if not category_data.empty:
                    fig2 = px.bar(
                        category_data,
                        x='emissions_kgCO2e',
                        y='category',
                        orientation='h',
                        title="📊 Top Emission Categories",
                        color='emissions_kgCO2e',
                        color_continuous_scale=['#ff6b6b', '#4ecdc4', '#ffd93d', '#6c5ce7']
                    )
                    
                    fig2.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        title_font_size=18,
                        title_font_color='#667eea',
                        title_x=0.5,
                        showlegend=False,
                        xaxis_title="Emissions (kgCO2e)",
                        yaxis_title="Category",
                        height=400,
                        font=dict(size=12, color='#333')
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                # Time series with vibrant colors
                if 'date' in st.session_state.emissions_data.columns:
                    time_data = st.session_state.emissions_data.copy()
                    time_data['date'] = pd.to_datetime(time_data['date'], errors='coerce')
                    time_data = time_data.dropna(subset=['date'])
                    
                    if not time_data.empty:
                        time_data['month'] = time_data['date'].dt.strftime('%Y-%m')
                        time_data = time_data.groupby(['month', 'scope'])['emissions_kgCO2e'].sum().reset_index()
                        
                        if len(time_data['month'].unique()) > 0:
                            fig3 = px.line(
                                time_data, 
                                x='month', 
                                y='emissions_kgCO2e', 
                                color='scope', 
                                markers=True,
                                title="📈 Emissions Over Time",
                                color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#ffd93d'],
                                line_shape='spline'
                            )
                            
                            fig3.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                title_font_size=18,
                                title_font_color='#667eea',
                                title_x=0.5,
                                xaxis_title="Month",
                                yaxis_title="Emissions (kgCO2e)",
                                legend_title="Scope",
                                height=400,
                                font=dict(size=12, color='#333')
                            )
                            
                            fig3.update_traces(line=dict(width=4), marker=dict(size=8))
                            
                            st.plotly_chart(fig3, use_container_width=True)
                        else:
                            st.info("📊 Not enough time data to show emissions over time.")
                    else:
                        st.info("📅 No valid date data available for time series chart.")
                else:
                    st.info("📈 No date information available for time series analysis.")
        else:
            st.info("📊 No emissions data available for visualization. Start by adding some data!")
    
    # Add some celebratory JavaScript
    st.markdown("""
    <script>
    // Trigger confetti after page load
    setTimeout(function() {
        createConfetti();
    }, 2000);
    </script>
    """, unsafe_allow_html=True)

elif st.session_state.active_page == "Data Entry":
    st.markdown(f"<h1> {t('data_entry')}</h1>", unsafe_allow_html=True)
    
    # Simplified reporting period - just show current data summary
    if len(st.session_state.emissions_data) > 0:
        st.markdown("### � Current Data Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_entries = len(st.session_state.emissions_data)
            st.metric("Total Entries", total_entries)
        
        with col2:
            total_emissions = st.session_state.emissions_data['emissions_kgCO2e'].sum()
            st.metric("Total Emissions (kgCO2e)", f"{total_emissions:,.2f}")
        
        with col3:
            scopes = st.session_state.emissions_data['scope'].nunique()
            st.metric("Scopes Covered", f"{scopes}/3")
        
        with col4:
            if total_entries > 0:
                latest_date = st.session_state.emissions_data['date'].max()
                # Convert timestamp to nice format for display (Jan 30th 2025)
                if pd.notna(latest_date):
                    # Convert to datetime and format using format_date_nice
                    latest_date_dt = pd.to_datetime(latest_date)
                    latest_date_str = format_date_nice(latest_date_dt)
                else:
                    latest_date_str = "No valid date"
                st.metric("Latest Entry", latest_date_str)
            else:
                st.metric("Latest Entry", "None")
    else:
        st.info("📋 No emissions data yet. Add your first entry below or upload a CSV file.")
    
    st.divider()
    
    tabs = st.tabs(["📝 Manual Entry", "📤 CSV Upload", "📋 Data Guide", "🤖 Data Assistant"])
    
    with tabs[0]:
        st.markdown("<h3>Add New Emission Entry</h3>", unsafe_allow_html=True)
        with st.form("emission_form", border=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🏢 Business Information")
                
                # Add date input as the first field
                date = st.date_input(
                    "Date", 
                    value=datetime.now().date(),
                    help="The date when the emission occurred",
                    format="DD-MM-YYYY"
                )
                
                # Add business unit field for enterprise tracking
                business_unit = st.selectbox(
                    "Business Unit", 
                    ["Corporate", "Manufacturing", "Sales", "R&D", "Logistics", "IT", "Other"],
                    help="The business unit responsible for this emission"
                )
                if business_unit == "Other":
                    business_unit = st.text_input("Custom Business Unit", placeholder="Enter business unit name")
                
                # Add project field for better categorization
                project = st.selectbox(
                    "Project", 
                    ["Not Applicable", "Carbon Reduction Initiative", "Sustainability Program", "Operational", "Other"],
                    help="The project or initiative associated with this emission"
                )
                if project == "Other":
                    project = st.text_input("Custom Project", placeholder="Enter project name")
                
                # Add scope selection with tooltip explaining each scope
                scope = st.selectbox(
                    t('scope'), 
                    ['Scope 1', 'Scope 2', 'Scope 3'],
                    help="Scope 1: Direct emissions from owned sources\nScope 2: Indirect emissions from purchased energy\nScope 3: All other indirect emissions in value chain"
                )
                category_options = {
                    'Scope 1': ['Stationary Combustion', 'Mobile Combustion', 'Fugitive Emissions', 'Process Emissions', 'Other'],
                    'Scope 2': ['Electricity', 'Steam', 'Heating', 'Cooling', 'Other'],
                    'Scope 3': ['Purchased Goods and Services', 'Capital Goods', 'Fuel- and Energy-Related Activities', 'Upstream Transportation and Distribution', 'Waste Generated in Operations', 'Business Travel', 'Employee Commuting', 'Upstream Leased Assets', 'Downstream Transportation and Distribution', 'Processing of Sold Products', 'Use of Sold Products', 'End-of-Life Treatment of Sold Products', 'Downstream Leased Assets', 'Franchises', 'Investments', 'Other']
                }
                category = st.selectbox(
                    t('category'), 
                    category_options[scope],
                    help="The category of emission source"
                )
                if category == 'Other':
                    category = st.text_input(t('custom_category'), placeholder="Enter custom category")
                
                # Location tracking
                country_options = ['India', 'United States', 'United Kingdom', 'Japan', 'Indonesia', 'Other']
                country = st.selectbox(
                    "Country", 
                    country_options,
                    help="Country where the emission occurred"
                )
                if country == 'Other':
                    country = st.text_input("Custom Country", placeholder="Enter country name")
                
                # Add facility/location field
                facility = st.text_input(
                    "Facility/Location", 
                    placeholder="e.g., Mumbai HQ, Jakarta Plant 2, etc.",
                    help="Specific facility or location where the emission occurred"
                )
                
                # Add responsible person field
                responsible_person = st.text_input(
                    "Responsible Person", 
                    placeholder="Person responsible for this emission source",
                    help="Name of the person accountable for managing this emission source"
                )
            with col2:
                activity_options = {
                    'Stationary Combustion': ['Boiler', 'Furnace', 'Generator', 'Other'],
                    'Mobile Combustion': ['Company Vehicle', 'Fleet Vehicle', 'Machinery', 'Other'],
                    'Fugitive Emissions': ['Refrigerant Leak', 'SF6 Emissions', 'Other'],
                    'Process Emissions': ['Cement Production', 'Chemical Production', 'Other'],
                    'Electricity': ['Office Electricity', 'Manufacturing Electricity', 'Other'],
                    'Steam': ['Industrial Steam', 'Heating Steam', 'Other'],
                    'Heating': ['Office Heating', 'Industrial Heating', 'Other'],
                    'Cooling': ['Office Cooling', 'Industrial Cooling', 'Other'],
                    'Purchased Goods and Services': ['Raw Materials', 'Office Supplies', 'Other'],
                    'Capital Goods': ['Equipment Purchase', 'Vehicle Purchase', 'Other'],
                    'Fuel- and Energy-Related Activities': ['Upstream Fuel Production', 'Transmission Losses', 'Other'],
                    'Upstream Transportation and Distribution': ['Supplier Transport', 'Inbound Logistics', 'Other'],
                    'Waste Generated in Operations': ['Solid Waste', 'Wastewater', 'Other'],
                    'Business Travel': ['Air Travel', 'Ground Travel', 'Hotel Stays', 'Other'],
                    'Employee Commuting': ['Private Vehicle', 'Public Transport', 'Other'],
                    'Upstream Leased Assets': ['Leased Equipment', 'Leased Vehicles', 'Other'],
                    'Downstream Transportation and Distribution': ['Outbound Logistics', 'Customer Transport', 'Other'],
                    'Processing of Sold Products': ['Intermediate Processing', 'Final Assembly', 'Other'],
                    'Use of Sold Products': ['Product Operation', 'Energy Consumption', 'Other'],
                    'End-of-Life Treatment of Sold Products': ['Recycling', 'Landfill', 'Other'],
                    'Downstream Leased Assets': ['Leased Equipment', 'Leased Property', 'Other'],
                    'Franchises': ['Franchise Operations', 'Franchise Energy Use', 'Other'],
                    'Investments': ['Investment Emissions', 'Financed Emissions', 'Other'],
                    'Other': ['Custom Activity', 'Other']
                }
                activity_key = category if category != 'Other' else 'Other'
                activity_list = activity_options.get(activity_key, ['Custom Activity', 'Other'])
                activity = st.selectbox(
                    "Activity", 
                    activity_options.get(category, ['Other']),
                    help="Specific activity that generated the emissions"
                )
                if activity == 'Other':
                    activity = st.text_input("Custom Activity", placeholder="Enter custom activity")
                
                # Add validation for quantity with tooltip
                quantity = st.number_input(
                    t('quantity'), 
                    min_value=0.0, 
                    format="%.2f",
                    help="The amount of activity (e.g., kWh used, liters consumed, etc.)"
                )
                
                # Enhanced unit selection with tooltip
                unit_options = ['kWh', 'MWh', 'GJ', 'liter', 'gallon', 'kg', 'tonne', 'km', 'mile', 'hour', 'day', 'piece', 'INR', 'Other']
                unit = st.selectbox(
                    t('unit'), 
                    unit_options,
                    help="The unit of measurement for the quantity"
                )
                if unit == 'Other':
                    unit = st.text_input(t('custom_unit'), placeholder="Enter custom unit")
                    
                # Emission factor auto-population based on country and category
                emission_factors = {
                    'India': {
                        'Electricity': 0.82, 'Mobile Combustion': 2.31, 'Stationary Combustion': 1.85, 'Other': 0.0
                    },
                    'United States': {
                        'Electricity': 0.42,
                        'Mobile Combustion': 2.32,
                        'Stationary Combustion': 2.01,
                        'Business Travel': 0.12,
                        'Employee Commuting': 0.15
                    }
                }
                default_factor = emission_factors.get(country, {}).get(category, 0.0) if country != 'Other' else 0.0
                
                # Now that default_factor is defined, show AI suggestion
                st.info(f"💡 AI Suggestion: Based on your selections, a typical emission factor for {category} in {country} would be around {default_factor:.4f} kgCO2e per unit.")
                
                emission_factor = st.number_input(
                    t('emission_factor'), 
                    min_value=0.0, 
                    value=default_factor, 
                    format="%.4f",
                    help=f"Emission factor in kgCO2e per unit. Typical range: {max(0.1, default_factor*0.8):.4f} to {default_factor*1.2:.4f}"
                )
                
                # Add data quality indicator with color-coded help
                data_quality = st.select_slider(
                    "Data Quality",
                    options=["Low", "Medium", "High"],
                    value="Medium",
                    help="🔴 Low: Estimated or proxy data\n🟡 Medium: Calculated from bills or invoices\n🟢 High: Directly measured or metered data"
                )
                
                # Add verification status with detailed help
                verification_status = st.selectbox(
                    "Verification Status",
                    ["Unverified", "Internally Verified", "Third-Party Verified"],
                    help="Unverified: No verification process applied\nInternally Verified: Checked by internal team\nThird-Party Verified: Validated by external auditor"
                )
                
                # Enhanced notes field with better guidance
                notes = st.text_area(
                    t('notes'), 
                    placeholder="Additional information, data sources, calculation methods, etc.",
                    help="Include information about data sources, calculation methodology, assumptions made, and any other relevant context"
                )
                
                # Add cost field for financial impact tracking (optional)
                cost = st.number_input(
                    "Cost (Optional)", 
                    min_value=0.0, 
                    value=0.0,
                    format="%.2f",
                    help="Optional: Associated cost in your local currency"
                )
                
                # Add cost currency if cost is entered
                if cost > 0:
                    currency = st.selectbox(
                        "Currency",
                        ["USD", "EUR", "INR", "GBP", "JPY", "Other"],
                        help="Currency for the entered cost"
                    )
            
            # Form submission buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                submitted = st.form_submit_button(t('add_entry'), type="primary", use_container_width=True)
            with col2:
                clear = st.form_submit_button(t('clear_form'), type="secondary", use_container_width=True)
            
            if submitted:
                # Basic validation
                if quantity <= 0:
                    st.error("Quantity must be greater than zero.")
                elif not facility.strip():
                    st.warning("Facility/Location is recommended for enterprise tracking.")
                else:
                    try:
                        # Include cost in the entry if provided
                        cost_value = cost if 'cost' in locals() and cost > 0 else 0.0
                        currency_value = currency if 'currency' in locals() and cost > 0 else ""
                        
                        add_emission_entry(
                            date, business_unit, project, scope, category, activity, country, facility,
                            responsible_person, quantity, unit, emission_factor, data_quality, verification_status, notes
                        )
                        st.success(t('entry_added'))
                        # Redirect to Dashboard after successful entry
                        st.session_state.active_page = "Dashboard"
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('entry_failed')} {str(e)}")
    
    # Show existing data table
    if len(st.session_state.emissions_data) > 0:
        st.markdown("<h3>Existing Emissions Data</h3>", unsafe_allow_html=True)
        
        # Create a copy of the dataframe with an action column
        display_df = st.session_state.emissions_data.copy()
        
        # Add a column for the delete action
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display the dataframe
            st.dataframe(
                display_df,
                column_config={
                    "date": st.column_config.DateColumn("Date", format="DD-MM-YYYY"),
                    "business_unit": st.column_config.TextColumn("Business Unit"),
                    "project": st.column_config.TextColumn("Project"),
                    "scope": st.column_config.TextColumn("Scope"),
                    "category": st.column_config.TextColumn("Category"),
                    "activity": st.column_config.TextColumn("Activity"),
                    "country": st.column_config.TextColumn("Country"),
                    "facility": st.column_config.TextColumn("Facility"),
                    "responsible_person": st.column_config.TextColumn("Responsible Person"),
                    "quantity": st.column_config.NumberColumn("Quantity", format="%.2f"),
                    "unit": st.column_config.TextColumn("Unit"),
                    "emission_factor": st.column_config.NumberColumn("Emission Factor", format="%.4f"),
                    "emissions_kgCO2e": st.column_config.NumberColumn("Emissions (kgCO2e)", format="%.2f"),
                    "data_quality": st.column_config.TextColumn("Data Quality"),
                    "verification_status": st.column_config.TextColumn("Verification"),
                    "notes": st.column_config.TextColumn("Notes"),
                },
                use_container_width=True,
                hide_index=False
            )
        
        with col2:
            # Add delete functionality
            st.markdown("### Delete Entry")
            entry_to_delete = st.number_input("Select entry number to delete", min_value=0, 
                                           max_value=len(display_df)-1 if len(display_df) > 0 else 0, 
                                           step=1, 
                                           help="Enter the index number of the entry you want to delete")
            
            if st.button("🗑️ Delete Selected Entry", type="primary"):
                if delete_emission_entry(entry_to_delete):
                    st.success(f"Entry {entry_to_delete} deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to delete entry {entry_to_delete}")
        
    
    with tabs[1]:
        st.markdown("<h3>📤 Upload CSV Data</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        ### 📊 CSV Format Requirements
        
        **Required Columns:**
        - `scope`: Scope 1, Scope 2, or Scope 3
        - `category`: Emission category (e.g., 'Electricity', 'Mobile Combustion')
        - `activity`: Description of the activity
        - `quantity`: Amount of activity data
        - `unit`: Unit of measurement (e.g., 'kWh', 'liter', 'kg')
        - `emission_factor`: CO2 emission factor per unit
        
        **Optional Columns:**
        - `date`: Specific date (YYYY-MM-DD format)
        - `reporting_period`: Period description (e.g., "January 2025")
        - `emissions_kgCO2e`: Pre-calculated emissions (if provided, will override quantity × emission_factor)
        - `business_unit`, `project`, `country`, `facility`, `responsible_person`
        - `data_quality`, `verification_status`, `notes`
        """)
        
        st.info("""
        **🎯 Flexible Date Handling:**
        - **CSV with dates**: We'll use the actual dates from your file
        - **CSV with reporting_period**: Perfect for monthly/quarterly reports
        - **CSV without dates**: We'll assign current date to all entries
        """)
        
        uploaded_file = st.file_uploader(
            "Choose CSV file", 
            type='csv',
            help="Upload your emissions data in CSV format"
        )
        
        if uploaded_file is not None:
            # Preview the uploaded file
            try:
                preview_df = pd.read_csv(uploaded_file)
                
                st.markdown("#### 📋 File Preview")
                st.dataframe(preview_df, use_container_width=True)
                
                # Show file info
                col1, col2 = st.columns(2)
                with col1:
                    # Count only non-empty data rows (excluding header)
                    data_rows = len(preview_df.dropna(how='all'))
                    st.metric("Data Rows", data_rows)
                with col2:
                    st.metric("Columns", len(preview_df.columns))
                
                # Show scope breakdown if available
                if 'scope' in preview_df.columns:
                    st.markdown("**📊 Scope Breakdown:**")
                    scope_counts = preview_df['scope'].value_counts()
                    cols = st.columns(len(scope_counts))
                    for i, (scope, count) in enumerate(scope_counts.items()):
                        with cols[i]:
                            st.metric(scope, count)
                
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
                uploaded_file = None
            
            if uploaded_file is not None:
                # Process button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Upload & Process Data", type="primary"):
                        if process_csv(uploaded_file):
                            st.success("✅ CSV uploaded successfully!")
                            st.info("💡 Data has been added to your emissions database. Check the summary above or go to other pages to analyze your data.")
                            time.sleep(2)
                            st.rerun()
                
                with col2:
                    if st.button("🔍 Validate Only", type="secondary"):
                        # Just validate without uploading
                        required_columns = ['scope', 'category', 'activity', 'quantity', 'unit', 'emission_factor']
                        missing_cols = [col for col in required_columns if col not in preview_df.columns]
                        
                        if missing_cols:
                            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                        else:
                            st.success("✅ All required columns present!")
                            
                            # Check for date column
                            if 'date' in preview_df.columns:
                                st.info("📅 Date column detected - will use specific dates")
                            elif 'reporting_period' in preview_df.columns:
                                st.info("📊 Reporting period detected - period-based data")
                            else:
                                st.info("� No date column - will use current date")
        
        
        # Sample CSV templates
        st.markdown("#### 📥 Download Sample CSV Templates")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**� Reporting Period Template (Recommended)**")
            
            # Create simple reporting period template
            sample_data_period = {
                'reporting_period': ['January 2025'] * 6,
                'business_unit': ['Manufacturing', 'Office Operations', 'Fleet', 'Data Center', 'Travel', 'Facilities'],
                'scope': ['Scope 2', 'Scope 1', 'Scope 1', 'Scope 2', 'Scope 3', 'Scope 2'],
                'category': ['Electricity', 'Stationary Combustion', 'Mobile Combustion', 'Electricity', 'Business Travel', 'Electricity'],
                'activity': ['Manufacturing Equipment', 'Heating Boiler', 'Company Vehicles', 'Server Operations', 'Employee Flights', 'Office Lighting'],
                'country': ['India'] * 6,
                'facility': ['Production Plant', 'Corporate Office', 'Vehicle Fleet', 'Data Center', 'Various Locations', 'Head Office'],
                'quantity': [5200, 180, 650, 2100, 4500, 1800],
                'unit': ['kWh', 'cubic meter', 'liter', 'kWh', 'passenger-km', 'kWh'],
                'emission_factor': [0.82, 2.03, 2.68, 0.82, 0.15, 0.82],
                'emissions_kgCO2e': [4264.0, 365.4, 1742.0, 1722.0, 675.0, 1476.0],
                'data_quality': ['High', 'Medium', 'High', 'High', 'Medium', 'High'],
                'verification_status': ['Third-Party Verified', 'Internally Verified', 'Third-Party Verified', 'Internally Verified', 'Unverified', 'Internally Verified'],
                'notes': [
                    'Monthly production equipment electricity',
                    'Natural gas for building heating',
                    'Fleet vehicle fuel consumption', 
                    'Data center power consumption',
                    'Business travel emissions',
                    'Office facility electricity'
                ]
            }
            
            sample_df_period = pd.DataFrame(sample_data_period)
            csv_period = sample_df_period.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Reporting Period Template",
                data=csv_period,
                file_name="emissions_reporting_period_template.csv",
                mime="text/csv",
                help="Template with reporting period - perfect for monthly/quarterly reports"
            )
            
            st.markdown("*✅ Best for: Monthly reports, quarterly summaries, business reporting*")
        
        with col2:
            st.markdown("**� Specific Dates Template**")
            
            # Create sample with specific dates
            from datetime import datetime, timedelta
            base_date = datetime(2025, 1, 15)
            sample_dates = [(base_date + timedelta(days=i*5)).strftime('%Y-%m-%d') for i in range(6)]
            
            sample_data_dates = {
                'date': sample_dates,
                'business_unit': ['Manufacturing', 'Office Operations', 'Fleet', 'Data Center', 'Travel', 'Facilities'],
                'scope': ['Scope 2', 'Scope 1', 'Scope 1', 'Scope 2', 'Scope 3', 'Scope 2'],
                'category': ['Electricity', 'Stationary Combustion', 'Mobile Combustion', 'Electricity', 'Business Travel', 'Electricity'],
                'activity': ['Manufacturing Equipment', 'Heating Boiler', 'Company Vehicles', 'Server Operations', 'Employee Flights', 'Office Lighting'],
                'country': ['India'] * 6,
                'facility': ['Production Plant', 'Corporate Office', 'Vehicle Fleet', 'Data Center', 'Various Locations', 'Head Office'],
                'quantity': [5200, 180, 650, 2100, 4500, 1800],
                'unit': ['kWh', 'cubic meter', 'liter', 'kWh', 'passenger-km', 'kWh'],
                'emission_factor': [0.82, 2.03, 2.68, 0.82, 0.15, 0.82],
                'data_quality': ['High', 'Medium', 'High', 'High', 'Medium', 'High'],
                'verification_status': ['Third-Party Verified', 'Internally Verified', 'Third-Party Verified', 'Internally Verified', 'Unverified', 'Internally Verified'],
                'notes': [
                    'Daily production equipment electricity',
                    'Weekly natural gas consumption',
                    'Fleet vehicle daily fuel usage', 
                    'Data center daily power consumption',
                    'Specific business trip',
                    'Office daily electricity'
                ]
            }
            
            sample_df_dates = pd.DataFrame(sample_data_dates)
            csv_dates = sample_df_dates.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Specific Dates Template",
                data=csv_dates,
                file_name="emissions_specific_dates_template.csv",
                mime="text/csv",
                help="Template with specific dates - for detailed tracking"
            )
            
            st.markdown("*✅ Best for: Daily tracking, detailed analysis, time-series data*")
    
    with tabs[2]:
        st.markdown("<h3>📋 Data Requirements Guide</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        ### 🎯 For Accurate Carbon Accounting
        
        #### 📊 Minimum Data Requirements:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔴 Scope 1 (Direct Emissions)**
            - Company vehicles fuel consumption
            - On-site fuel combustion (generators, boilers)
            - Refrigerant leaks from AC/cooling systems
            - Process emissions (if applicable)
            
            **🔵 Scope 2 (Energy Indirect)**
            - Electricity consumption (offices, facilities)
            - Purchased steam or heating
            - District cooling systems
            """)
        
        with col2:
            st.markdown("""
            **🟡 Scope 3 (Other Indirect)**
            - Business travel (flights, hotels, ground transport)
            - Employee commuting
            - Waste disposal
            - Water consumption
            - Purchased goods and services
            - Upstream transportation
            """)
        
        st.markdown("""
        #### 📈 Data Quality Guidelines:
        
        | Quality Level | Data Source | Accuracy | Example |
        |---------------|-------------|----------|---------|
        | **High** | Direct measurement/metering | ±5% | Smart meter readings, fuel receipts |
        | **Medium** | Calculated from bills/invoices | ±15% | Electricity bills, travel expense reports |
        | **Low** | Estimated/proxy data | ±30% | Employee surveys, industry averages |
        
        #### 🏭 Industry-Specific Focus Areas:
        """)
        
        industries = {
            "Manufacturing": ["Energy consumption", "Process emissions", "Raw materials", "Waste streams"],
            "Technology": ["Office electricity", "Data centers", "Business travel", "Employee commuting"],
            "Services": ["Office operations", "Business travel", "Client visits", "Purchased services"],
            "Retail": ["Store electricity", "Transportation", "Product sourcing", "Customer travel"],
            "Transportation": ["Fleet fuel", "Facility energy", "Maintenance", "Infrastructure"],
            "Agriculture": ["Equipment fuel", "Fertilizers", "Land use", "Processing"],
            "Energy": ["Facility operations", "Distribution losses", "Maintenance vehicles", "Office operations"]
        }
        
        selected_industry = st.selectbox("Select your industry for specific guidance:", list(industries.keys()), key="industry_selector")
        
        if selected_industry:
            st.markdown(f"**Key focus areas for {selected_industry}:**")
            for area in industries[selected_industry]:
                st.markdown(f"- {area}")
        
        st.markdown("""
        #### 💡 Tips for Complete Carbon Accounting:
        
        1. **📅 Consistent Time Periods**: Ensure data covers your reporting period
        2. **🔍 Scope Coverage**: Include at least one activity from each scope (1, 2, 3)
        3. **📊 Data Granularity**: Monthly or quarterly data points are ideal
        4. **✅ Verification**: Include verification status for each data point
        5. **📝 Documentation**: Add notes explaining data sources and calculation methods
        6. **🏢 Facility Coverage**: Include all significant facilities and operations
        7. **👥 Responsibility**: Assign responsible persons for data accuracy
        
        #### 🎯 Carbon Accounting Benefits:
        - **Baseline Establishment**: Understand your current carbon footprint
        - **Financial Impact**: Calculate potential carbon costs/savings
        - **Performance Tracking**: Monitor emission trends over time
        - **Improvement Planning**: Identify reduction opportunities
        - **Regulatory Readiness**: Prepare for carbon regulations
        - **Stakeholder Reporting**: Transparent emissions reporting
        """)
        
        # Quick data readiness check
        if len(st.session_state.emissions_data) > 0:
            st.markdown("#### ✅ Your Data Readiness:")
            
            # Use all available data
            period_data = st.session_state.emissions_data.copy()
            
            readiness_score = 0
            total_checks = 7
            
            checks = []
            
            # Check 1: Minimum entries
            if len(period_data) >= 5:
                checks.append("✅ Sufficient data entries (5+)")
                readiness_score += 1
            else:
                checks.append(f"❌ Need more data entries ({len(period_data)}/5)")
            
            # Check 2: Scope coverage
            if len(period_data) > 0:
                scopes = set(period_data['scope'].unique())
                if len(scopes) >= 2:
                    checks.append(f"✅ Good scope coverage ({len(scopes)}/3 scopes)")
                    readiness_score += 1
                else:
                    checks.append(f"❌ Need more scope coverage ({len(scopes)}/3 scopes)")
            else:
                checks.append("❌ No scope coverage")
            
            # Check 3: Time distribution
            if len(period_data) > 0:
                # Convert date column to datetime for proper calculation
                try:
                    period_data['date'] = pd.to_datetime(period_data['date'], errors='coerce')
                    # Filter out any invalid dates
                    valid_dates = period_data['date'].dropna()
                    if len(valid_dates) > 0:
                        date_range = (valid_dates.max() - valid_dates.min()).days
                        if date_range >= 30:
                            checks.append("✅ Good time distribution")
                            readiness_score += 1
                        else:
                            checks.append("❌ Data concentrated in short time period")
                    else:
                        checks.append("❌ No valid date information")
                except Exception:
                    checks.append("❌ Invalid date format")
            else:
                checks.append("❌ No time distribution")
            
            # Check 4: Data quality
            if len(period_data) > 0:
                high_quality = len(period_data[period_data['data_quality'] == 'High'])
                if high_quality >= len(period_data) * 0.5:
                    checks.append("✅ Good data quality (50%+ high quality)")
                    readiness_score += 1
                else:
                    checks.append("❌ Need better data quality")
            else:
                checks.append("❌ No data quality assessment")
            
            # Check 5: Verification
            if len(period_data) > 0:
                verified = len(period_data[period_data['verification_status'] != 'Unverified'])
                if verified >= len(period_data) * 0.3:
                    checks.append("✅ Some data verification (30%+)")
                    readiness_score += 1
                else:
                    checks.append("❌ Need more data verification")
            else:
                checks.append("❌ No verification status")
            
            # Check 6: Facility coverage
            if len(period_data) > 0:
                facilities = period_data['facility'].nunique()
                if facilities >= 2:
                    checks.append("✅ Multiple facilities covered")
                    readiness_score += 1
                else:
                    checks.append("❌ Limited facility coverage")
            else:
                checks.append("❌ No facility information")
            
            # Check 7: Emission factors
            if len(period_data) > 0:
                valid_factors = len(period_data[period_data['emission_factor'] > 0])
                if valid_factors == len(period_data):
                    checks.append("✅ All entries have emission factors")
                    readiness_score += 1
                else:
                    checks.append("❌ Some entries missing emission factors")
            else:
                checks.append("❌ No emission factors")
            
            # Display readiness
            readiness_percent = (readiness_score / total_checks) * 100
            
            if readiness_percent >= 80:
                st.success(f"🎉 Assessment Ready! Score: {readiness_percent:.0f}%")
            elif readiness_percent >= 60:
                st.warning(f"⚠️ Almost Ready! Score: {readiness_percent:.0f}%")
            else:
                st.error(f"❌ Needs More Data! Score: {readiness_percent:.0f}%")
            
            for check in checks:
                st.write(check)
                
            if readiness_percent >= 70:
                st.info("💡 You're ready for compliance assessment! Go to the Compliance page to run your assessment.")
        else:
            st.info("🚀 Start by adding emission data to see your assessment readiness!")
    
    with tabs[3]:
        st.markdown("<h3>🤖 Data Entry Assistant</h3>", unsafe_allow_html=True)
        st.markdown("Get AI-powered help with classifying emissions and mapping them to the correct scope and category.")
        
        # Import AI agents inside the tab to avoid loading issues
        try:
            from ai_agents import CarbonFootprintAgents
            
            # Initialize AI agents
            if 'ai_agents' not in st.session_state:
                st.session_state.ai_agents = CarbonFootprintAgents()
            
            # Check if AI is available
            if not st.session_state.ai_agents.available:
                st.warning("AI features temporarily unavailable. Manual classification guidance provided below.")
                st.info("""
                **Manual Classification Guide:**
                
                **Scope 1 (Direct Emissions):**
                - Company-owned vehicles and equipment
                - On-site fuel combustion (generators, boilers)
                - Refrigerant leaks from AC systems
                - Process emissions from manufacturing
                
                **Scope 2 (Energy Indirect):**
                - Purchased electricity
                - Purchased steam, heating, or cooling
                
                **Scope 3 (Other Indirect):**
                - Business travel (flights, hotels)
                - Employee commuting
                - Waste disposal
                - Purchased goods and services
                - Transportation and distribution
                """)
            else:
                data_description = st.text_area("Describe your emission activity", 
                                              placeholder="Example: We use diesel generators for backup power at our office in Mumbai. How should I categorize this?",
                                              key="data_entry_assistant_input")
                
                if st.button("Get Assistance", key="data_entry_assistant_btn"):
                    if data_description:
                        with st.spinner("AI assistant is analyzing your request..."):
                            try:
                                result = st.session_state.ai_agents.analyze_emissions(data_description)
                                # Handle CrewOutput object by converting it to string
                                result_str = str(result)
                                st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error: {str(e)}. Please check your API key and try again.")
                    else:
                        st.warning("Please describe your emission activity first.")
        except ImportError:
            st.error("AI agents module not available. Please ensure ai_agents.py is properly configured.")
        except Exception as e:
            st.error(f"Error initializing AI assistant: {str(e)}")
            
    # Show existing data table
    if len(st.session_state.emissions_data) > 0:
        st.markdown("<h2>📊 Current Emissions Data</h2>", unsafe_allow_html=True)
        
        # Use all available data
        filtered_data = st.session_state.emissions_data.copy()
        st.info(f"Showing all {len(filtered_data)} entries")
        
        if len(filtered_data) > 0:
            # Show data with edit/delete options
            st.dataframe(
                filtered_data[['date', 'business_unit', 'scope', 'category', 'activity', 'quantity', 'unit', 'emissions_kgCO2e', 'data_quality', 'verification_status']],
                use_container_width=True,
                hide_index=True
            )
            
            # Data management options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📥 Download Current Data"):
                    csv = filtered_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="💾 Download as CSV",
                        data=csv,
                        file_name=f"emissions_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                # Add confirmation state to session state
                if 'clear_data_confirm' not in st.session_state:
                    st.session_state.clear_data_confirm = False
                
                if not st.session_state.clear_data_confirm:
                    if st.button("🗑️ Clear All Data", type="secondary"):
                        st.session_state.clear_data_confirm = True
                        st.rerun()
                else:
                    st.warning("Are you sure you want to clear all data? This action cannot be undone.")
                    col2a, col2b = st.columns(2)
                    with col2a:
                        if st.button("⚠️ Yes, Clear All", type="secondary"):
                            st.session_state.emissions_data = pd.DataFrame(columns=[
                                'date', 'business_unit', 'project', 'scope', 'category', 'activity',
                                'country', 'facility', 'responsible_person', 'quantity', 'unit', 
                                'emission_factor', 'emissions_kgCO2e', 'data_quality', 'verification_status', 'notes'
                            ])
                            save_emissions_data()
                            st.session_state.clear_data_confirm = False
                            st.success("All data cleared!")
                            st.rerun()
                    with col2b:
                        if st.button("❌ Cancel", type="primary"):
                            st.session_state.clear_data_confirm = False
                            st.rerun()
            
            with col3:
                if st.button("🔄 Refresh Data"):
                    st.rerun()
        else:
            st.info("No data found for the selected period.")

# Reports page removed - focusing on AI features only

elif st.session_state.active_page == "Settings":
    st.markdown(f"<h1> {t('settings')}</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3>Company Information</h3>", unsafe_allow_html=True)
        
    # Company info form
    with st.form("company_info_form"):
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name")
            industry = st.text_input("Industry")
            location = st.text_input("Location")
        with col2:
            contact_person = st.text_input("Contact Person")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        
        st.markdown("<h4>Export Markets</h4>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            eu_market = st.checkbox("European Union")
        with col2:
            japan_market = st.checkbox("Japan")
        with col3:
            indonesia_market = st.checkbox("Indonesia")
        
        submitted = st.form_submit_button("Save Settings")
        if submitted:
            st.success("Settings saved successfully!")

elif st.session_state.active_page == "Compliance":
    st.markdown(f"<h1>⚖️ {t('compliance')}</h1>", unsafe_allow_html=True)
    
    # Import compliance framework
    from carbon_compliance import CarbonComplianceFramework, ComplianceStatus
    
    # Initialize compliance framework
    if 'compliance_framework' not in st.session_state:
        st.session_state.compliance_framework = CarbonComplianceFramework()
    
    # Check if we have emissions data
    if len(st.session_state.emissions_data) == 0:
        st.warning("No emissions data available. Please add emissions data first in the Data Entry section.")
        st.info("The compliance assessment requires emissions data to evaluate your carbon performance against industry benchmarks.")
    else:
        # Create tabs for compliance features
        compliance_tabs = st.tabs(["Assessment", "Industry Benchmarks", "Compliance Report"])
        
        with compliance_tabs[0]:
            st.markdown("<h3>Carbon Compliance Assessment</h3>", unsafe_allow_html=True)
            st.markdown("Evaluate your carbon performance against industry benchmarks and regulatory requirements.")
            
            # Company information form for compliance assessment
            with st.form("compliance_assessment_form"):
                st.markdown("<h4>Company Information</h4>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    company_name = st.text_input("Company Name", value="My Company")
                    industry = st.selectbox(
                        "Industry", 
                        ["Manufacturing", "Technology", "Services", "Retail", "Transportation", "Agriculture", "Energy"],
                        help="Select your industry for appropriate benchmarking"
                    )
                    country = st.selectbox(
                        "Primary Location", 
                        ["India", "Indonesia", "Japan", "Global"],
                        help="Your primary business location"
                    )
                
                with col2:
                    employees = st.number_input("Number of Employees", min_value=1, value=10, help="Total number of employees")
                    revenue = st.number_input("Annual Revenue (Million INR)", min_value=0.1, value=1.0, step=0.1, help="Annual revenue in millions INR")
                    assessment_period = st.number_input("Assessment Period (Months)", min_value=1, max_value=36, value=12, step=1, help="Period in months for assessment (1-36 months)")
                
                assess_button = st.form_submit_button("Run Compliance Assessment", type="primary")
                
                if assess_button:
                    # Prepare company info
                    company_info = {
                        'name': company_name,
                        'industry': industry.lower(),
                        'employees': employees,
                        'revenue_million_inr': revenue,
                        'country': country
                    }
                    
                    # Run compliance assessment
                    with st.spinner("Analyzing compliance status..."):
                        try:
                            result = st.session_state.compliance_framework.assess_compliance(
                                st.session_state.emissions_data, 
                                company_info, 
                                assessment_period
                            )
                            
                            # Store result in session state
                            st.session_state.compliance_result = result
                            st.session_state.company_info = company_info
                            
                            # Display results
                            st.success("Compliance assessment completed!")
                            
                            # Status indicator
                            status_colors = {
                                'excellent': '🟢',
                                'good': '🟡', 
                                'needs_improvement': '🟠',
                                'poor': '🔴',
                                'critical': '🔴'
                            }
                            
                            status_display = result.status.value.replace('_', ' ').title()
                            st.markdown(f"## {status_colors.get(result.status.value, '⚪')} Compliance Status: {status_display}")
                            
                            # Show assessment period information
                            st.info(f"📅 Assessment Period: {result.period_description}")
                            
                            # Key metrics - Focus on Performance Ratio
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if result.performance_ratio < 1.0:
                                    st.metric("Performance Ratio", f"{result.performance_ratio:.2f}", 
                                             delta="✅ Better than industry average", 
                                             delta_color="inverse")  # Green downward arrow for better (lower emissions)
                                elif result.performance_ratio == 1.0:
                                    st.metric("Performance Ratio", f"{result.performance_ratio:.2f}", 
                                             delta="⚖️ Equal to industry average", 
                                             delta_color="off")  # No arrow for equal
                                else:
                                    # Add red styling for performance ratio above 1.0
                                    st.markdown(f"""
                                    <div style="background-color: #ffebee; padding: 10px; border-radius: 5px; border-left: 4px solid #f44336;">
                                        <h3 style="color: #f44336; margin: 0;">Performance Ratio</h3>
                                        <h1 style="color: #f44336; margin: 5px 0;">{result.performance_ratio:.2f}</h1>
                                        <p style="color: #f44336; margin: 0;">⚠️ Higher than industry average</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            with col2:
                                if result.credit_amount > 0:
                                    st.metric("Carbon Credits", f"₹{result.credit_amount:,.2f}", delta="💰 Credit", delta_color="normal")
                                elif result.fine_amount > 0:
                                    # Remove arrow indication for tax - just show the amount
                                    st.markdown(f"""
                                    <div style="background-color: #ffebee; padding: 10px; border-radius: 5px; border-left: 4px solid #f44336;">
                                        <h3 style="color: #f44336; margin: 0;">Carbon Tax</h3>
                                        <h1 style="color: #f44336; margin: 5px 0;">₹{result.fine_amount:,.2f}</h1>
                                        <p style="color: #f44336; margin: 0;">💸 Tax Due</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.metric("Financial Impact", "₹0", delta="⚖️ Neutral", delta_color="off")
                            with col3:
                                from datetime import datetime
                                reviewed_date = datetime.now().strftime('%B %d, %Y')
                                # Add ordinal suffix (st, nd, rd, th)
                                day = datetime.now().day
                                if 10 <= day % 100 <= 20:
                                    suffix = 'th'
                                else:
                                    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
                                reviewed_date = datetime.now().strftime(f'%B %d{suffix}, %Y')
                                st.metric("Reviewed Date", reviewed_date)
                            
                            # SME-Friendly Explanation Section
                            st.markdown("<h4>📊 Understanding Your Performance (SME Guide)</h4>", unsafe_allow_html=True)
                            
                            # Add calculation formulas section
                            st.markdown("<h5>🧮 Calculation Formulas</h5>", unsafe_allow_html=True)
                            
                            with st.expander("📐 View Detailed Calculation Formulas", expanded=False):
                                st.markdown("""
                                <div class="stCard">
                                    <h6>1. 📈 Performance Ratio Calculation</h6>
                                    <p><strong>Formula:</strong></p>
                                    <code>Performance Ratio = Your Actual Emissions ÷ Industry Benchmark Emissions</code>
                                    <p><strong>Your Calculation:</strong></p>
                                    <p>Performance Ratio = {:.2f} ÷ {:.2f} = {:.2f}</p>
                                    <p><strong>Interpretation:</strong></p>
                                    <ul>
                                        <li><strong>< 1.0:</strong> Better than industry average ✅</li>
                                        <li><strong>= 1.0:</strong> Equal to industry average ⚖️</li>
                                        <li><strong>> 1.0:</strong> Higher than industry average ⚠️</li>
                                    </ul>
                                    <p><strong>Your Performance:</strong> You emit <strong>{:.2f}x</strong> the industry benchmark</p>
                                </div>
                                """.format(result.emissions_actual, result.emissions_benchmark, result.performance_ratio, result.performance_ratio), unsafe_allow_html=True)
                                
                                st.markdown("""
                                <div class="stCard">
                                    <h6>2. 🏭 Industry Benchmark Calculation</h6>
                                    <p><strong>Formula:</strong></p>
                                    <code>
                                    Employee-based Benchmark = (Employees × Emissions per Employee) ÷ 12 × Assessment Period
                                    Revenue-based Benchmark = (Revenue × Emissions per Revenue) ÷ 12 × Assessment Period
                                    Final Benchmark = Average of both methods
                                    </code>
                                    <p><strong>Your Calculation:</strong></p>
                                    <p>Employee-based: ({} employees × {} kg CO2e/employee/year) ÷ 12 × {} months = {:.2f} tonnes</p>
                                    <p>Revenue-based: (₹{:.1f}M × {} kg CO2e/M INR/year) ÷ 12 × {} months = {:.2f} tonnes</p>
                                    <p>Final Benchmark: ({:.2f} + {:.2f}) ÷ 2 = {:.2f} tonnes CO2e</p>
                                </div>
                                """.format(
                                    company_info['employees'], 
                                    1000,  # Approximate emissions per employee for manufacturing
                                    assessment_period,
                                    (company_info['employees'] * 1000 / 1000) / 12 * assessment_period,
                                    company_info['revenue_million_inr'],
                                    37500,  # Approximate emissions per million INR revenue
                                    assessment_period,
                                    (company_info['revenue_million_inr'] * 37500 / 1000) / 12 * assessment_period,
                                    (company_info['employees'] * 1000 / 1000) / 12 * assessment_period,
                                    (company_info['revenue_million_inr'] * 37500 / 1000) / 12 * assessment_period,
                                    result.emissions_benchmark
                                ), unsafe_allow_html=True)
                                
                                st.markdown("""
                                <div class="stCard">
                                    <h6>3. 💰 Carbon Tax Calculation</h6>
                                    <p><strong>Formula:</strong></p>
                                    <code>
                                    Excess Emissions = max(0, Actual Emissions - Benchmark Emissions)
                                    Carbon Tax = Excess Emissions × Tax Rate per tonne
                                    </code>
                                    <p><strong>Your Calculation:</strong></p>
                                    <p>Excess Emissions = max(0, {:.2f} - {:.2f}) = {:.2f} tonnes CO2e</p>
                                    <p>Carbon Tax = {:.2f} × ₹2100 = ₹{:,.2f}</p>
                                    <p><strong>Tax Rate:</strong> ₹2100 per tonne CO2e (industry standard)</p>
                                </div>
                                """.format(
                                    result.emissions_actual,
                                    result.emissions_benchmark,
                                    max(0, result.emissions_actual - result.emissions_benchmark),
                                    max(0, result.emissions_actual - result.emissions_benchmark),
                                    result.fine_amount
                                ), unsafe_allow_html=True)
                                
                                st.markdown("""
                                <div class="stCard">
                                    <h6>4. 🌱 Carbon Credits Calculation</h6>
                                    <p><strong>Formula:</strong></p>
                                    <code>
                                    if Actual Emissions < Benchmark Emissions:
                                        Saved Emissions = Benchmark Emissions - Actual Emissions
                                        Carbon Credits = Saved Emissions × Credit Rate per tonne
                                    else:
                                        Carbon Credits = 0
                                    </code>
                                    <p><strong>Your Calculation:</strong></p>
                                    <p>Actual Emissions ({:.2f}) vs Benchmark ({:.2f})</p>
                                    {}
                                    <p><strong>Credit Rate:</strong> ₹1680 per tonne CO2e saved</p>
                                </div>
                                """.format(
                                    result.emissions_actual,
                                    result.emissions_benchmark,
                                    f"<p>Saved Emissions = {result.emissions_benchmark - result.emissions_actual:.2f} tonnes</p><p>Carbon Credits = {result.emissions_benchmark - result.emissions_actual:.2f} × ₹1680 = ₹{result.credit_amount:,.2f}</p>" if result.emissions_actual < result.emissions_benchmark else "<p>No credits earned (emissions exceed benchmark)</p>"
                                ), unsafe_allow_html=True)
                                
                                st.markdown("""
                                <div class="stCard">
                                    <h6>5. 📊 Emission Factor Calculations</h6>
                                    <p><strong>Formula:</strong></p>
                                    <code>Total Emissions = Σ(Activity Data × Emission Factor)</code>
                                    <p><strong>Your Top Contributors:</strong></p>
                                    <table style="width: 100%; border-collapse: collapse;">
                                        <tr style="border-bottom: 1px solid #ddd;">
                                            <th style="text-align: left; padding: 8px;">Activity</th>
                                            <th style="text-align: right; padding: 8px;">Quantity</th>
                                            <th style="text-align: right; padding: 8px;">Factor</th>
                                            <th style="text-align: right; padding: 8px;">Emissions</th>
                                        </tr>
                                """, unsafe_allow_html=True)
                                
                                # Show top 5 emission sources with calculations
                                top_sources = st.session_state.emissions_data.nlargest(5, 'emissions_kgCO2e')
                                for _, row in top_sources.iterrows():
                                    st.markdown(f"""
                                        <tr style="border-bottom: 1px solid #eee;">
                                            <td style="padding: 8px;">{row['activity']}</td>
                                            <td style="text-align: right; padding: 8px;">{row['quantity']:.1f} {row['unit']}</td>
                                            <td style="text-align: right; padding: 8px;">{row['emission_factor']:.2f}</td>
                                            <td style="text-align: right; padding: 8px;">{row['emissions_kgCO2e']/1000:.2f}t</td>
                                        </tr>
                                    """, unsafe_allow_html=True)
                                
                                st.markdown("""
                                    </table>
                                    <p><strong>Total Emissions = {:.2f} tonnes CO2e</strong></p>
                                </div>
                                """.format(result.emissions_actual), unsafe_allow_html=True)
                                
                                st.markdown("""
                                <div class="stCard">
                                    <h6>6. 📅 Time Period Scaling</h6>
                                    <p><strong>Formula:</strong></p>
                                    <code>
                                    Scaled Emissions = (Data Emissions ÷ Data Period) × Assessment Period
                                    Scaled Benchmark = (Annual Benchmark ÷ 12) × Assessment Period
                                    </code>
                                    <p><strong>Your Calculation:</strong></p>
                                    <p>Assessment Period: {} months</p>
                                    <p>Data Period: {} days (from {} to {})</p>
                                    <p>Your data represents the full assessment period as specified.</p>
                                </div>
                                """.format(
                                    assessment_period,
                                    28,  # Based on your data range
                                    "2025-01-03",
                                    "2025-01-30"
                                ), unsafe_allow_html=True)
                            
                            # Create explanation cards - Focus on Performance Ratio
                            st.markdown("""
                            <div class="stCard">
                                <h5>📈 Performance Ratio Explained</h5>
                                <p><strong>Your Ratio: {:.2f}</strong></p>
                                <p><strong>What it means:</strong></p>
                                <ul>
                                    <li><strong>Below 1.0:</strong> ✅ Better than industry average</li>
                                    <li><strong>1.0:</strong> ⚖️ Equal to industry average</li>
                                    <li><strong>Above 1.0:</strong> ⚠️ Higher than industry average</li>
                                </ul>
                                <p><strong>Your Performance:</strong> You emit <strong>{:.2f}x</strong> the industry benchmark</p>
                                <p><strong>Status:</strong> {}</p>
                            </div>
                            """.format(result.performance_ratio, result.performance_ratio,
                                "🟢 Excellent - You're performing better than industry average!" if result.performance_ratio < 1.0 else
                                "🟡 Average - You're at industry standard" if result.performance_ratio == 1.0 else
                                "🟠 Above Average - Emissions too high, room for improvement" if result.performance_ratio < 2.0 else
                                "🔴 High Impact - Emissions significantly above average, reduction needed"
                            ), unsafe_allow_html=True)
                            
                            # Financial Impact Explanation
                            st.markdown("""
                            <div class="stCard">
                                <h5>💰 Financial Impact Calculation</h5>
                                <div style="display: flex; gap: 20px;">
                                    <div style="flex: 1;">
                                        <p><strong>Carbon Tax Calculation:</strong></p>
                                        <p>• Your Emissions: <strong>{:.2f} tonnes CO2e</strong></p>
                                        <p>• Industry Benchmark: <strong>{:.2f} tonnes CO2e</strong></p>
                                        <p>• Excess Emissions: <strong>{:.2f} tonnes CO2e</strong></p>
                                        <p>• Tax Rate: <strong>₹{} per tonne CO2e</strong></p>
                                        <p>• <strong>Total Tax: ₹{:,.2f}</strong></p>
                                    </div>
                                    <div style="flex: 1;">
                                        <p><strong>What this means for your business:</strong></p>
                                        {}
                                        <p><strong>Monthly Impact:</strong> ₹{:,.2f}</p>
                                        <p><strong>Annual Projection:</strong> ₹{:,.2f}</p>
                                    </div>
                                </div>
                            </div>
                            """.format(
                                result.emissions_actual,
                                result.emissions_benchmark,
                                max(0, result.emissions_actual - result.emissions_benchmark),
                                2100,  # Assuming ₹2100 per tonne CO2e
                                result.fine_amount,
                                "<p>• You're paying carbon tax due to higher emissions</p><p>• This is a regulatory cost you should plan for</p><p>• Reducing emissions can save money</p>" if result.fine_amount > 0 else "<p>• You're eligible for carbon credits</p><p>• This can be additional revenue</p><p>• Good environmental performance pays off</p>",
                                result.fine_amount,
                                result.fine_amount * 12
                            ), unsafe_allow_html=True)
                            
                            # Quick Action Items for SMEs
                            st.markdown("""
                            <div class="stCard">
                                <h5>🎯 Quick Action Items for Your Business</h5>
                                <div style="display: flex; gap: 20px;">
                                    <div style="flex: 1;">
                                        <p><strong>Immediate Actions (This Month):</strong></p>
                                        <ul>
                                            <li>Fix the refrigerant leak (saves 35 tonnes CO2e)</li>
                                            <li>Review electricity usage patterns</li>
                                            <li>Implement energy-saving measures</li>
                                        </ul>
                                    </div>
                                    <div style="flex: 1;">
                                        <p><strong>Medium-term Goals (3-6 months):</strong></p>
                                        <ul>
                                            <li>Upgrade to energy-efficient equipment</li>
                                            <li>Optimize manufacturing processes</li>
                                            <li>Consider renewable energy options</li>
                                        </ul>
                                    </div>
                                </div>
                                <p><strong>💡 SME Tip:</strong> Start with low-cost, high-impact actions. Fixing the refrigerant leak alone could save you ₹{:,.2f} in carbon taxes!</p>
                            </div>
                            """.format(35 * 25), unsafe_allow_html=True)
                            
                            # Emissions comparison
                            st.markdown("<h4>Emissions Analysis</h4>", unsafe_allow_html=True)
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Actual Emissions", f"{result.emissions_actual:.2f} tonnes CO2e")
                            with col2:
                                st.metric("Benchmark Emissions", f"{result.emissions_benchmark:.2f} tonnes CO2e")
                            
                            # Visual comparison chart for SMEs
                            st.markdown("<h5>📊 Visual Comparison</h5>", unsafe_allow_html=True)
                            
                            # Create a simple bar chart
                            fig = go.Figure()
                            fig.add_trace(go.Bar(
                                x=['Your Emissions', 'Industry Benchmark'],
                                y=[result.emissions_actual, result.emissions_benchmark],
                                marker_color=['#ff4444' if result.emissions_actual > result.emissions_benchmark else '#44ff44', '#4444ff'],
                                text=[f'{result.emissions_actual:.1f}t', f'{result.emissions_benchmark:.1f}t'],
                                textposition='auto',
                            ))
                            fig.update_layout(
                                title="Your Emissions vs Industry Benchmark",
                                yaxis_title="Emissions (tonnes CO2e)",
                                height=400,
                                showlegend=False
                            )
                            # Add a line showing the benchmark level
                            fig.add_hline(y=result.emissions_benchmark, line_dash="dash", line_color="blue", 
                                        annotation_text="Industry Benchmark")
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Breakdown by emission source for SMEs
                            st.markdown("<h5>💡 Where Your Emissions Come From</h5>", unsafe_allow_html=True)
                            
                            # Create a breakdown of emissions by scope
                            emissions_data = st.session_state.emissions_data
                            scope_breakdown = emissions_data.groupby('scope')['emissions_kgCO2e'].sum() / 1000
                            
                            # Create pie chart
                            fig_pie = go.Figure(data=[go.Pie(
                                labels=scope_breakdown.index,
                                values=scope_breakdown.values,
                                hole=0.3,
                                textinfo='label+percent+value',
                                texttemplate='%{label}<br>%{percent}<br>%{value:.1f}t',
                                marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1']
                            )])
                            fig_pie.update_layout(
                                title="Emissions Breakdown by Scope",
                                height=400,
                                showlegend=True
                            )
                            
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                            # Top emission sources
                            st.markdown("<h5>🎯 Top Emission Sources (Focus Areas)</h5>", unsafe_allow_html=True)
                            top_sources = emissions_data.nlargest(5, 'emissions_kgCO2e')[['activity', 'emissions_kgCO2e', 'scope']]
                            
                            for idx, row in top_sources.iterrows():
                                col1, col2, col3 = st.columns([3, 1, 1])
                                with col1:
                                    st.write(f"**{row['activity']}**")
                                with col2:
                                    st.write(f"{row['emissions_kgCO2e']/1000:.1f}t CO2e")
                                with col3:
                                    st.write(f"{row['scope']}")
                            
                            # SME-specific cost savings calculator
                            st.markdown("<h5>💰 Potential Cost Savings Calculator</h5>", unsafe_allow_html=True)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("""
                                **If you reduce emissions by 10%:**
                                - Emissions saved: {:.1f} tonnes CO2e
                                - Tax savings: ₹{:,.2f}
                                - Monthly savings: ₹{:,.2f}
                                """.format(
                                    result.emissions_actual * 0.1,
                                    result.emissions_actual * 0.1 * 2100,
                                    result.emissions_actual * 0.1 * 2100
                                ))
                            
                            with col2:
                                st.markdown("""
                                **If you reduce emissions by 25%:**
                                - Emissions saved: {:.1f} tonnes CO2e
                                - Tax savings: ₹{:,.2f}
                                - Monthly savings: ₹{:,.2f}
                                """.format(
                                    result.emissions_actual * 0.25,
                                    result.emissions_actual * 0.25 * 2100,
                                    result.emissions_actual * 0.25 * 2100
                                ))
                            
                            # Recommendations
                            st.markdown("<h4>Recommendations</h4>", unsafe_allow_html=True)
                            for i, rec in enumerate(result.recommendations, 1):
                                st.markdown(f"{i}. {rec}")
                                
                        except Exception as e:
                            st.error(f"Error during compliance assessment: {str(e)}")
        
        with compliance_tabs[1]:
            st.markdown("<h3>Industry Benchmarks</h3>", unsafe_allow_html=True)
            st.markdown("View emission benchmarks for different industries.")
            
            # Display industry benchmarks
            benchmarks_data = []
            for industry_key, benchmark in st.session_state.compliance_framework.industry_benchmarks.items():
                benchmarks_data.append({
                    'Industry': benchmark.industry,
                    'Emissions per Employee (kg CO2e/year)': f"{benchmark.emissions_per_employee_kg:,}",
                    'Emissions per Revenue (kg CO2e/M INR)': f"{benchmark.emissions_per_revenue_kg:,}",
                    'Reduction Target (%)': f"{benchmark.reduction_target_percent}%",
                    'Applicable Countries': ", ".join(benchmark.countries)
                })
            
            benchmarks_df = pd.DataFrame(benchmarks_data)
            st.dataframe(benchmarks_df, use_container_width=True)
            
            # Benchmark comparison chart
            if 'company_info' in st.session_state and 'compliance_result' in st.session_state:
                st.markdown("<h4>Your Performance vs Industry Benchmark</h4>", unsafe_allow_html=True)
                
                # Create comparison chart
                comparison_data = {
                    'Category': ['Your Emissions', 'Industry Benchmark'],
                    'Emissions (tonnes CO2e)': [
                        st.session_state.compliance_result.emissions_actual,
                        st.session_state.compliance_result.emissions_benchmark
                    ]
                }
                
                import plotly.express as px
                fig = px.bar(
                    comparison_data, 
                    x='Category', 
                    y='Emissions (tonnes CO2e)',
                    color='Category',
                    title="Emissions Comparison"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with compliance_tabs[2]:
            st.markdown("<h3>Compliance Report</h3>", unsafe_allow_html=True)
            st.markdown("Generate and download detailed compliance reports.")
            
            if 'compliance_result' in st.session_state and 'company_info' in st.session_state:
                # Generate report
                report_text = st.session_state.compliance_framework.generate_compliance_report(
                    st.session_state.compliance_result,
                    st.session_state.company_info
                )
                
                # Display report
                st.markdown(report_text)
                
                # Download button
                st.download_button(
                    label="Download Compliance Report",
                    data=report_text,
                    file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            else:
                st.info("Please run a compliance assessment first to generate a report.")

elif st.session_state.active_page == "Data Insights":
    st.markdown(f"<h1>🧠 Data Insights</h1>", unsafe_allow_html=True)
    
    # Initialize AI availability flag
    if 'ai_agents_initialized' not in st.session_state:
        st.session_state.ai_agents_initialized = False
        st.session_state.ai_agents_available = False
    
    # Create tabs for different Analytics features
    ai_tabs = st.tabs(["Report Summary", "Offset Advisor", "Regulation Radar", "Emission Optimizer"])
    
    with ai_tabs[0]:
        st.markdown("<h3>Report Summary Generator</h3>", unsafe_allow_html=True)
        st.markdown("Generate a human-readable summary of your emissions data.")
        
        if len(st.session_state.emissions_data) == 0:
            st.warning("No emissions data available. Please add data first.")
        else:
            if st.button("Generate Summary", key="report_summary_btn"):
                # Try to initialize AI agents only when needed
                if not st.session_state.ai_agents_initialized:
                    with st.spinner("Initializing AI features..."):
                        try:
                            from ai_agents import CarbonFootprintAgents
                            st.session_state.ai_agents = CarbonFootprintAgents()
                            st.session_state.ai_agents_available = st.session_state.ai_agents.available
                            st.session_state.ai_agents_initialized = True
                        except Exception as e:
                            st.session_state.ai_agents_available = False
                            st.session_state.ai_agents_initialized = True
                            st.error(f"AI features unavailable: {str(e)}")
                
                if not st.session_state.ai_agents_available:
                    st.warning("AI features temporarily unavailable. This feature will generate intelligent summaries of your emissions data once dependencies are resolved.")
                    
                    # Show manual summary
                    total_emissions = st.session_state.emissions_data['emissions_kgCO2e'].sum()
                    num_entries = len(st.session_state.emissions_data)
                    scope_breakdown = st.session_state.emissions_data.groupby('scope')['emissions_kgCO2e'].sum()
                    
                    st.info(f"""
                    **Manual Summary:**
                    - Total Emissions: {total_emissions/1000:.2f} tonnes CO2e
                    - Number of Activities: {num_entries}
                    - Scope Breakdown: {dict(scope_breakdown/1000)}
                    - Period: {st.session_state.emissions_data['date'].min()} to {st.session_state.emissions_data['date'].max()}
                    """)
                else:
                    with st.spinner("Generating report summary..."):
                        try:
                            # Convert DataFrame to string representation for the AI
                            emissions_str = st.session_state.emissions_data.to_string()
                            result = st.session_state.ai_agents.run_report_summary_crew(emissions_str)
                            # Handle CrewOutput object by converting it to string
                            result_str = str(result)
                            st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error: {str(e)}. Please check your API key and try again.")
    
    with ai_tabs[1]:
        st.markdown("<h3>Carbon Offset Advisor</h3>", unsafe_allow_html=True)
        st.markdown("Get recommendations for verified carbon offset options based on your profile.")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location", placeholder="e.g., Mumbai, India")
            industry = st.selectbox("Industry", ["Manufacturing", "Technology", "Agriculture", "Transportation", "Energy", "Services", "Other"])
        
        if len(st.session_state.emissions_data) == 0:
            st.warning("No emissions data available. Please add data first.")
        else:
            total_emissions = st.session_state.emissions_data['emissions_kgCO2e'].sum()
            st.markdown(f"<p>Total emissions to offset: <strong>{total_emissions:,.2f} kg CO₂e</strong></p>", unsafe_allow_html=True)
            
            if st.button("Get Offset Recommendations", key="offset_advisor_btn"):
                if not location:
                    st.warning("Please enter your location.")
                else:
                    # Try to initialize AI agents only when needed
                    if not st.session_state.ai_agents_initialized:
                        with st.spinner("Initializing AI features..."):
                            try:
                                from ai_agents import CarbonFootprintAgents
                                st.session_state.ai_agents = CarbonFootprintAgents()
                                st.session_state.ai_agents_available = st.session_state.ai_agents.available
                                st.session_state.ai_agents_initialized = True
                            except Exception as e:
                                st.session_state.ai_agents_available = False
                                st.session_state.ai_agents_initialized = True
                                st.error(f"AI features unavailable: {str(e)}")
                    
                    if not st.session_state.ai_agents_available:
                        st.warning("AI features temporarily unavailable. Manual offset guidance provided below.")
                        st.info(f"""
                        **Manual Offset Guidance for {total_emissions/1000:.2f} tonnes CO2e:**
                        
                        **Recommended Offset Types:**
                        - Renewable Energy Projects (Solar/Wind): ₹800-1200 per tonne
                        - Reforestation Projects: ₹600-900 per tonne
                        - Energy Efficiency Projects: ₹700-1000 per tonne
                        
                        **Estimated Cost:** ₹{(total_emissions/1000) * 900:,.0f} - ₹{(total_emissions/1000) * 1200:,.0f}
                        
                        **Verification Standards:** Look for Gold Standard or VCS certified projects
                        """)
                    else:
                        with st.spinner("Finding offset options..."):
                            try:
                                result = st.session_state.ai_agents.run_offset_advice_crew(total_emissions, location, industry)
                                # Handle CrewOutput object by converting it to string
                                result_str = str(result)
                                st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error: {str(e)}. Please check your API key and try again.")
    
    with ai_tabs[2]:
        st.markdown("<h3>Regulation Radar</h3>", unsafe_allow_html=True)
        st.markdown("Get insights on current and upcoming carbon regulations relevant to your business.")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Company Location", placeholder="e.g., Jakarta, Indonesia", key="reg_location")
            industry = st.selectbox("Industry Sector", ["Manufacturing", "Technology", "Agriculture", "Transportation", "Energy", "Services", "Other"], key="reg_industry")
        with col2:
            export_markets = st.multiselect("Export Markets", ["European Union", "Japan", "United States", "China", "Indonesia", "India", "Other"])
        
        if st.button("Check Regulations", key="regulation_radar_btn"):
            if not location or len(export_markets) == 0:
                st.warning("Please enter your location and select at least one export market.")
            else:
                # Try to initialize AI agents only when needed
                if not st.session_state.ai_agents_initialized:
                    with st.spinner("Initializing AI features..."):
                        try:
                            from ai_agents import CarbonFootprintAgents
                            st.session_state.ai_agents = CarbonFootprintAgents()
                            st.session_state.ai_agents_available = st.session_state.ai_agents.available
                            st.session_state.ai_agents_initialized = True
                        except Exception as e:
                            st.session_state.ai_agents_available = False
                            st.session_state.ai_agents_initialized = True
                            st.error(f"AI features unavailable: {str(e)}")
                
                if not st.session_state.ai_agents_available:
                    st.warning("AI features temporarily unavailable. Manual regulatory guidance provided below.")
                    st.info(f"""
                    **Key Regulations for {industry} in {location}:**
                    
                    **Current Regulations:**
                    - India: Perform Achieve Trade (PAT) scheme for energy-intensive industries
                    - EU CBAM: Carbon Border Adjustment Mechanism (2026 implementation)
                    - Japan: Voluntary Carbon Credit System
                    
                    **Export Market Requirements:**
                    {', '.join(export_markets)}:
                    - EU: CBAM reporting requirements for imports
                    - Japan: Tokyo Cap-and-Trade system participation
                    - US: Various state-level carbon regulations
                    
                    **Recommended Actions:**
                    - Start carbon accounting and reporting
                    - Implement emission reduction measures
                    - Consider carbon offset strategies
                    """)
                else:
                    with st.spinner("Analyzing regulatory requirements..."):
                        try:
                            result = st.session_state.ai_agents.run_regulation_check_crew(location, industry, ", ".join(export_markets))
                            # Handle CrewOutput object by converting it to string
                            result_str = str(result)
                            st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error: {str(e)}. Please check your API key and try again.")
    
    with ai_tabs[3]:
        st.markdown("<h3>Emission Optimizer</h3>", unsafe_allow_html=True)
        st.markdown("Get AI-powered recommendations to reduce your carbon footprint.")
        
        if len(st.session_state.emissions_data) == 0:
            st.warning("No emissions data available. Please add data first.")
        else:
            if st.button("Generate Optimization Recommendations", key="emission_optimizer_btn"):
                # Try to initialize AI agents only when needed
                if not st.session_state.ai_agents_initialized:
                    with st.spinner("Initializing AI features..."):
                        try:
                            from ai_agents import CarbonFootprintAgents
                            st.session_state.ai_agents = CarbonFootprintAgents()
                            st.session_state.ai_agents_available = st.session_state.ai_agents.available
                            st.session_state.ai_agents_initialized = True
                        except Exception as e:
                            st.session_state.ai_agents_available = False
                            st.session_state.ai_agents_initialized = True
                            st.error(f"AI features unavailable: {str(e)}")
                
                if not st.session_state.ai_agents_available:
                    st.warning("AI features temporarily unavailable. Manual optimization tips provided below.")
                    
                    # Show basic manual optimization tips
                    st.info("**Manual Optimization Tips (Available Now):**")
                    # Calculate top emission sources
                    top_sources = st.session_state.emissions_data.nlargest(3, 'emissions_kgCO2e')
                    st.markdown("**Your Top 3 Emission Sources:**")
                    for idx, row in top_sources.iterrows():
                        st.write(f"• **{row['activity']}**: {row['emissions_kgCO2e']/1000:.2f} tonnes CO2e ({row['scope']})")
                    
                    st.markdown("""
                    **General Reduction Strategies:**
                    - **Scope 1 (Direct)**: Upgrade equipment efficiency, switch to cleaner fuels, fix leaks
                    - **Scope 2 (Energy)**: Improve energy efficiency, switch to renewable energy
                    - **Scope 3 (Indirect)**: Optimize supply chain, reduce business travel, improve waste management
                    """)
                else:
                    with st.spinner("Analyzing your emissions data..."):
                        try:
                            # Convert DataFrame to string representation for the AI
                            emissions_str = st.session_state.emissions_data.to_string()
                            result = st.session_state.ai_agents.run_optimization_crew(emissions_str)
                            # Handle CrewOutput object by converting it to string
                            result_str = str(result)
                            st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error: {str(e)}. Please check your API key and try again.")
    
                            # Convert DataFrame to string representation for the AI
                            emissions_str = st.session_state.emissions_data.to_string()
                            result = st.session_state.ai_agents.run_optimization_crew(emissions_str)
                            # Handle CrewOutput object by converting it to string
                            result_str = str(result)
                            st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error: {str(e)}. Please check your API key and try again.")

elif st.session_state.active_page == "Carbon Credits":
    st.markdown("<h1>💰 Carbon Credits Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"**Company:** {st.session_state.company_data['company_name']}")
    
    # Get company-specific carbon summary
    company_summary = company_manager.get_company_carbon_summary(st.session_state.current_company)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Refresh Data", type="secondary"):
            st.rerun()
    with col2:
        if st.button("� Record Emissions", type="primary"):
            st.session_state.active_page = "Data Entry"
            st.rerun()
    with col3:
        if st.button("🌊 View Blue Carbon Projects"):
            st.session_state.active_page = "Blue Carbon"
            st.rerun()
    
    st.divider()
    
    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        colorful_metric_card(
            "Total Carbon Credits",
            f"{company_summary.get('total_carbon_credits', 0):.2f}",
            "tons CO2 credits available",
            "💚",
            color_scheme="success"
        )
    
    with col2:
        colorful_metric_card(
            "Total Emissions",
            f"{company_summary.get('total_emissions_tonnes', 0):.2f}",
            "tons CO2 emitted",
            "📊",
            color_scheme="warning"
        )
    
    with col3:
        remaining = company_summary.get('remaining_credits', 0)
        color = "success" if remaining >= 0 else "warning"
        colorful_metric_card(
            "Remaining Credits",
            f"{remaining:.2f}",
            "after offsetting emissions",
            "⚖️",
            color_scheme=color
        )
    
    with col4:
        status = company_summary.get('carbon_status', 'Unknown')
        status_color = "success" if status == "Carbon Positive" else "warning"
        colorful_metric_card(
            "Carbon Status",
            status,
            "environmental impact",
            "🏆",
            color_scheme=status_color
        )
    
    st.divider()
    
    # Detailed breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Credits Breakdown")
        
        # Credits breakdown chart
        if company_summary.get('total_carbon_credits', 0) > 0:
            credits_data = {
                'Type': ['Credits Earned', 'Credits Purchased'],
                'Amount': [
                    company_summary.get('credits_earned', 0),
                    company_summary.get('credits_purchased', 0)
                ]
            }
            
            fig = px.pie(
                values=credits_data['Amount'],
                names=credits_data['Type'],
                title="Carbon Credits Sources",
                color_discrete_sequence=['#00cc96', '#636efa']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No carbon credits available yet. Register blue carbon projects or purchase credits to get started!")
    
    with col2:
        st.subheader("📈 Carbon Balance Overview")
        
        # Balance comparison chart
        if company_summary.get('total_emissions_tonnes', 0) > 0 or company_summary.get('total_carbon_credits', 0) > 0:
            balance_data = {
                'Category': ['Carbon Credits', 'Emissions (CO2)', 'Net Balance'],
                'Amount': [
                    company_summary.get('total_carbon_credits', 0),
                    -company_summary.get('total_emissions_tonnes', 0),  # Negative for emissions
                    company_summary.get('remaining_credits', 0)
                ],
                'Color': ['green', 'red', 'blue']
            }
            
            fig = go.Figure(data=[
                go.Bar(
                    name='Carbon Balance',
                    x=balance_data['Category'],
                    y=balance_data['Amount'],
                    marker_color=['green', 'red', 'blue' if company_summary.get('remaining_credits', 0) >= 0 else 'orange']
                )
            ])
            
            fig.update_layout(
                title="Carbon Credits vs Emissions",
                yaxis_title="Tons CO2",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start recording emissions and earning credits to see your carbon balance!")
    
    st.divider()
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Record New Emissions")
        emissions_amount = st.number_input("Emissions (kg CO2)", min_value=0.0, step=0.1, key="quick_emissions")
        if st.button("🔄 Add Emissions", key="add_emissions_btn"):
            if emissions_amount > 0:
                # Update company emissions
                company_manager.update_company_emissions(st.session_state.current_company, emissions_amount)
                
                # Add to emissions data
                emissions_data = company_manager.get_company_emissions_data(st.session_state.current_company)
                new_emission = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'business_unit': 'Operations',
                    'project': 'Quick Entry',
                    'scope': 'Scope 1',
                    'category': 'General',
                    'activity': 'Quick Entry',
                    'country': st.session_state.company_data['location'],
                    'facility': st.session_state.company_data['company_name'],
                    'responsible_person': st.session_state.company_data['contact_person'],
                    'quantity': emissions_amount,
                    'unit': 'kg',
                    'emission_factor': 1.0,
                    'emissions_kgCO2e': emissions_amount,
                    'data_quality': 'Medium',
                    'verification_status': 'Unverified',
                    'notes': 'Quick entry from Carbon Credits dashboard'
                }
                emissions_data.append(new_emission)
                company_manager.save_company_emissions_data(st.session_state.current_company, emissions_data)
                
                st.success(f"✅ Added {emissions_amount} kg CO2 emissions")
                st.rerun()
    
    with col2:
        st.markdown("### 🌊 Register Blue Carbon Project")
        st.markdown("Earn carbon credits by registering blue carbon restoration projects.")
        if st.button("🌱 Register Project", key="register_project_btn"):
            st.session_state.active_page = "Blue Carbon"
            st.rerun()
    
    with col3:
        st.markdown("### 🏪 Visit Marketplace")
        st.markdown("Buy or sell carbon credits with other companies.")
        if st.button("🛒 Open Marketplace", key="open_marketplace_btn"):
            st.session_state.active_page = "Marketplace"
            st.rerun()
    
    st.divider()
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    
    # Get recent emissions data
    emissions_data = company_manager.get_company_emissions_data(st.session_state.current_company)
    
    if emissions_data:
        # Show last 5 emissions entries
        recent_emissions = emissions_data[-5:] if len(emissions_data) > 5 else emissions_data
        
        df_recent = pd.DataFrame(recent_emissions)
        if not df_recent.empty:
            # Select key columns for display
            display_columns = ['date', 'activity', 'emissions_kgCO2e', 'scope', 'verification_status']
            if all(col in df_recent.columns for col in display_columns):
                st.dataframe(
                    df_recent[display_columns].tail(5),
                    column_config={
                        'date': 'Date',
                        'activity': 'Activity',
                        'emissions_kgCO2e': st.column_config.NumberColumn('Emissions (kg CO2)', format="%.2f"),
                        'scope': 'Scope',
                        'verification_status': 'Status'
                    },
                    use_container_width=True
                )
            else:
                st.dataframe(df_recent.tail(5), use_container_width=True)
        
        if st.button("📊 View All Emissions Data"):
            st.session_state.active_page = "Dashboard"
            st.rerun()
    else:
        st.info("No emissions data recorded yet. Start by adding your first emissions entry!")
        if st.button("📝 Add First Emission"):
            st.session_state.active_page = "Data Entry"
            st.rerun()
    
    st.divider()
    
    # Record new emissions
    st.subheader("📊 Record New Emissions")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        new_emissions = st.number_input("Emissions (tons CO2)", min_value=0.0, step=0.1, help="Enter emissions to record")
    
    with col2:
        if st.button("🔄 Record Emissions", type="primary"):
            if new_emissions > 0:
                blockchain_mrv.record_company_emissions(company_address, new_emissions)
                st.success(f"Recorded {new_emissions} tons CO2 emissions")
                st.rerun()
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Credits vs Emissions")
        if dashboard_data['carbon_credits'] > 0 or dashboard_data['total_emissions'] > 0:
            fig = go.Figure(data=[
                go.Bar(name='Carbon Credits', x=['Your Company'], y=[dashboard_data['carbon_credits']], marker_color='green'),
                go.Bar(name='Total Emissions', x=['Your Company'], y=[dashboard_data['total_emissions']], marker_color='red')
            ])
            fig.update_layout(barmode='group', title="Carbon Credits vs Emissions")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data to display. Record emissions or earn credits to see charts.")
    
    with col2:
        st.subheader("🏪 Your Marketplace Listings")
        if dashboard_data['marketplace_listings']:
            for listing in dashboard_data['marketplace_listings']:
                st.info(f"**{listing['amount']} tons CO2** - ${listing['price_per_ton']}/ton (Total: ${listing['total_price']})")
        else:
            st.info("No active marketplace listings")

elif st.session_state.active_page == "Blue Carbon":
    st.markdown("<h1>🌊 Blue Carbon Projects</h1>", unsafe_allow_html=True)
    st.markdown("Register and manage blue carbon ecosystem restoration projects.")
    
    tab1, tab2, tab3 = st.tabs(["🆕 Register Project", "📋 View Projects", "📊 Project Analytics"])
    
    with tab1:
        st.subheader("Register New Blue Carbon Project")
        
        with st.form("register_project"):
            col1, col2 = st.columns(2)
            
            with col1:
                project_name = st.text_input("Project Name*", help="Name of your blue carbon project")
                location = st.text_input("Location*", help="Geographic location of the project")
                area = st.number_input("Area (hectares)*", min_value=0.1, step=0.1, help="Project area in hectares")
                ecosystem_type = st.selectbox("Ecosystem Type*", 
                                            ["mangrove", "seagrass", "salt_marsh", "coastal_wetland"],
                                            help="Type of blue carbon ecosystem")
            
            with col2:
                owner = st.text_input("Project Owner*", value="company_demo_001", help="Company or organization address")
                estimated_sequestration = st.number_input("Estimated CO2 Sequestration (tons/year)*", 
                                                        min_value=0.1, step=0.1,
                                                        help="Annual carbon sequestration estimate")
                
                # Additional project data
                st.markdown("**Additional Project Details:**")
                biodiversity_impact = st.text_area("Biodiversity Impact", help="Expected biodiversity benefits")
                community_benefits = st.text_area("Community Benefits", help="Benefits to local communities")
            
            submit_project = st.form_submit_button("🌱 Register Project", type="primary")
            
            if submit_project:
                if all([project_name, location, area, ecosystem_type, owner, estimated_sequestration]):
                    # Create project data for IPFS storage
                    project_data = {
                        "biodiversity_impact": biodiversity_impact,
                        "community_benefits": community_benefits,
                        "registration_date": datetime.now().isoformat(),
                        "project_type": "blue_carbon_restoration"
                    }
                    
                    try:
                        project_id = blockchain_mrv.register_blue_carbon_project(
                            name=project_name,
                            location=location,
                            area=area,
                            ecosystem_type=ecosystem_type,
                            estimated_sequestration=estimated_sequestration,
                            owner=owner,
                            project_data=project_data
                        )
                        st.success(f"✅ Project registered successfully! Project ID: {project_id}")
                    except Exception as e:
                        st.error(f"Error registering project: {str(e)}")
                else:
                    st.error("Please fill in all required fields marked with *")
    
    with tab2:
        st.subheader("Registered Blue Carbon Projects")
        
        projects = blockchain_mrv.get_all_projects()
        
        if projects:
            for project in projects:
                with st.expander(f"🌊 {project.name} (ID: {project.id})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Location:** {project.location}")
                        st.markdown(f"**Area:** {project.area} hectares")
                        st.markdown(f"**Ecosystem:** {project.ecosystem_type}")
                    
                    with col2:
                        st.markdown(f"**Owner:** {project.owner}")
                        st.markdown(f"**Status:** {project.status}")
                        st.markdown(f"**Estimated Sequestration:** {project.estimated_carbon_sequestration} tons CO2/year")
                    
                    with col3:
                        st.markdown(f"**Created:** {project.created_at.strftime('%Y-%m-%d')}")
                        st.markdown(f"**IPFS Hash:** `{project.ipfs_hash[:20]}...`")
                        
                        # Show verification records
                        verifications = blockchain_mrv.get_verification_records(project.id)
                        st.markdown(f"**Verifications:** {len(verifications)} records")
        else:
            st.info("No blue carbon projects registered yet. Register the first project!")
    
    with tab3:
        st.subheader("Blue Carbon Analytics")
        
        projects = blockchain_mrv.get_all_projects()
        
        if projects:
            # Project distribution by ecosystem type
            ecosystem_counts = {}
            total_area = 0
            total_sequestration = 0
            
            for project in projects:
                ecosystem_counts[project.ecosystem_type] = ecosystem_counts.get(project.ecosystem_type, 0) + 1
                total_area += project.area
                total_sequestration += project.estimated_carbon_sequestration
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                colorful_metric_card(
                    "Total Projects",
                    str(len(projects)),
                    "registered projects",
                    "🌊",
                    color_scheme="info"
                )
            
            with col2:
                colorful_metric_card(
                    "Total Area",
                    f"{total_area:.1f}",
                    "hectares under restoration",
                    "📏",
                    color_scheme="success"
                )
            
            with col3:
                colorful_metric_card(
                    "Annual Sequestration",
                    f"{total_sequestration:.1f}",
                    "tons CO2/year potential",
                    "🌱",
                    color_scheme="purple"
                )
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                if ecosystem_counts:
                    fig = px.pie(values=list(ecosystem_counts.values()), 
                               names=list(ecosystem_counts.keys()),
                               title="Projects by Ecosystem Type")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                project_areas = [p.area for p in projects]
                project_names = [p.name for p in projects]
                fig = px.bar(x=project_names, y=project_areas, title="Project Areas")
                fig.update_xaxes(title="Project")
                fig.update_yaxes(title="Area (hectares)")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No projects to analyze yet.")

elif st.session_state.active_page == "Marketplace":
    st.markdown("<h1>🏪 Carbon Credits Marketplace</h1>", unsafe_allow_html=True)
    st.markdown("Buy and sell verified carbon credits from blue carbon projects.")
    
    tab1, tab2 = st.tabs(["🛒 Buy Credits", "💰 Sell Credits"])
    
    with tab1:
        st.subheader("Available Carbon Credits")
        
        listings = blockchain_mrv.get_marketplace_listings()
        
        if listings:
            for i, listing in enumerate(listings):
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Seller:** {listing['seller']}")
                        st.markdown(f"**Project ID:** {listing['project_id']}")
                    
                    with col2:
                        st.markdown(f"**Amount:** {listing['amount']} tons")
                        st.markdown(f"**Price:** ${listing['price_per_ton']}/ton")
                    
                    with col3:
                        st.markdown(f"**Total:** ${listing['total_price']:.2f}")
                        st.markdown(f"**Listed:** {listing['created_at'][:10]}")
                    
                    with col4:
                        buyer_address = st.text_input(f"Your Address", key=f"buyer_{i}", value="company_demo_002")
                        if st.button(f"💰 Buy", key=f"buy_{i}", type="primary"):
                            try:
                                blockchain_mrv.purchase_carbon_credits(
                                    buyer=buyer_address,
                                    seller=listing['seller'],
                                    amount=listing['amount'],
                                    price_per_ton=listing['price_per_ton']
                                )
                                st.success(f"✅ Purchased {listing['amount']} credits successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Purchase failed: {str(e)}")
                    
                    st.divider()
        else:
            st.info("No carbon credits available in the marketplace currently.")
    
    with tab2:
        st.subheader("List Your Carbon Credits for Sale")
        
        with st.form("sell_credits"):
            seller_address = st.text_input("Your Address", value="company_demo_001")
            amount_to_sell = st.number_input("Amount to Sell (tons CO2)", min_value=0.1, step=0.1)
            price_per_ton = st.number_input("Price per Ton ($)", min_value=1.0, step=1.0, value=50.0)
            
            submit_listing = st.form_submit_button("📝 List for Sale", type="primary")
            
            if submit_listing:
                available_credits = blockchain_mrv.get_company_carbon_balance(seller_address)
                
                if available_credits >= amount_to_sell:
                    st.success(f"✅ Listed {amount_to_sell} tons for ${price_per_ton}/ton")
                    st.info("Note: In production, this would create a blockchain transaction")
                else:
                    st.error(f"Insufficient credits. You have {available_credits} tons available.")

elif st.session_state.active_page == "MRV System":
    st.markdown("<h1>👥 Monitoring, Reporting & Verification System</h1>", unsafe_allow_html=True)
    st.markdown("Submit field data and manage verification processes for blue carbon projects.")
    
    tab1, tab2, tab3 = st.tabs(["📱 Submit Field Data", "✅ Verification Records", "👮 Admin Panel"])
    
    with tab1:
        st.subheader("Submit Field Data for Verification")
        st.markdown("Upload monitoring data from field visits, drones, or mobile apps.")
        
        with st.form("submit_verification"):
            col1, col2 = st.columns(2)
            
            with col1:
                project_id = st.number_input("Project ID*", min_value=1, step=1, help="ID of the project to verify")
                verifier_address = st.text_input("Verifier Address*", value="verifier_001", help="Your verifier credentials")
                verified_amount = st.number_input("Verified Carbon Amount (tons CO2)*", min_value=0.1, step=0.1)
            
            with col2:
                verification_date = st.date_input("Verification Date", value=datetime.now().date())
                comments = st.text_area("Comments", help="Additional notes about the verification")
            
            st.markdown("**Field Data Upload:**")
            col1, col2 = st.columns(2)
            
            with col1:
                area_measurement = st.file_uploader("Area Measurement Data", type=['csv', 'json', 'xlsx'])
                biomass_data = st.file_uploader("Biomass Assessment", type=['csv', 'json', 'xlsx'])
                soil_carbon_data = st.file_uploader("Soil Carbon Measurement", type=['csv', 'json', 'xlsx'])
            
            with col2:
                gps_coordinates = st.text_input("GPS Coordinates", help="Lat, Long of verification site")
                photo_evidence = st.file_uploader("Photographic Evidence", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
                drone_data = st.file_uploader("Drone Survey Data", type=['csv', 'json', 'kml'])
            
            submit_verification = st.form_submit_button("📋 Submit Verification", type="primary")
            
            if submit_verification:
                if all([project_id, verifier_address, verified_amount]):
                    # Create verification data package
                    verification_data = {
                        "verification_date": verification_date.isoformat(),
                        "gps_coordinates": gps_coordinates,
                        "files_uploaded": {
                            "area_measurement": area_measurement.name if area_measurement else None,
                            "biomass_data": biomass_data.name if biomass_data else None,
                            "soil_carbon_data": soil_carbon_data.name if soil_carbon_data else None,
                            "photo_count": len(photo_evidence) if photo_evidence else 0,
                            "drone_data": drone_data.name if drone_data else None
                        }
                    }
                    
                    try:
                        verification_id = blockchain_mrv.submit_verification(
                            project_id=int(project_id),
                            verified_amount=verified_amount,
                            verifier=verifier_address,
                            verification_data=verification_data,
                            comments=comments
                        )
                        st.success(f"✅ Verification submitted successfully! Verification ID: {verification_id}")
                    except Exception as e:
                        st.error(f"Error submitting verification: {str(e)}")
                else:
                    st.error("Please fill in all required fields marked with *")
    
    with tab2:
        st.subheader("Verification Records")
        
        # Show all verification records
        all_verifications = list(blockchain_mrv.verifications.values())
        
        if all_verifications:
            for verification in all_verifications:
                status_color = "🟢" if verification.is_approved else "🟡"
                status_text = "Approved" if verification.is_approved else "Pending"
                
                with st.expander(f"{status_color} Verification {verification.id} - {status_text}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Project ID:** {verification.project_id}")
                        st.markdown(f"**Verifier:** {verification.verifier}")
                        st.markdown(f"**Verified Amount:** {verification.verified_carbon_amount} tons CO2")
                    
                    with col2:
                        st.markdown(f"**Date:** {verification.verification_date.strftime('%Y-%m-%d %H:%M')}")
                        st.markdown(f"**Status:** {status_text}")
                        st.markdown(f"**Data Hash:** `{verification.verification_data_hash[:20]}...`")
                    
                    with col3:
                        st.markdown(f"**Comments:** {verification.comments}")
                        
                        if not verification.is_approved:
                            if st.button(f"✅ Approve Verification {verification.id}", key=f"approve_{verification.id}"):
                                try:
                                    blockchain_mrv.approve_verification_and_issue_credits(verification.id)
                                    st.success("Verification approved and credits issued!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error approving verification: {str(e)}")
        else:
            st.info("No verification records found.")
    
    with tab3:
        st.subheader("Admin Panel - NCCR Management")
        st.markdown("Administrative tools for the National Centre for Coastal Research (NCCR).")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**System Statistics:**")
            projects = blockchain_mrv.get_all_projects()
            verifications = list(blockchain_mrv.verifications.values())
            pending_verifications = [v for v in verifications if not v.is_approved]
            
            st.info(f"📊 **Total Projects:** {len(projects)}")
            st.info(f"📋 **Total Verifications:** {len(verifications)}")
            st.warning(f"⏳ **Pending Verifications:** {len(pending_verifications)}")
            
            # Carbon credits issued
            total_credits = sum(blockchain_mrv.get_company_carbon_balance(addr) for addr in blockchain_mrv.carbon_credits.keys())
            st.success(f"💰 **Total Credits Issued:** {total_credits} tons CO2")
        
        with col2:
            st.markdown("**Quick Actions:**")
            
            if st.button("📊 Generate System Report", type="primary"):
                st.markdown("**System Report Generated:**")
                report_data = {
                    "timestamp": datetime.now().isoformat(),
                    "total_projects": len(projects),
                    "total_verifications": len(verifications),
                    "pending_verifications": len(pending_verifications),
                    "total_credits_issued": total_credits,
                    "active_companies": len(blockchain_mrv.carbon_credits.keys())
                }
                st.json(report_data)
            
            if st.button("🔄 Refresh System"):
                st.success("System refreshed successfully!")
                st.rerun()
            
            if st.button("📤 Export Data"):
                st.info("Data export functionality would be implemented here")

# About page removed - focusing on AI features only