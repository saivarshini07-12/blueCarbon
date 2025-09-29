"""
FastAPI Backend Service for Blockchain Blue Carbon Registry
This provides REST API endpoints for the blockchain MRV system
Run with: uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
from datetime import datetime
import uvicorn

from blockchain_mrv import blockchain_mrv, BlueCarbonProject, VerificationRecord, CarbonCredit

# Initialize FastAPI app
app = FastAPI(
    title="Blue Carbon Registry API",
    description="Blockchain-based Blue Carbon Registry and MRV System for SIH 2025",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ProjectCreate(BaseModel):
    name: str
    location: str
    area: float
    ecosystem_type: str
    estimated_sequestration: float
    owner: str
    additional_data: Dict = {}

class VerificationCreate(BaseModel):
    project_id: int
    verified_amount: float
    verifier: str
    verification_data: Dict
    comments: str = ""

class EmissionRecord(BaseModel):
    company_address: str
    emissions: float

class CreditPurchase(BaseModel):
    buyer: str
    seller: str
    amount: float
    price_per_ton: float

# API Endpoints

@app.get("/")
async def root():
    """API Health Check"""
    return {
        "message": "Blue Carbon Registry API",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/projects")
async def get_all_projects():
    """Get all registered blue carbon projects"""
    projects = blockchain_mrv.get_all_projects()
    return {
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "location": p.location,
                "area": p.area,
                "ecosystem_type": p.ecosystem_type,
                "owner": p.owner,
                "estimated_carbon_sequestration": p.estimated_carbon_sequestration,
                "created_at": p.created_at.isoformat(),
                "status": p.status,
                "ipfs_hash": p.ipfs_hash
            } for p in projects
        ],
        "total": len(projects)
    }

@app.post("/api/projects")
async def create_project(project: ProjectCreate):
    """Register a new blue carbon project"""
    try:
        project_id = blockchain_mrv.register_blue_carbon_project(
            name=project.name,
            location=project.location,
            area=project.area,
            ecosystem_type=project.ecosystem_type,
            estimated_sequestration=project.estimated_sequestration,
            owner=project.owner,
            project_data=project.additional_data
        )
        return {
            "success": True,
            "project_id": project_id,
            "message": f"Project '{project.name}' registered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/projects/{project_id}")
async def get_project(project_id: int):
    """Get details of a specific project"""
    project = blockchain_mrv.get_project_details(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    verifications = blockchain_mrv.get_verification_records(project_id)
    
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "location": project.location,
            "area": project.area,
            "ecosystem_type": project.ecosystem_type,
            "owner": project.owner,
            "estimated_carbon_sequestration": project.estimated_carbon_sequestration,
            "created_at": project.created_at.isoformat(),
            "status": project.status,
            "ipfs_hash": project.ipfs_hash
        },
        "verifications": [
            {
                "id": v.id,
                "verified_amount": v.verified_carbon_amount,
                "verifier": v.verifier,
                "verification_date": v.verification_date.isoformat(),
                "is_approved": v.is_approved,
                "comments": v.comments
            } for v in verifications
        ]
    }

@app.post("/api/verifications")
async def submit_verification(verification: VerificationCreate):
    """Submit verification for a project"""
    try:
        verification_id = blockchain_mrv.submit_verification(
            project_id=verification.project_id,
            verified_amount=verification.verified_amount,
            verifier=verification.verifier,
            verification_data=verification.verification_data,
            comments=verification.comments
        )
        return {
            "success": True,
            "verification_id": verification_id,
            "message": "Verification submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/verifications/{verification_id}/approve")
async def approve_verification(verification_id: int):
    """Approve verification and issue carbon credits"""
    try:
        result = blockchain_mrv.approve_verification_and_issue_credits(verification_id)
        if result:
            return {
                "success": True,
                "message": "Verification approved and carbon credits issued"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to approve verification")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/emissions")
async def record_emissions(emission: EmissionRecord):
    """Record company emissions"""
    try:
        blockchain_mrv.record_company_emissions(
            emission.company_address,
            emission.emissions
        )
        return {
            "success": True,
            "message": f"Recorded {emission.emissions} tons CO2 for {emission.company_address}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/companies/{company_address}/dashboard")
async def get_company_dashboard(company_address: str):
    """Get comprehensive dashboard data for a company"""
    try:
        dashboard_data = blockchain_mrv.get_company_dashboard_data(company_address)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/marketplace")
async def get_marketplace_listings():
    """Get available carbon credits in marketplace"""
    try:
        listings = blockchain_mrv.get_marketplace_listings()
        return {
            "listings": listings,
            "total": len(listings)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/marketplace/purchase")
async def purchase_credits(purchase: CreditPurchase):
    """Purchase carbon credits from marketplace"""
    try:
        result = blockchain_mrv.purchase_carbon_credits(
            buyer=purchase.buyer,
            seller=purchase.seller,
            amount=purchase.amount,
            price_per_ton=purchase.price_per_ton
        )
        if result:
            return {
                "success": True,
                "message": f"Successfully purchased {purchase.amount} credits from {purchase.seller}"
            }
        else:
            raise HTTPException(status_code=400, detail="Purchase failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/stats")
async def get_system_stats():
    """Get overall system statistics"""
    projects = blockchain_mrv.get_all_projects()
    verifications = list(blockchain_mrv.verifications.values())
    pending_verifications = [v for v in verifications if not v.is_approved]
    total_credits = sum(blockchain_mrv.get_company_carbon_balance(addr) for addr in blockchain_mrv.carbon_credits.keys())
    total_emissions = sum(blockchain_mrv.company_emissions.values())
    
    return {
        "total_projects": len(projects),
        "total_verifications": len(verifications),
        "pending_verifications": len(pending_verifications),
        "total_credits_issued": total_credits,
        "total_emissions_recorded": total_emissions,
        "active_companies": len(blockchain_mrv.carbon_credits.keys()),
        "ecosystem_distribution": {
            "mangrove": len([p for p in projects if p.ecosystem_type == "mangrove"]),
            "seagrass": len([p for p in projects if p.ecosystem_type == "seagrass"]),
            "salt_marsh": len([p for p in projects if p.ecosystem_type == "salt_marsh"]),
            "coastal_wetland": len([p for p in projects if p.ecosystem_type == "coastal_wetland"])
        }
    }

# Background task to populate demo data
@app.post("/api/admin/populate-demo")
async def populate_demo_data(background_tasks: BackgroundTasks):
    """Populate system with demo data (Admin only)"""
    background_tasks.add_task(run_demo_population)
    return {
        "success": True,
        "message": "Demo data population started in background"
    }

def run_demo_population():
    """Background task to populate demo data"""
    try:
        from demo_populate import populate_demo_data
        populate_demo_data()
        print("✅ Demo data populated successfully")
    except Exception as e:
        print(f"❌ Error populating demo data: {e}")

if __name__ == "__main__":
    print("🚀 Starting Blue Carbon Registry API Server...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🌊 Blockchain MRV System: http://localhost:8000/api/stats")
    
    # Auto-populate demo data on startup
    try:
        from demo_populate import populate_demo_data
        populate_demo_data()
    except Exception as e:
        print(f"Warning: Could not populate demo data: {e}")
    
    uvicorn.run(
        "backend_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )