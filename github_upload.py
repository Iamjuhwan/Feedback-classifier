import os
import getpass
from github import Github, GithubException

token = getpass.getpass("Paste your GitHub token here (won't be shown): ")
g = Github(token)
repo = g.get_repo("Iamjuhwan/Feedback-classifier")

ROOT = "."
SKIP_DIR_NAMES = {".git", "__pycache__", "afro-xlmr-health-feedback"}

uploaded, failed = 0, 0

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [
        d for d in dirnames
        if d not in SKIP_DIR_NAMES and not d.startswith("checkpoint-")
    ]
    for fname in filenames:
        full_path = os.path.join(dirpath, fname)
        rel_path = os.path.relpath(full_path, ROOT).replace("\\", "/")
        if rel_path.startswith(".git/") or rel_path == ".":
            continue
        with open(full_path, "rb") as f:
            content = f.read()
        try:
            repo.create_file(rel_path, f"Add {rel_path}", content)
            print(f"Uploaded: {rel_path}")
            uploaded += 1
        except GithubException as e:
            print(f"FAILED: {rel_path} -> {e.data.get('message', e)}")
            failed += 1

print(f"\nDone. {uploaded} uploaded, {failed} failed.")
