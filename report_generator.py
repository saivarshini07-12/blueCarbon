"""
Report generator for YourCarbonFootprint application.
Generates PDF reports and visualizations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF  # fpdf2 package
import os
from datetime import datetime
import base64
from io import BytesIO

class ReportGenerator:
    def __init__(self, data_handler):
        """Initialize the ReportGenerator class."""
        self.data_handler = data_handler
    
    def generate_pdf_report(self, file_path=None, start_date=None, end_date=None, company_info=None):
        """
        Generate PDF report.
        
        Args:
            file_path (str, optional): Path to save PDF file
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering
            company_info (dict, optional): Company information
            
        Returns:
            bytes or bool: PDF bytes if file_path is None, otherwise True if successful
        """
        try:
            # Get filtered data
            data = self.data_handler.get_filtered_data(start_date, end_date)
            
            if len(data) == 0:
                return False, "No data available for the selected period."
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Set font
            pdf.set_font("Arial", "B", 16)
            
            # Title
            pdf.cell(0, 10, "Carbon Emissions Report", 0, 1, "C")
            pdf.set_font("Arial", "", 12)
            
            # Company info
            if company_info:
                pdf.cell(0, 10, f"Company: {company_info.get('name', 'N/A')}", 0, 1)
                pdf.cell(0, 10, f"Industry: {company_info.get('industry', 'N/A')}", 0, 1)
                pdf.cell(0, 10, f"Location: {company_info.get('location', 'N/A')}", 0, 1)
            
            # Reporting period
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
            
            # Compliance section
            pdf.ln(10)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Regulatory Compliance", 0, 1)
            pdf.set_font("Arial", "", 12)
            
            pdf.cell(0, 10, "EU CBAM: This report can be used as supporting documentation for EU CBAM compliance.", 0, 1)
            pdf.cell(0, 10, "Japan GX League: This report follows the GX League reporting format.", 0, 1)
            pdf.cell(0, 10, "Indonesia ETS/ETP: This report can be used for Indonesia ETS/ETP compliance.", 0, 1)
            
            # Recommendations
            pdf.ln(10)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Recommendations", 0, 1)
            pdf.set_font("Arial", "", 12)
            
            pdf.cell(0, 10, "1. Focus on reducing emissions from the top categories identified in this report.", 0, 1)
            pdf.cell(0, 10, "2. Consider implementing energy efficiency measures for Scope 2 emissions.", 0, 1)
            pdf.cell(0, 10, "3. Explore renewable energy options to reduce your carbon footprint.", 0, 1)
            pdf.cell(0, 10, "4. Engage with suppliers to address Scope 3 emissions in your value chain.", 0, 1)
            
            if file_path:
                # Save to file
                pdf.output(file_path)
                return True, "Report generated successfully."
            else:
                # Return PDF bytes
                return pdf.output(dest='S').encode('latin1'), "Report generated successfully."
        except Exception as e:
            return False, f"Error generating PDF report: {str(e)}"
    
    def create_scope_pie_chart(self, data):
        """
        Create pie chart of emissions by scope.
        
        Args:
            data (pandas.DataFrame): Emissions data
            
        Returns:
            plotly.graph_objects.Figure: Pie chart figure
        """
        scope_data = data.groupby('scope')['emissions_kgCO2e'].sum().reset_index()
        fig = px.pie(
            scope_data, 
            values='emissions_kgCO2e', 
            names='scope',
            color='scope',
            color_discrete_map={
                'Scope 1': '#4CAF50', 
                'Scope 2': '#2196F3', 
                'Scope 3': '#FFC107'
            },
            title='Emissions by Scope'
        )
        fig.update_layout(
            legend_title="Scope",
            font=dict(size=12),
            margin=dict(t=50, b=20, l=20, r=20)
        )
        return fig
    
    def create_category_bar_chart(self, data):
        """
        Create bar chart of emissions by category.
        
        Args:
            data (pandas.DataFrame): Emissions data
            
        Returns:
            plotly.graph_objects.Figure: Bar chart figure
        """
        category_data = data.groupby('category')['emissions_kgCO2e'].sum().reset_index()
        category_data = category_data.sort_values('emissions_kgCO2e', ascending=False)
        fig = px.bar(
            category_data, 
            x='category', 
            y='emissions_kgCO2e',
            color='category',
            title='Emissions by Category'
        )
        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Emissions (kgCO2e)",
            legend_title="Category",
            font=dict(size=12),
            margin=dict(t=50, b=100, l=50, r=20),
            xaxis_tickangle=-45
        )
        return fig
    
    def create_time_series_chart(self, data):
        """
        Create time series chart of emissions over time.
        
        Args:
            data (pandas.DataFrame): Emissions data
            
        Returns:
            plotly.graph_objects.Figure: Line chart figure
        """
        if 'date' not in data.columns or len(data) == 0:
            # Create empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title='Emissions Over Time',
                xaxis_title="Month",
                yaxis_title="Emissions (kgCO2e)",
                font=dict(size=12),
                margin=dict(t=50, b=50, l=50, r=20)
            )
            return fig
        
        # Group by month and scope
        time_data = data.copy()
        time_data['month'] = pd.to_datetime(time_data['date']).dt.strftime('%Y-%m')
        time_data = time_data.groupby(['month', 'scope'])['emissions_kgCO2e'].sum().reset_index()
        
        fig = px.line(
            time_data, 
            x='month', 
            y='emissions_kgCO2e',
            color='scope',
            markers=True,
            title='Emissions Over Time'
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Emissions (kgCO2e)",
            legend_title="Scope",
            font=dict(size=12),
            margin=dict(t=50, b=50, l=50, r=20)
        )
        return fig
    
    def create_activity_treemap(self, data):
        """
        Create treemap of emissions by scope, category, and activity.
        
        Args:
            data (pandas.DataFrame): Emissions data
            
        Returns:
            plotly.graph_objects.Figure: Treemap figure
        """
        fig = px.treemap(
            data,
            path=['scope', 'category', 'activity'],
            values='emissions_kgCO2e',
            color='scope',
            color_discrete_map={
                'Scope 1': '#4CAF50', 
                'Scope 2': '#2196F3', 
                'Scope 3': '#FFC107'
            },
            title='Emissions Breakdown'
        )
        fig.update_layout(
            margin=dict(t=50, b=20, l=20, r=20),
            font=dict(size=12)
        )
        return fig
    
    def create_monthly_comparison_chart(self, data):
        """
        Create bar chart comparing emissions by month.
        
        Args:
            data (pandas.DataFrame): Emissions data
            
        Returns:
            plotly.graph_objects.Figure: Bar chart figure
        """
        if 'date' not in data.columns or len(data) == 0:
            # Create empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title='Monthly Emissions Comparison',
                xaxis_title="Month",
                yaxis_title="Emissions (kgCO2e)",
                font=dict(size=12),
                margin=dict(t=50, b=50, l=50, r=20)
            )
            return fig
        
        # Group by month
        monthly_data = data.copy()
        monthly_data['month'] = pd.to_datetime(monthly_data['date']).dt.strftime('%Y-%m')
        monthly_data = monthly_data.groupby('month')['emissions_kgCO2e'].sum().reset_index()
        
        fig = px.bar(
            monthly_data,
            x='month',
            y='emissions_kgCO2e',
            title='Monthly Emissions Comparison'
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Emissions (kgCO2e)",
            font=dict(size=12),
            margin=dict(t=50, b=50, l=50, r=20)
        )
        return fig
