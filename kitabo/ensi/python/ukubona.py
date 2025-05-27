import os
import subprocess
import sys
from pathlib import Path
import argparse
import shlex

def run(cmd, cwd=None, check_error=True):
    print(f"▶️ {cmd}")
    result = subprocess.run(cmd, shell=True, text=True, cwd=cwd, capture_output=True)
    if result.returncode != 0:
        if check_error:
            print(f"❌ Error:\n{result.stderr.strip()}")
            sys.exit(1)
        else:
            print(f"⚠️ Warning:\n{result.stderr.strip()}")
    return result.stdout.strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy folder with index.html to any branch.")
    parser.add_argument("folder", help="Path to folder with index.html")
    parser.add_argument("--branch", default="gh-pages", help="Target branch (default: gh-pages)")
    parser.add_argument("--message", default="2 Chronicles 16:9 as mission", help="Commit message")
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    branch = args.branch
    message = args.message
    index_path = folder / "index.html"

    if not index_path.exists():
        print(f"❌ No index.html found in: {folder}")
        sys.exit(1)

    print(f"\n📦 Folder: {folder}")
    print(f"🌿 Branch: {branch}")
    print(f"📝 Commit message: {message}\n")

    if branch == "gh-pages":
        run(f"ghp-import -n -p -f -m {shlex.quote(message)} {shlex.quote(str(folder))}")
    else:
        run(f"git add {shlex.quote(os.path.relpath(index_path))}")
        Path(".nojekyll").touch(exist_ok=True)
        run("git add .nojekyll")
        commit_output = run(f"git commit -m {shlex.quote(message)}", check_error=False)
        if "nothing to commit" in commit_output.lower():
            print("⚠️ No new changes to commit.")
        else:
            print(commit_output)
        run(f"git push origin {branch}")

    print(f"✅ Done. {os.path.relpath(index_path)} pushed to {branch}.\n")     
