import os
import sys
import subprocess

LOCK_FILE = "/tmp/ai_rtsp.pid"
REPO_URL = "https://github.com/destroyer886/test.git"
LOCAL_DIR = "../"  # temporary local folder for the repo
BRANCH = "main"

def single_instance_lock():
    """Prevent multiple instances of this script from running."""
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, "r") as f:
            pid = f.read().strip()
            if pid and pid.isdigit():
                try:
                    os.kill(int(pid), 0)
                    print("⚠️ Another instance is already running. Exiting...")
                    sys.exit(0)
                except ProcessLookupError:
                    pass  # PID not running, safe to proceed

    # Write current PID to lock file
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

def update_code():
    """Clone or pull the repo from GitHub."""
    if not os.path.exists(LOCAL_DIR):
        print("📦 Cloning repository from GitHub...")
        subprocess.run(["git", "clone", REPO_URL, LOCAL_DIR], check=True)
    else:
        print("🔄 Pulling latest code from GitHub...")
        os.chdir(LOCAL_DIR)
        subprocess.run(["git", "fetch", "--all"], check=True)
        subprocess.run(["git", "reset", "--hard", f"origin/{BRANCH}"], check=True)
        subprocess.run(["git", "pull"], check=True)
    
    print("✅ Code is up to date.\n")
    return True

if __name__ == "__main__":
    # 🔐 Acquire lock to ensure single instance
    single_instance_lock()

    # 🔄 Update code
    updated = update_code()

    if updated:
        print("♻️ Restarting with updated code...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    # 🧠 Main script logic (after update)
    print("🚀 Running AI RTSP processing...")
    # your ai_rtsp code here...
