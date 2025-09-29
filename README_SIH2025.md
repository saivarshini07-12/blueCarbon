# 🌊 Blockchain-Based Blue Carbon Registry and MRV System
## SIH 2025 - Problem Statement 25038

### 🎯 **Project Overview**
A comprehensive blockchain-powered platform that combines carbon accounting with blue carbon ecosystem restoration, implementing a decentralized Monitoring, Reporting, and Verification (MRV) system for transparent carbon credit generation and trading.

### 🏆 **Key Features**

#### 🌊 **Blue Carbon Registry**
- **Immutable Project Registration**: Register mangrove, seagrass, salt marsh, and coastal wetland restoration projects
- **Decentralized Storage**: Project data stored on blockchain with IPFS integration
- **Smart Contract Automation**: Automated carbon credit issuance upon verification
- **Multi-stakeholder Support**: NGOs, communities, coastal panchayats, and companies can participate

#### 💰 **Carbon Credits Marketplace**
- **Tokenized Credits**: Smart contracts for verified carbon credit tokens
- **Real-time Trading**: Buy and sell carbon credits with transparent pricing
- **Company Dashboard**: Track carbon balance, emissions, and net environmental impact
- **Compliance Integration**: Automated compliance checking and reporting

#### 📱 **MRV System (Monitoring, Reporting & Verification)**
- **Field Data Integration**: Upload from mobile apps, drones, and field surveys
- **Multi-verifier Support**: Independent verification from authorized entities
- **Data Integrity**: Cryptographic hashing ensures data immutability
- **Automated Workflows**: Streamlined verification and credit issuance process

#### 🏛️ **NCCR Admin Tools**
- **Centralized Management**: Admin panel for National Centre for Coastal Research
- **Verification Oversight**: Approve verifications and manage verifiers
- **System Analytics**: Comprehensive reporting and statistics
- **Compliance Monitoring**: Track regulatory compliance across projects

### 🚀 **Quick Start Guide**

#### **1. Installation**
```bash
# Clone the repository
git clone https://github.com/kjssmanohar/Carbon_Accounting.git
cd Carbon_Accounting

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your Groq API key
```

#### **2. Initialize Demo Data**
```bash
# Populate with sample blue carbon projects and verifications
python demo_populate.py
```

#### **3. Launch Application**
```bash
# Start the Streamlit application
streamlit run app.py
```

### 📊 **System Architecture**

#### **Blockchain Layer**
- **Smart Contracts**: Solidity contracts for registry, credits, and verification
- **Network Support**: Ethereum, Polygon, or custom networks
- **IPFS Integration**: Decentralized storage for project documentation

#### **Application Layer**
- **Streamlit Frontend**: Interactive web interface
- **Python Backend**: Business logic and blockchain integration
- **AI Integration**: Groq-powered analytics and recommendations

#### **Data Layer**
- **Blockchain Storage**: Immutable project and verification records
- **IPFS Storage**: Large files and documentation
- **Local Cache**: Performance optimization for frequent queries

### 🔧 **Configuration**

#### **Blockchain Configuration (blockchain_config.json)**
```json
{
  "blockchain_enabled": true,
  "network": "sepolia",
  "rpc_url": "your_rpc_endpoint",
  "contract_address": "deployed_contract_address",
  "private_key": "your_private_key",
  "verification_threshold": 2
}
```

#### **Environment Variables (.env)**
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 🌍 **Use Cases for SIH 2025**

#### **1. Coastal Panchayats**
- Register community-led mangrove restoration projects
- Earn carbon credits for environmental conservation
- Generate revenue from carbon credit sales
- Monitor project progress with transparent verification

#### **2. NGOs and Research Organizations**
- Submit field verification data through mobile interface
- Contribute to scientific monitoring and reporting
- Access comprehensive project analytics
- Collaborate with NCCR for policy development

#### **3. Corporations**
- Offset carbon emissions through verified blue carbon credits
- Meet corporate sustainability goals and ESG requirements
- Support coastal community development
- Transparent reporting for stakeholders

#### **4. Government Agencies (NCCR/MoES)**
- Centralized oversight of blue carbon initiatives
- Evidence-based policy making with real data
- International reporting for climate commitments
- Quality assurance through multi-level verification

### 📈 **Demo Scenarios**

