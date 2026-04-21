import os
import subprocess
import sys
import time

def run_project():
    print("🚀 Starting GRsimulator...")
    
    # Start Backend
    print("🔧 Starting Backend...")
    backend_proc = subprocess.Popen(
        ["uvicorn", "app.main:app", "--reload", "--port", "8000"],
        cwd="backend"
    )
    
    # Wait for backend to warm up
    time.sleep(2)
    
    # Start Frontend
    print("🎨 Starting Frontend...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd="ui",
        shell=True
    )
    
    try:
        # Keep main process alive
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping GRsimulator...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    run_project()
