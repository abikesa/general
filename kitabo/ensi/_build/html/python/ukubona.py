import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import shlex
import argparse

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

def deploy_gh_pages(folder: Path, msg: str):
    if not folder.exists() or not (folder / "index.html").exists():
        print(f"❌ Invalid target: {folder}")
        sys.exit(1)

    print(f"\n🌍 Deploying to `gh-pages`: {folder}")
    cmd = f"ghp-import -n -p -f -m {shlex.quote(msg)} {shlex.quote(str(folder))}"
    run(cmd)
    print("✅ gh-pages deployment complete.\n")

def deploy_main(folder: Path, msg: str):
    if not folder.exists() or not (folder / "index.html").exists():
        print(f"❌ Invalid target: {folder}")
        sys.exit(1)

    print(f"\n🌐 Deploying to `main`: {folder}")
    run(f"git add {shlex.quote(str(folder / 'index.html'))}")
    quoted_msg = shlex.quote(msg)
    commit_output = run(f"git commit -m {quoted_msg}", check_error=False)

    if "nothing to commit" in commit_output.lower():
        print("⚠️ No new changes to commit.")
    else:
        print(commit_output)
        run("git push")
    print("✅ main branch commit complete.\n")

def summarize_folder(folder: Path):
    print(f"\n📦 Summary of folder: {folder}")
    total_files = sum(len(filenames) for _, _, filenames in os.walk(folder))
    print(f"🗂️  Total files: {total_files}")
    print("🕰️ ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def main():
    parser = argparse.ArgumentParser(description="Deploy Ukubona index.html to gh-pages or main.")
    parser.add_argument("folder", help="Target folder containing index.html")
    parser.add_argument("--branch", choices=["main", "gh-pages"], default="gh-pages", help="Branch to deploy to")
    parser.add_argument("--message", default="2 Chronicles 16:9 as mission", help="Commit message")

    args = parser.parse_args()
    target = Path(args.folder).resolve()

    summarize_folder(target)

    if args.branch == "gh-pages":
        deploy_gh_pages(target, args.message)
    elif args.branch == "main":
        deploy_main(target, args.message)

if __name__ == "__main__":
    main()
