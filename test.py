import os
import sys
import subprocess
import time
import fcntl

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


def get_commit_hash():
    """Returns the current git commit hash, or None if not a git repo."""
    git_dir = os.path.join(LOCAL_DIR, ".git")
    if not os.path.exists(git_dir):
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=LOCAL_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def update_repo():
    """Pull latest code and return True if updated, else False."""
    old_commit = get_commit_hash()
    if not old_commit:
        print("📦 Cloning repository...")
        subprocess.run(["git", "clone", REPO_URL, LOCAL_DIR], check=True)
        return True

    print("🔄 Checking for updates...")
    subprocess.run(["git", "fetch", "origin", BRANCH], cwd=LOCAL_DIR, check=True)
    new_commit = subprocess.run(
        ["git", "rev-parse", f"origin/{BRANCH}"],
        cwd=LOCAL_DIR,
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()

    if new_commit != old_commit:
        print("✅ Update found! Pulling latest code...")
        subprocess.run(["git", "reset", "--hard", f"origin/{BRANCH}"], cwd=LOCAL_DIR, check=True)
        return True
    else:
        print("✅ Code is up to date.")
        return False


if __name__ == "__main__":
    single_instance_lock()
    updated = update_repo()

    if updated:
        print("♻️ Restarting with new code...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    print("🚀 Running main logic here...")
    # ---------------------------
    # Your actual code below
    # ---------------------------
    try:
        while True:
            print("🧠 AI RTSP running...")
            time.sleep(3)
    except KeyboardInterrupt:
        print("👋 Exiting cleanly.")
