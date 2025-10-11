import os
import sys
import subprocess
import fcntl

LOCK_FILE = "/tmp/ai_rtsp.lock"

def single_instance_lock():
    """Prevent multiple instances of this script from running."""
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
        return lock_fd  # keep lock open while running
    except IOError:
        print("⚠️ Another instance is already running. Exiting...")
        sys.exit(0)

def update_code():
    repo_dir = "/home/jetson/yourrepo"  # path to your repo
    branch = "main"
    try:
        os.chdir(repo_dir)
        print("🔄 Fetching latest code from GitHub...")
        subprocess.run(["git", "fetch", "--all"], check=True)
        subprocess.run(["git", "reset", "--hard", f"origin/{branch}"], check=True)
        subprocess.run(["git", "pull"], check=True)
        print("✅ Code updated successfully.\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git update failed: {e}")
        return False

if __name__ == "__main__":
    # 🔐 Acquire lock to ensure single instance
    lock_fd = single_instance_lock()

    # 🔄 Update code
    updated = update_code()

    if updated:
        print("♻️ Restarting with updated code...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    # 🧠 Main script logic (after update)
    print("🚀 Running AI RTSP processing...")
    # your ai_rtsp code here...

    # ⚠️ Lock will automatically release on exit
