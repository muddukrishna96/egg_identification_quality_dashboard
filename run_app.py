import subprocess
import time
import sys
import os

def run_backend():
    """Start the FastAPI backend using uvicorn."""
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ]
    return subprocess.Popen(backend_cmd)

def run_frontend():
    """Start the Streamlit frontend."""
    frontend_path = os.path.join("frontend", "app.py")
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", frontend_path]
    return subprocess.Popen(frontend_cmd)

if __name__ == "__main__":
    print("🚀 Starting EggCounting System...")
    print("===================================")

    # Start backend
    print("⚙️  Launching FastAPI backend...")
    backend_proc = run_backend()
    time.sleep(3)  # Give backend a few seconds to start

    # Start frontend
    print("🧠 Launching Streamlit frontend...")
    frontend_proc = run_frontend()

    print("\n✅ Both backend and frontend are running.")
    print("   → Frontend: http://localhost:8501")
    print("   → Backend:  http://127.0.0.1:8000\n")
    print("Press Ctrl+C to stop both.\n")

    try:
        # Keep both processes alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping both processes...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("✅ Clean exit.")
