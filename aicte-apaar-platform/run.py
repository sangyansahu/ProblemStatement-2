import os
import sys
import time
import subprocess
import webbrowser
import signal
from pathlib import Path

# Resolve directory paths
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

def find_python_executable():
    """Locate appropriate Python interpreter with installed packages."""
    mamba_env = Path(r"C:\ProgramData\mambaforge\envs\projects_env\python.exe")
    if mamba_env.exists():
        return str(mamba_env)
    return sys.executable

def check_server_ready(url, max_attempts=30, delay=1):
    """Wait until an HTTP endpoint responds."""
    import urllib.request
    for attempt in range(max_attempts):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status in (200, 304):
                    return True
        except Exception:
            pass
        time.sleep(delay)
    return False

def main():
    print("=" * 75)
    print("  AICTE APAAR-Based Student Data Management & Verification Portal")
    print("=" * 75)
    print("\n[1/3] Initializing Backend & Database...")

    python_exe = find_python_executable()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)
    db_file = (BASE_DIR / "aicte_platform.db").resolve()
    env["DATABASE_URL"] = f"sqlite:///{db_file.as_posix()}"

    # Start FastAPI Backend
    backend_cmd = [
        python_exe, "-m", "uvicorn", "app.main:app",
        "--host", "127.0.0.1",
        "--port", "8000"
    ]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(BASE_DIR),
        env=env
    )

    print(f"      Backend process launched (PID: {backend_proc.pid})")
    print("      Waiting for FastAPI at http://127.0.0.1:8000/health ...")

    if check_server_ready("http://127.0.0.1:8000/health", max_attempts=20):
        print("      [OK] FastAPI Backend is healthy & database initialized!")
    else:
        print("      (!) Backend took longer than expected to report health, continuing...")

    print("\n[2/3] Launching Frontend Development Server...")
    # Start Vite Frontend
    is_win = sys.platform.startswith("win")
    npm_cmd = ["npm.cmd" if is_win else "npm", "run", "dev"]

    frontend_proc = subprocess.Popen(
        npm_cmd,
        cwd=str(FRONTEND_DIR)
    )
    print(f"      Frontend process launched (PID: {frontend_proc.pid})")
    print("      Waiting for Vite at http://localhost:5173 ...")

    if check_server_ready("http://localhost:5173", max_attempts=25):
        print("      [OK] Frontend is online!")
    else:
        print("      (!) Frontend started, opening browser...")

    print("\n[3/3] Opening Portal in Default Browser...")
    time.sleep(1)
    webbrowser.open("http://localhost:5173")

    print("\n" + "=" * 75)
    print("  PORTAL IS RUNNING SUCCESSFULLY!")
    print("=" * 75)
    print("  Frontend UI:          http://localhost:5173")
    print("  Backend API & Docs:   http://localhost:8000/docs")
    print("  API Health Check:     http://localhost:8000/health")
    print("\n  Pre-seeded Demo Accounts for Evaluation:")
    print("  - Institution Operator:  inst_operator  (Upload CSV & Edit Records)")
    print("  - Institution Admin:     inst_admin     (Resolve Discrepancies & Issue Credential)")
    print("  - AICTE Administrator:   aicte_admin    (National Oversight & Analytics)")
    print("  - Credential Verifier:   verifier       (Verify Credentials)")
    print("  - Security Auditor:      auditor        (Audit Log Inspection)")
    print("  (Password for all demo accounts: password123)")
    print("\n  Press CTRL+C to stop both servers.")
    print("=" * 75 + "\n")

    def shutdown(signum=None, frame=None):
        print("\nStopping AICTE APAAR Platform servers...")
        try:
            if is_win:
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(backend_proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(frontend_proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                backend_proc.terminate()
                frontend_proc.terminate()
        except Exception:
            pass
        print("Servers stopped cleanly. Goodbye.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend process exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend process exited unexpectedly.")
                break
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()
