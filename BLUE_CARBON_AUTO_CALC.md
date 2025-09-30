# Blue Carbon Automatic CO2 Sequestration Calculator

## 🌊 Enhancement Overview

This enhancement implements automatic CO2 sequestration calculation for Blue Carbon projects, eliminating the need for manual data entry and ensuring accurate, science-based estimates.

## ✨ Features Added

### 1. Scientific Rate Database
- **Mangrove**: 0.5 tons CO2/hectare/year (range: 0.3-0.8)
- **Seagrass**: 0.35 tons CO2/hectare/year (range: 0.2-0.6)
- **Salt Marsh**: 0.3 tons CO2/hectare/year (range: 0.15-0.5)
- **Coastal Wetland**: 0.4 tons CO2/hectare/year (range: 0.25-0.65)

### 2. Site Quality Assessment
Users can now specify site conditions:
- **Poor (0.5x)**: Degraded or challenging conditions
- **Average (1.0x)**: Standard conditions
- **Good (1.2x)**: Favorable conditions 
- **Excellent (1.5x)**: Optimal conditions

### 3. Smart Form Interface
- **Real-time calculation** as users input area and select ecosystem type
- **Calculation transparency** showing formula and assumptions
- **Range estimates** to indicate uncertainty
- **Disabled input field** for sequestration (auto-calculated, read-only)

## 🔧 Technical Implementation

### Files Modified:
1. **`emission_factors.py`**: Added blue carbon sequestration rates and calculation functions
2. **`app.py`**: Modified Blue Carbon registration form for automatic calculation

### New Functions:
- `calculate_blue_carbon_sequestration(area, ecosystem_type, quality_factor)`
- `get_blue_carbon_rate_info(ecosystem_type)`

## 📊 Example Calculations

### Example 1: Mangrove Restoration
- **Area**: 100 hectares
- **Ecosystem**: Mangrove
- **Quality**: Average (1.0x)
- **Result**: 50.0 tons CO2/year (range: 30.0-80.0)

### Example 2: Seagrass Conservation  
- **Area**: 150 hectares
- **Ecosystem**: Seagrass
- **Quality**: Good (1.2x)
- **Result**: 63.0 tons CO2/year (range: 36.0-108.0)

## 🎯 Benefits

### For Users:
- **Eliminates manual calculation errors**
- **Provides science-based estimates**
- **Saves time during project registration**
- **Increases confidence in carbon credit calculations**

### For the Platform:
- **Standardized calculations across all projects**
- **Improved data quality and consistency**
- **Enhanced credibility with stakeholders**
- **Better compliance with international standards**

## 🔬 Scientific Basis

The sequestration rates are based on:
- **IPCC Guidelines** for coastal ecosystems
- **Peer-reviewed research** on blue carbon sequestration
- **Field measurements** from restoration projects
- **Conservative estimates** to ensure credibility

## 🚀 Usage

1. Navigate to **Blue Carbon** → **Register Project**
2. Enter **Project Name** and **Location**
3. Input **Area** (hectares)
4. Select **Ecosystem Type**
5. Choose **Site Quality** assessment
6. **CO2 Sequestration is automatically calculated!**

## 🔍 Validation

The calculation can be tested using:
```bash
python test_blue_carbon_calc.py
```

This script demonstrates various scenarios and validates the calculation logic.

---

**Note**: This enhancement follows international best practices for blue carbon accounting and provides transparency in all calculations, supporting the credibility of the carbon credit registry.