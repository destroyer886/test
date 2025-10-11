import os
import sys
import subprocess
import shutil

LOCK_FILE = "/tmp/ai_rtsp.pid"
REPO_URL = "https://github.com/destroyer886/test.git"
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))  # current folder
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

def clear_folder(folder):
    """Delete all files/folders in folder except this script."""
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if item_path == os.path.abspath(__file__):
            continue
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

def update_code():
    git_folder = os.path.join(LOCAL_DIR, ".git")

    if os.path.exists(git_folder):
        # Pull latest changes
        print("🔄 Pulling latest code from GitHub...")
        os.chdir(LOCAL_DIR)
        subprocess.run(["git", "fetch", "--all"], check=True)
        subprocess.run(["git", "reset", "--hard", f"origin/{BRANCH}"], check=True)
        subprocess.run(["git", "pull"], check=True)
    else:
        # Clean folder except the script
        print("🗑️ Clearing folder before clone...")
        clear_folder(LOCAL_DIR)
        # Clone into the same folder
        print("📦 Cloning repository into current folder...")
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
