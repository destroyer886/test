import os
import sys
import subprocess
import time
import fcntl
import socket

LOCK_FILE = "/tmp/ai_rtsp.lock"
REPO_URL = "https://github.com/destroyer886/test.git"
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
BRANCH = "main"


def single_instance_lock():
    """Prevents multiple instances of this script."""
    global lock_fd
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
    except BlockingIOError:
        print("⚠️ Another instance is already running. Exiting...")
        sys.exit(0)


def internet_available(host="8.8.8.8", port=53, timeout=5, retries=3):
    """Check if internet is available (with retries)."""
    for attempt in range(retries):
        try:
            socket.setdefaulttimeout(timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.close()
            return True
        except Exception:
            print(f"🌐 Internet check failed (attempt {attempt + 1}/{retries})...")
            time.sleep(2)
    return False


def get_commit_hash():
    """Get current commit hash (None if not a git repo)."""
    git_dir = os.path.join(LOCAL_DIR, ".git")
    if not os.path.exists(git_dir):
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=LOCAL_DIR,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return result.stdout.strip()
    except subprocess.SubprocessError:
        return None


def update_repo():
    """Update repo if possible; handle weak or no internet gracefully."""
    if not internet_available():
        print("🌐 No or weak internet connection. Running existing code...")
        return False

    old_commit = get_commit_hash()
    if not old_commit:
        print("📦 No git repo found — trying to clone...")
        try:
            subprocess.run(
                ["git", "clone", REPO_URL, LOCAL_DIR],
                check=True,
                timeout=60
            )
            return True
        except subprocess.SubprocessError:
            print("❌ Clone failed (weak or no internet). Running existing code.")
            return False

    try:
        print("🔄 Checking for updates (may take a few seconds)...")
        subprocess.run(
            ["git", "fetch", "origin", BRANCH],
            cwd=LOCAL_DIR,
            check=True,
            timeout=30
        )

        new_commit = subprocess.run(
            ["git", "rev-parse", f"origin/{BRANCH}"],
            cwd=LOCAL_DIR,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        ).stdout.strip()

        if new_commit != old_commit:
            print("✅ Update found! Pulling latest code...")
            subprocess.run(
                ["git", "reset", "--hard", f"origin/{BRANCH}"],
                cwd=LOCAL_DIR,
                check=True,
                timeout=20
            )
            return True
        else:
            print("✅ Code is up to date.")
            return False

    except subprocess.TimeoutExpired:
        print("⏱ Git command timed out — slow internet. Running current code.")
        return False
    except subprocess.SubprocessError as e:
        print(f"❌ Git update failed: {e}. Running existing code.")
        return False


if __name__ == "__main__":
    single_instance_lock()

    updated = update_repo()
    if updated:
        print("♻️ Restarting with new code...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    print("🚀 Running AI RTSP logic...")
    try:
        while True:
            print("🧩 Processing RTSP stream... updated, filecheck, again")
            time.sleep(3)
    except KeyboardInterrupt:
        print("👋 Exiting cleanly.")
