#!/usr/bin/env python3
"""
Automated Git Synchronization Engine for IJHMT_CFP.
Performs:
1. Pull updates from origin/main.
2. Stage results and postprocessing outputs.
3. Commit and push updates to github.com/azan84/IJHMT_CFP.
"""

import os
import sys
import subprocess

def git_pull(repo_root):
    try:
        res = subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=repo_root, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[GIT PULL] Successfully updated local repository from origin/main.")
            return True
        else:
            print(f"[GIT PULL WARN] {res.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[GIT PULL ERROR] {e}")
        return False

def git_push_results(repo_root, completed_count, total_count):
    try:
        # Stage results folder and case summaries
        subprocess.run(["git", "add", "parametric_campaign/results/"], cwd=repo_root, check=True)
        
        status_res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True)
        if not status_res.stdout.strip():
            print("[GIT PUSH] No changes to commit.")
            return True
            
        commit_msg = f"feat(parametric): auto-update DOE campaign results [{completed_count}/{total_count} completed]"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_root, check=True)
        
        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=repo_root, capture_output=True, text=True)
        if push_res.returncode == 0:
            print(f"[GIT PUSH SUCCESS] Pushed {completed_count}/{total_count} results to github.com/azan84/IJHMT_CFP.")
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
