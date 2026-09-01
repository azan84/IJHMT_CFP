#!/usr/bin/env python3
"""
Automated Git Synchronization Engine for IJHMT_CFP.
Performs:
1. Ensure git user.name and user.email are set (sets fallback if unconfigured).
2. Pull updates from origin/main.
3. Stage results and postprocessing outputs.
4. Commit and push updates to github.com/azan84/IJHMT_CFP.
"""

import os
import sys
import subprocess

def ensure_git_identity(repo_root):
    try:
        name_check = subprocess.run(["git", "config", "user.name"], cwd=repo_root, capture_output=True, text=True)
        if not name_check.stdout.strip():
            subprocess.run(["git", "config", "user.name", "azan84"], cwd=repo_root, check=True)
            
        email_check = subprocess.run(["git", "config", "user.email"], cwd=repo_root, capture_output=True, text=True)
        if not email_check.stdout.strip():
            subprocess.run(["git", "config", "user.email", "azan84@users.noreply.github.com"], cwd=repo_root, check=True)
    except Exception:
        pass

def get_current_branch(repo_root):
    try:
        res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root, capture_output=True, text=True)
        branch = res.stdout.strip()
        return branch if branch else "main"
    except Exception:
        return "main"

def git_pull(repo_root):
    ensure_git_identity(repo_root)
    branch = get_current_branch(repo_root)
    try:
        res = subprocess.run(["git", "pull", "--rebase", "origin", branch], cwd=repo_root, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[GIT PULL] Successfully updated local repository from origin/{branch}.")
            return True
        else:
            print(f"[GIT PULL WARN] {res.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[GIT PULL ERROR] {e}")
        return False

def git_push_results(repo_root, completed_count, total_count):
    ensure_git_identity(repo_root)
    branch = get_current_branch(repo_root)
    try:
        # Rebase pull first
        subprocess.run(["git", "pull", "--rebase", "origin", branch], cwd=repo_root, capture_output=True, text=True)
        
        # Stage results and simulations folder
        subprocess.run(["git", "add", "parametric_campaign/results/", "simulations/"], cwd=repo_root, check=True)
        
        status_res = subprocess.run(["git", "status", "--porcelain", "parametric_campaign/results/", "simulations/"], cwd=repo_root, capture_output=True, text=True)
        if not status_res.stdout.strip():
            return True
            
        commit_msg = f"feat(parametric): auto-update DOE campaign results [{completed_count}/{total_count} completed]"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_root, check=True)
        
        push_res = subprocess.run(["git", "push", "origin", branch], cwd=repo_root, capture_output=True, text=True)
        if push_res.returncode == 0:
            print(f"[GIT PUSH SUCCESS] Pushed {completed_count}/{total_count} results to origin/{branch}.")
            return True
        else:
            print(f"[GIT PUSH WARN] {push_res.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[GIT PUSH ERROR] {e}")
        return False

if __name__ == "__main__":
    r_root = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    git_pull(r_root)