#### **Scenario 1: Project Registration**
1. Navigate to "Blue Carbon" → "Register Project"
2. Register a new mangrove restoration project
3. Provide location, area, and expected carbon sequestration
4. Project is recorded on blockchain with unique ID

#### **Scenario 2: Field Verification**
1. Go to "MRV System" → "Submit Field Data"
2. Upload verification data (area measurement, biomass, soil carbon)
3. Add GPS coordinates and photographic evidence
4. Submit for NCCR verification and approval

#### **Scenario 3: Carbon Credit Trading**
1. Check "Carbon Credits" dashboard for your balance
2. Visit "Marketplace" to buy/sell credits
3. Companies can offset emissions by purchasing verified credits
4. Transparent pricing and transaction history

#### **Scenario 4: Compliance Reporting**
1. Record company emissions in "Carbon Credits"
2. Purchase offsets to achieve carbon neutrality
3. Generate compliance reports with blockchain verification
4. Export data for regulatory submissions

### 🛠️ **Technology Stack**

- **Frontend**: Streamlit, Plotly, Pandas
- **Backend**: Python, Web3.py, FastAPI
- **Blockchain**: Solidity, Ethereum, IPFS
- **AI/ML**: Groq API, CrewAI, LangChain
- **Database**: Blockchain (primary), Local cache
- **Deployment**: Docker, Docker Compose

### 🏅 **SIH 2025 Alignment**

#### **Problem Statement Requirements ✅**
- ✅ **Blockchain-powered registry**: Immutable project and verification storage
- ✅ **Smart contracts for tokenized credits**: Automated credit issuance and trading
- ✅ **NGO/community onboarding**: Multi-stakeholder platform support
- ✅ **Field data integration**: Mobile and drone data upload capabilities
- ✅ **Admin tools for NCCR**: Comprehensive management and oversight panel

#### **Innovation Highlights**
- **Integrated Approach**: Combines carbon accounting with blue carbon restoration
- **Multi-stakeholder Platform**: Supports diverse user types and use cases
- **AI-Powered Analytics**: Intelligent insights and recommendations
- **Scalable Architecture**: Designed for national-level deployment
- **International Standards**: Aligned with global MRV best practices

### 📋 **Project Structure**
```
Carbon_Accounting/
├── app.py                 # Main Streamlit application
├── blockchain_mrv.py      # Blockchain MRV system
├── ai_agents.py          # AI-powered analytics
├── demo_populate.py      # Demo data population
├── blockchain/
│   └── contracts/
│       └── BlueCarbonRegistry.sol  # Smart contracts
├── blockchain_config.json # Blockchain configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── README_SIH2025.md    # This file
```

### 🎥 **Demo Video Script**

1. **Introduction** (30s): Overview of blue carbon importance and blockchain solution
2. **Project Registration** (45s): Register a new mangrove restoration project
3. **Field Verification** (60s): Upload verification data through MRV system
4. **Credit Issuance** (30s): Show automated credit generation upon approval
5. **Marketplace Trading** (45s): Demonstrate carbon credit buying/selling
6. **Dashboard Analytics** (30s): Company carbon balance and compliance status
7. **Admin Panel** (30s): NCCR oversight and system management

### 🌟 **Future Enhancements**

- **Mobile App**: Native iOS/Android app for field data collection
- **IoT Integration**: Sensor networks for real-time monitoring
- **Satellite Integration**: Automated verification using satellite imagery
- **International Standards**: Integration with global carbon registries
- **Payment Gateway**: Fiat currency integration for credit purchases

### 👥 **Team & Contact**

**Project Team**: [Your Team Name]
**Institution**: [Your Institution]
**Contact**: [Your Contact Information]
**SIH 2025 Problem Statement**: 25038 - Blockchain-Based Blue Carbon Registry and MRV System

---

### 🚀 **Ready for SIH 2025 Evaluation!**

This comprehensive blockchain-based blue carbon registry demonstrates the complete solution for Problem Statement 25038, providing a production-ready platform for transparent, verifiable carbon credit generation from coastal ecosystem restoration projects.

**Key Deliverables:**
- ✅ Functional blockchain application
- ✅ Smart contracts for credit tokenization
- ✅ MRV system with field data integration
- ✅ Multi-stakeholder onboarding capability
- ✅ NCCR admin tools and oversight
- ✅ Demo data and complete documentation