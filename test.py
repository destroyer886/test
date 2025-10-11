import os
import sys
import subprocess
import shutil

LOCK_FILE = "/tmp/ai_rtsp.pid"
REPO_URL = "https://github.com/destroyer886/test.git"
LOCAL_DIR = "../"
BRANCH = "main"

def single_instance_lock():
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, "r") as f:
            pid = f.read().strip()
            if pid and pid.isdigit():
                try:
                    os.kill(int(pid), 0)
                    print("⚠️ Another instance is already running. Exiting...")
                    sys.exit(0)
                except ProcessLookupError:
                    pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

def update_code():
    """Always overwrite local files with latest GitHub repo."""
    if os.path.exists(LOCAL_DIR):
        print("🗑️ Removing existing repo folder...")
        shutil.rmtree(LOCAL_DIR)

    print("📦 Cloning repository from GitHub...")
    subprocess.run(["git", "clone", REPO_URL, LOCAL_DIR], check=True)
    print("✅ Code is up to date.\n")
    return True

if __name__ == "__main__":
    single_instance_lock()
    updated = update_code()
    if updated:
        print("♻️ Restarting with updated code...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    print("🚀 Running AI RTSP processing...")
    # your ai_rtsp code here...
