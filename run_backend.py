"""
Production-ready backend service runner
Combines Streamlit frontend with FastAPI backend for full-stack deployment
"""

import subprocess
import time
import threading
import os
import signal
import sys

def run_streamlit():
    """Run Streamlit frontend"""
    print("🎨 Starting Streamlit Frontend on port 8501...")
    try:
        subprocess.run([
            "python3", "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.enableCORS", "true",
            "--server.enableXsrfProtection", "false"
        ])
    except KeyboardInterrupt:
        print("🛑 Streamlit frontend stopped")

def run_fastapi():
    """Run FastAPI backend"""
    print("🚀 Starting FastAPI Backend on port 8000...")
    try:
        subprocess.run([
            "python3", "-m", "uvicorn", "backend_api:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("🛑 FastAPI backend stopped")

def populate_demo_data():
    """Populate demo data"""
    print("📊 Populating demo data...")
    try:
        subprocess.run(["python3", "demo_populate.py"])
        print("✅ Demo data populated successfully")
    except Exception as e:
        print(f"⚠️  Demo data population failed: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutdown signal received. Stopping all services...")
    sys.exit(0)

def main():
    """Run the complete backend system"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("🌊 BLUE CARBON REGISTRY - SIH 2025")
    print("   Blockchain-based Carbon Accounting System")
    print("=" * 60)
    
    # Populate demo data first
    populate_demo_data()
    
    print("\n🚀 Starting Full-Stack Application...")
    print("   📱 Frontend (Streamlit): http://localhost:8501")
    print("   🔗 Backend API (FastAPI): http://localhost:8000")
    print("   📚 API Docs: http://localhost:8000/docs")
    print("   📊 API Stats: http://localhost:8000/api/stats")
    
    # Create threads for both services
    streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    
    # Start both services
    streamlit_thread.start()
    time.sleep(2)  # Give Streamlit a head start
    fastapi_thread.start()
    
    print("\n✅ Both services are starting...")
    print("   Press Ctrl+C to stop all services")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all services...")

if __name__ == "__main__":
    main()