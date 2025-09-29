# 🌍 CarbonSenseAI - User Manual

**Carbon Accounting & Reporting Tool for Indian SMEs**

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Navigation Overview](#navigation-overview)
3. [Home Page](#home-page)
4. [Dashboard](#dashboard)
5. [Data Entry](#data-entry)
6. [Compliance](#compliance)
7. [Analytics](#analytics)
8. [Settings](#settings)
9. [Data Management](#data-management)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### What is CarbonSenseAI?
CarbonSenseAI is an AI-powered carbon accounting platform designed specifically for Indian Small and Medium Enterprises (SMEs). It helps you track, analyze, and reduce your environmental impact while ensuring compliance with Indian MoEF&CC guidelines and BIS standards.

### First Steps
1. **Launch the Application**: Open the app in your web browser
2. **Explore the Home Page**: Get familiar with the interface and features
3. **Add Your First Data**: Start with the Data Entry section
4. **View Analytics**: Check your Dashboard for insights
5. **Assess Compliance**: Use the Compliance tools for regulatory requirements

---

## 🧭 Navigation Overview

The application has 6 main sections accessible via the sidebar:

| Icon | Section | Purpose |
|------|---------|---------|
| 🏠 | **Home** | Welcome page and quick start guide |
| 📊 | **Dashboard** | Analytics, charts, and data visualization |
| 📝 | **Data Entry** | Add and manage emissions data |
| ⚖️ | **Compliance** | Regulatory compliance assessment |
| 🕵️ | **Analytics** | Advanced analytics and insights |
| ⚙️ | **Settings** | Company information and preferences |

---

## 🏠 Home Page

### Features
- **Welcome Message**: Introduction to the platform
- **Quick Start Guide**: Step-by-step guidance for new users
- **Key Features Overview**: Platform capabilities
- **Action Buttons**: Quick navigation to important sections
- **Pro Tips**: Best practices for success
- **Data Summary**: Current data status (when available)

### What You'll See
- **With No Data**: Full welcome experience with guidance
- **With Data**: Welcome content plus summary metrics:
  - Total Emissions
  - Data Points
  - Scopes Covered
  - Latest Entry Date

---

## 📊 Dashboard

### Overview
The Dashboard provides visual analytics of your carbon footprint with interactive charts and key metrics.

### Key Metrics (Top Section)
- **Total Emissions**: Your complete carbon footprint in kgCO2e
- **Latest Entry**: Date of your most recent data entry (format: Jan 30th 2025)
- **Scopes Covered**: Progress indicator (X/3 scopes)
- **Data Points**: Total number of entries in your database

### Charts & Visualizations

#### 🌍 Emissions by Scope (Centered Pie Chart)
- **Purpose**: Shows distribution across Scope 1, 2, and 3 emissions
- **Features**: 
  - Interactive hover details
  - Percentage breakdown
  - Color-coded by scope
  - Centered layout for better visibility

#### 📊 Top Emission Categories (Bar Chart)
- **Purpose**: Identifies your highest emission sources
- **Features**:
  - Horizontal bar chart
  - Top 10 categories only
  - Sorted by emission volume
  - Color gradient visualization

#### 📈 Emissions Over Time (Line Chart)
- **Purpose**: Tracks emission trends by scope over time
- **Features**:
  - Multi-line chart by scope
  - Monthly aggregation
  - Interactive markers
  - Trend analysis

### No Data State
- **Message**: Guidance to add data first
- **Quick Actions**: Direct buttons to Data Entry and CSV Upload

---

## 📝 Data Entry

### Overview
The Data Entry section allows you to add, manage, and import emissions data through multiple methods.

### Manual Entry Tab

#### Business Information Section
- **Date**: When the emission occurred (date picker)
- **Business Unit**: Department/division (Corporate, Manufacturing, Sales, R&D, Logistics, IT, Other)
- **Project**: Associated initiative (Carbon Reduction, Sustainability Program, Operational, Other)
- **Scope**: Emission scope (1, 2, or 3) with helpful tooltips
- **Category**: Emission category (auto-populated based on scope)
- **Country**: Location where emission occurred
- **Facility/Location**: Specific facility (e.g., "Mumbai HQ", "Jakarta Plant 2")
- **Responsible Person**: Person accountable for this emission source

#### Activity & Measurement Section
- **Activity**: Specific activity (auto-populated based on category)
- **Quantity**: Amount of activity (numeric input with validation)
- **Unit**: Measurement unit (kWh, MWh, GJ, liter, gallon, kg, tonne, km, mile, etc.)
- **Emission Factor**: CO2 factor per unit (auto-suggested based on location/category)
- **Data Quality**: Quality indicator (Low, Medium, High) with color-coded help
- **Verification Status**: Verification level (Unverified, Internally Verified, Third-Party Verified)
- **Notes**: Additional context and documentation
- **Cost**: Optional cost tracking with currency selection

#### AI Assistance
- **Smart Suggestions**: Automatic emission factor recommendations
- **Country-Specific Factors**: Localized emission factors for India, US, UK, Japan, Indonesia
- **Validation**: Real-time form validation and error checking

### CSV Upload Tab

#### Supported Formats
**Required Columns:**
- `scope`: Scope 1, Scope 2, or Scope 3
- `category`: Emission category
- `activity`: Activity description
- `quantity`: Amount of activity
- `unit`: Unit of measurement
- `emission_factor`: CO2 emission factor per unit

**Optional Columns:**
- `date`: Specific date (YYYY-MM-DD format)
- `reporting_period`: Period description (e.g., "January 2025")
- `emissions_kgCO2e`: Pre-calculated emissions
- `business_unit`, `project`, `country`, `facility`, `responsible_person`
- `data_quality`, `verification_status`, `notes`

#### Date Handling Options
- **CSV with dates**: Uses actual dates from your file
- **CSV with reporting_period**: Perfect for monthly/quarterly reports
- **CSV without dates**: Assigns current date to all entries

#### File Processing
1. **Upload**: Choose your CSV file
2. **Preview**: Review file structure and data
3. **Validate**: Check for required columns and data integrity
4. **Process**: Import data into the system

#### Sample Templates
- **Reporting Period Template**: Best for monthly/quarterly reports
- **Specific Dates Template**: Best for detailed daily tracking

### Data Guide Tab

#### Data Requirements
- **Scope 1 (Direct)**: Company vehicles, on-site fuel, refrigerant leaks, process emissions
- **Scope 2 (Energy Indirect)**: Electricity, steam, heating, cooling
- **Scope 3 (Other Indirect)**: Business travel, commuting, waste, water, purchased goods

#### Data Quality Guidelines
- **High Quality (±5%)**: Direct measurement/metering
- **Medium Quality (±15%)**: Calculated from bills/invoices
- **Low Quality (±30%)**: Estimated/proxy data

#### Industry-Specific Guidance
- Customized recommendations for Manufacturing, Technology, Services, Retail, Transportation, Agriculture, and Energy sectors

#### Data Readiness Assessment
- Real-time scoring of your data completeness
- 7-point checklist covering entries, scope coverage, time distribution, quality, verification, facilities, and emission factors

### Data Assistant Tab

#### AI-Powered Help
- **Activity Classification**: Get help categorizing emission activities
- **Scope Mapping**: Assistance with correct scope assignment
- **Factor Recommendations**: AI-suggested emission factors
- **Calculation Guidance**: Step-by-step calculation help

### Data Management

#### Existing Data Table
- **View All Entries**: Complete data table with all fields
- **Delete Entries**: Remove specific entries by index number
- **Download Data**: Export current data as CSV
- **Clear All Data**: Remove all data (with confirmation)
- **Refresh**: Update the display

---

## ⚖️ Compliance

### Overview
The Compliance section helps you assess your carbon performance against industry benchmarks and regulatory requirements.

### Compliance Assessment Tab

#### Company Information Form
- **Company Name**: Your organization name
- **Industry**: Select from Manufacturing, Technology, Services, Retail, Transportation, Agriculture, Energy
- **Primary Location**: India, Indonesia, Japan, or Global
- **Number of Employees**: Total workforce size
- **Annual Revenue**: Revenue in Million INR
- **Assessment Period**: Time period in months (1-36)

#### Assessment Results
- **Compliance Status**: Color-coded status indicator
  - 🟢 Excellent
  - 🟡 Good
  - 🟠 Needs Improvement
  - 🔴 Poor/Critical
- **Detailed Analysis**: Comprehensive compliance report
- **Recommendations**: Specific improvement suggestions
- **Benchmarking**: Industry comparison data

### Industry Benchmarks Tab
- Compare your performance against industry standards
- Sector-specific emission factors and targets
- Best practices from leading companies

### Compliance Report Tab
- Generate detailed compliance reports
- Export compliance documentation
- Regulatory compliance summary

---

## 🕵️ Analytics

### Advanced Analytics Features
- **Trend Analysis**: Long-term emission patterns
- **Predictive Modeling**: Future emission projections
- **Comparative Analysis**: Period-over-period comparisons
- **Custom Reports**: Tailored analytical reports
- **Data Visualization**: Advanced charting options

---

## ⚙️ Settings

### Company Information
- **Basic Details**: Company name, industry, location
- **Contact Information**: Person, email, phone
- **Export Markets**: EU, Japan, Indonesia checkboxes
- **Preferences**: Application settings and configurations

---

## 📊 Data Management

### Data Import/Export
- **CSV Import**: Bulk data upload with validation
- **Data Export**: Download data in CSV format
- **Backup Creation**: Automatic backup of corrupted files
- **Data Validation**: Real-time error checking

### Data Quality
- **Quality Indicators**: Color-coded quality levels
- **Verification Status**: Track data verification progress
- **Documentation**: Notes and source tracking
- **Audit Trail**: Change history and responsibility tracking

---

## 💡 Best Practices

### Data Collection
1. **Start Small**: Begin with major emission sources (electricity, fuel, travel)
2. **Focus on Quality**: Prioritize accurate data over quantity
3. **Regular Updates**: Set monthly data entry sessions
4. **Document Sources**: Always include notes about data sources
5. **Verify Data**: Use verification status to track data quality

### Carbon Accounting
1. **Scope Coverage**: Include activities from all three scopes
2. **Consistent Periods**: Maintain regular reporting periods
3. **Facility Coverage**: Include all significant locations
4. **Responsibility Assignment**: Assign responsible persons for each source
5. **Baseline Establishment**: Create a solid baseline for comparison

### Platform Usage
1. **Regular Monitoring**: Check Dashboard weekly
2. **Compliance Tracking**: Run quarterly compliance assessments
3. **Data Backup**: Export data regularly for backup
4. **Team Training**: Ensure all users understand the platform
5. **Goal Setting**: Define clear reduction targets

---

## 🔧 Troubleshooting

### Common Issues

#### Data Entry Problems
**Issue**: Cannot add new entry
- **Solution**: Check all required fields are filled
- **Solution**: Ensure quantity is greater than zero
- **Solution**: Verify facility/location is provided

**Issue**: CSV upload fails
- **Solution**: Check file format is CSV
- **Solution**: Verify required columns are present
- **Solution**: Ensure data types are correct

#### Dashboard Issues
**Issue**: Charts not displaying
- **Solution**: Ensure you have emissions data
- **Solution**: Check data has valid emission values
- **Solution**: Verify date fields are properly formatted

**Issue**: Metrics showing zero
- **Solution**: Check emissions_kgCO2e calculations
- **Solution**: Verify emission factors are not zero
- **Solution**: Ensure quantity values are numeric

#### Navigation Problems
**Issue**: Page not loading
- **Solution**: Refresh the browser
- **Solution**: Clear browser cache
- **Solution**: Check internet connection

### Data Validation Errors
- **Missing Required Fields**: Fill all mandatory fields
- **Invalid Dates**: Use YYYY-MM-DD format
- **Negative Values**: Ensure quantities are positive
- **Invalid Numbers**: Use numeric values for calculations

### Performance Tips
- **Large Datasets**: Upload data in smaller batches
- **Browser Performance**: Use latest browser version
- **Memory Issues**: Close unnecessary browser tabs
- **Loading Speed**: Ensure stable internet connection

---

## 📞 Support

### Getting Help
- **In-App Help**: Use the ❓ Help section on Home page
- **Documentation**: Refer to this user manual
- **Data Guide**: Use the Data Guide tab for requirements
- **AI Assistant**: Use the Data Assistant for classification help

### Best Practices for Success
- **Start Simple**: Begin with basic data entry
- **Be Consistent**: Maintain regular data updates
- **Stay Organized**: Use proper categorization
- **Monitor Progress**: Check Dashboard regularly
- **Seek Compliance**: Use Compliance tools for regulatory alignment

---

## 🎯 Quick Reference

### Essential Workflows

#### New User Setup
1. Visit Home page → Read Quick Start Guide
2. Go to Data Entry → Add first emission entry
3. Return to Dashboard → View your first analytics
4. Check Compliance → Run initial assessment

#### Monthly Data Update
1. Go to Data Entry → Manual Entry or CSV Upload
2. Add new month's emissions data
3. Visit Dashboard → Review updated metrics
4. Check Analytics → Analyze trends

#### Quarterly Review
1. Export current data for backup
2. Run Compliance assessment
3. Review Dashboard analytics
4. Set targets for next quarter

### Keyboard Shortcuts
- **Navigation**: Use sidebar buttons for quick page switching
- **Forms**: Tab key to move between fields
- **Data Entry**: Enter key to submit forms

### Data Formats
- **Dates**: Jan 30th 2025 (display format)
- **Numbers**: Always use decimal points, not commas
- **Currencies**: Select appropriate currency when entering costs
- **Units**: Choose from predefined list or specify custom units

---

*This manual covers CarbonSenseAI version 2.0. For the latest updates and features, refer to the application interface.*

**© 2025 CarbonSenseAI - Empowering Indian SMEs for Sustainable Future**
