import os
import sys
import subprocess
import shutil

LOCK_FILE = "/tmp/ai_rtsp.pid"
REPO_URL = "https://github.com/destroyer886/test.git"
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
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
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if item_path == os.path.abspath(__file__):
            continue
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

def get_current_commit():
    git_folder = os.path.join(LOCAL_DIR, ".git")
    if os.path.exists(git_folder):
        os.chdir(LOCAL_DIR)
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    return None

def update_code():
    """Pull latest changes or clone if folder is empty."""
    old_commit = get_current_commit()
    git_folder = os.path.join(LOCAL_DIR, ".git")

    if os.path.exists(git_folder):
        print("🔄 Pulling latest code from GitHub...")
        os.chdir(LOCAL_DIR)
        subprocess.run(["git", "fetch", "--all"], check=True)
        subprocess.run(["git", "reset", "--hard", f"origin/{BRANCH}"], check=True)
        subprocess.run(["git", "pull"], check=True)
    else:
        print("🗑️ Clearing folder before clone...")
        clear_folder(LOCAL_DIR)
        print("📦 Cloning repository into current folder...")
        subprocess.run(["git", "clone", REPO_URL, LOCAL_DIR], check=True)

    new_commit = get_current_commit()
    if old_commit != new_commit:
        print("✅ Code updated! New commit:", new_commit)
        return True  # restart needed
    else:
        print("✅ Code is up to date. No restart needed.")
        return False  # no restart

if __name__ == "__main__":
    single_instance_lock()
    updated = update_code()

    # Remove lock file before restarting
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

    if updated:
        print("♻️ Restarting with updated code...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    print("🚀 Running AI RTSP processing...")
