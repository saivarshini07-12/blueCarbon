"""
Data handler for YourCarbonFootprint application.
Manages data import, export, and processing.
"""

import pandas as pd
import json
import os
from datetime import datetime
import csv
from io import StringIO
from fpdf import FPDF  # fpdf2 package
import matplotlib.pyplot as plt
import seaborn as sns
from emission_factors import get_emission_factor, get_categories, get_activities

# Constants
DATA_DIR = "data"
EMISSIONS_FILE = os.path.join(DATA_DIR, "emissions.json")
COMPANY_INFO_FILE = os.path.join(DATA_DIR, "company_info.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

class DataHandler:
    def __init__(self):
        """Initialize the DataHandler class."""
        self.load_emissions_data()
        self.load_company_info()
    
    def load_emissions_data(self):
        """Load emissions data from file."""
        if os.path.exists(EMISSIONS_FILE):
            with open(EMISSIONS_FILE, 'r') as f:
                try:
                    self.emissions_data = pd.DataFrame(json.load(f))
                    # Convert date strings to datetime objects
                    if 'date' in self.emissions_data.columns:
                        self.emissions_data['date'] = pd.to_datetime(self.emissions_data['date'])
                except json.JSONDecodeError:
                    self.create_empty_emissions_data()
        else:
            self.create_empty_emissions_data()
    
    def create_empty_emissions_data(self):
        """Create empty emissions dataframe."""
        self.emissions_data = pd.DataFrame(columns=[
            'date', 'business_unit', 'project', 'scope', 'category', 'activity', 
            'country', 'facility', 'responsible_person', 'quantity', 'unit', 
            'emission_factor', 'emissions_kgCO2e', 'data_quality', 
            'verification_status', 'notes'
        ])
    
    def load_company_info(self):
        """Load company information from file."""
        if os.path.exists(COMPANY_INFO_FILE):
            with open(COMPANY_INFO_FILE, 'r') as f:
                try:
                    self.company_info = json.load(f)
                except json.JSONDecodeError:
                    self.create_empty_company_info()
        else:
            self.create_empty_company_info()
    
    def create_empty_company_info(self):
        """Create empty company information."""
        self.company_info = {
            "name": "",
            "industry": "",
            "location": "",
            "export_markets": [],
            "contact_person": "",
            "email": "",
            "phone": "",
            "address": "",
            "registration_number": "",
            "reporting_year": datetime.now().year
        }
    
    def save_emissions_data(self):
        """Save emissions data to file."""
        # Convert datetime objects to strings
        data_to_save = self.emissions_data.copy()
        if 'date' in data_to_save.columns:
            data_to_save['date'] = data_to_save['date'].dt.strftime('%Y-%m-%d')
        
        with open(EMISSIONS_FILE, 'w') as f:
            json.dump(data_to_save.to_dict('records'), f, indent=2)
    
    def save_company_info(self):
        """Save company information to file."""
        with open(COMPANY_INFO_FILE, 'w') as f:
            json.dump(self.company_info, f, indent=2)
    
    def add_emission_entry(self, date, business_unit, project, scope, category, activity, country, facility, responsible_person, quantity, unit, emission_factor, data_quality, verification_status, notes=""):
        """
        Add a new emission entry.
        
        Args:
            date (datetime): Date of the emission
            business_unit (str): Business unit responsible
            project (str): Project associated with emission
            scope (str): Emission scope (Scope 1, Scope 2, or Scope 3)
            category (str): Emission category
            activity (str): Specific activity
            country (str): Country location
            facility (str): Facility/location
            responsible_person (str): Person responsible
            quantity (float): Quantity of activity
            unit (str): Unit of measurement
            emission_factor (float): Emission factor
            data_quality (str): Data quality indicator
            verification_status (str): Verification status
            notes (str, optional): Additional notes
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Calculate emissions
            emissions_kgCO2e = float(quantity) * float(emission_factor)
            
            # Create new entry
            new_entry = pd.DataFrame([{
                'date': pd.Timestamp(date),
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
            }])
            
            # Append to existing data
            self.emissions_data = pd.concat([self.emissions_data, new_entry], ignore_index=True)
            
            # Save data
            self.save_emissions_data()
            
            return True
        except Exception as e:
            print(f"Error adding emission entry: {str(e)}")
            return False
    
    def import_csv(self, file_path_or_buffer):
        """
        Import emissions data from CSV.
        
        Args:
            file_path_or_buffer: Path to CSV file or file-like object
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Read CSV
            df = pd.read_csv(file_path_or_buffer)
            
            # Check required columns
            required_columns = ['date', 'scope', 'category', 'activity', 'quantity', 'unit', 'emission_factor']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}"
            
            # Convert date strings to datetime objects
            df['date'] = pd.to_datetime(df['date'])
            
            # Calculate emissions if not provided
            if 'emissions_kgCO2e' not in df.columns:
                df['emissions_kgCO2e'] = df['quantity'].astype(float) * df['emission_factor'].astype(float)
            
            # Add notes column if not present
            if 'notes' not in df.columns:
                df['notes'] = ""
            
            # Append to existing data
            self.emissions_data = pd.concat([self.emissions_data, df], ignore_index=True)
            
            # Save data
            self.save_emissions_data()
            
            return True, f"Successfully imported {len(df)} entries"
        except Exception as e:
            return False, f"Error importing CSV: {str(e)}"
    
    def export_csv(self, file_path=None, start_date=None, end_date=None):
        """
        Export emissions data to CSV.
        
        Args:
            file_path (str, optional): Path to save CSV file
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering
            
        Returns:
            str or bool: CSV string if file_path is None, otherwise True if successful
        """
        try:
            # Filter data by date range if specified
            data = self.emissions_data.copy()
            if start_date and end_date:
                mask = (data['date'] >= pd.Timestamp(start_date)) & (data['date'] <= pd.Timestamp(end_date))
                data = data.loc[mask]
            
            # Convert datetime objects to strings
            if 'date' in data.columns:
                data['date'] = data['date'].dt.strftime('%Y-%m-%d')
            
            if file_path:
                # Save to file
                data.to_csv(file_path, index=False)
                return True
            else:
                # Return CSV string
                csv_buffer = StringIO()
                data.to_csv(csv_buffer, index=False)
                return csv_buffer.getvalue()
        except Exception as e:
            print(f"Error exporting CSV: {str(e)}")
            return False
    
    def generate_pdf_report(self, file_path=None, start_date=None, end_date=None):
        """
        Generate PDF report.
        
        Args:
            file_path (str, optional): Path to save PDF file
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering
            
        Returns:
            bytes or bool: PDF bytes if file_path is None, otherwise True if successful
        """
        try:
            # Filter data by date range if specified
            data = self.emissions_data.copy()
            if start_date and end_date:
                mask = (data['date'] >= pd.Timestamp(start_date)) & (data['date'] <= pd.Timestamp(end_date))
                data = data.loc[mask]
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Set font
            pdf.set_font("Arial", "B", 16)
            
            # Title
            pdf.cell(0, 10, "Carbon Emissions Report", 0, 1, "C")
            pdf.set_font("Arial", "", 12)
            
            # Company info
            pdf.cell(0, 10, f"Company: {self.company_info['name']}", 0, 1)
            pdf.cell(0, 10, f"Reporting Period: {start_date.strftime('%Y-%m-%d') if start_date else 'All'} to {end_date.strftime('%Y-%m-%d') if end_date else 'All'}", 0, 1)
            pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
            
            # Summary
            pdf.ln(10)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Summary", 0, 1)
            pdf.set_font("Arial", "", 12)
            
            total_emissions = data['emissions_kgCO2e'].sum()
            pdf.cell(0, 10, f"Total Emissions: {total_emissions:.2f} kgCO2e", 0, 1)
            
            # Emissions by scope
            scope_data = data.groupby('scope')['emissions_kgCO2e'].sum().reset_index()
            pdf.ln(5)
            pdf.cell(0, 10, "Emissions by Scope:", 0, 1)
            for _, row in scope_data.iterrows():
                pdf.cell(0, 10, f"{row['scope']}: {row['emissions_kgCO2e']:.2f} kgCO2e ({row['emissions_kgCO2e'] / total_emissions * 100:.1f}%)", 0, 1)
            
            # Emissions by category
            category_data = data.groupby('category')['emissions_kgCO2e'].sum().reset_index()
            pdf.ln(5)
            pdf.cell(0, 10, "Top Categories:", 0, 1)
            for _, row in category_data.nlargest(5, 'emissions_kgCO2e').iterrows():
                pdf.cell(0, 10, f"{row['category']}: {row['emissions_kgCO2e']:.2f} kgCO2e ({row['emissions_kgCO2e'] / total_emissions * 100:.1f}%)", 0, 1)
            
            # Data table
            pdf.ln(10)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Emissions Data", 0, 1)
            pdf.set_font("Arial", "B", 10)
            
            # Table header
            col_widths = [25, 25, 30, 30, 20, 15, 25, 30]
            headers = ['Date', 'Scope', 'Category', 'Activity', 'Quantity', 'Unit', 'Factor', 'Emissions (kgCO2e)']
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, 1)
            pdf.ln()
            
            # Table data
            pdf.set_font("Arial", "", 8)
            for _, row in data.iterrows():
                pdf.cell(col_widths[0], 10, row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], pd.Timestamp) else str(row['date']), 1)
                pdf.cell(col_widths[1], 10, str(row['scope']), 1)
                pdf.cell(col_widths[2], 10, str(row['category']), 1)
                pdf.cell(col_widths[3], 10, str(row['activity']), 1)
                pdf.cell(col_widths[4], 10, f"{row['quantity']:.2f}", 1)
                pdf.cell(col_widths[5], 10, str(row['unit']), 1)
                pdf.cell(col_widths[6], 10, f"{row['emission_factor']:.4f}", 1)
                pdf.cell(col_widths[7], 10, f"{row['emissions_kgCO2e']:.2f}", 1)
                pdf.ln()
            
            if file_path:
                # Save to file
                pdf.output(file_path)
                return True
            else:
                # Return PDF bytes
                return pdf.output(dest='S').encode('latin1')
        except Exception as e:
            print(f"Error generating PDF report: {str(e)}")
            return False
    
    def get_emissions_summary(self):
        """
        Get emissions summary statistics.
        
        Returns:
            dict: Summary statistics
        """
        if len(self.emissions_data) == 0:
            return {
                "total_emissions": 0,
                "scope_breakdown": {},
                "category_breakdown": {},
                "time_series": {}
            }
        
        # Total emissions
        total_emissions = self.emissions_data['emissions_kgCO2e'].sum()
        
        # Emissions by scope
        scope_data = self.emissions_data.groupby('scope')['emissions_kgCO2e'].sum().to_dict()
        
        # Emissions by category
        category_data = self.emissions_data.groupby('category')['emissions_kgCO2e'].sum().to_dict()
        
        # Time series data (monthly)
        time_data = self.emissions_data.copy()
        if 'date' in time_data.columns and len(time_data) > 0:
            time_data['month'] = time_data['date'].dt.strftime('%Y-%m')
            time_series = time_data.groupby(['month', 'scope'])['emissions_kgCO2e'].sum().reset_index()
            time_series_dict = {}
            for _, row in time_series.iterrows():
                if row['month'] not in time_series_dict:
                    time_series_dict[row['month']] = {}
                time_series_dict[row['month']][row['scope']] = row['emissions_kgCO2e']
        else:
            time_series_dict = {}
        
        return {
            "total_emissions": total_emissions,
            "scope_breakdown": scope_data,
            "category_breakdown": category_data,
            "time_series": time_series_dict
        }
    
    def get_filtered_data(self, start_date=None, end_date=None, scope=None, category=None):
        """
        Get filtered emissions data.
        
        Args:
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering
            scope (str, optional): Scope for filtering
            category (str, optional): Category for filtering
            
        Returns:
            pandas.DataFrame: Filtered data
        """
        data = self.emissions_data.copy()
        
        # Apply filters
        if start_date and end_date:
            mask = (data['date'] >= pd.Timestamp(start_date)) & (data['date'] <= pd.Timestamp(end_date))
            data = data.loc[mask]
        
        if scope:
            data = data[data['scope'] == scope]
        
        if category:
            data = data[data['category'] == category]
        
        return data
