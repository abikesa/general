#!/usr/bin/env python3

import subprocess
import shutil
import os
import sys
from pathlib import Path
import click

def run(cmd, check=True, capture_output=False, cwd=None):
    print(f"⚙️  {cmd}")
    result = subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True, cwd=cwd)
    if capture_output:
        return result.stdout.strip()
    return result.returncode

def branch_exists(branch):
    try:
        run(f"git rev-parse --verify {branch}", capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def remote_exists(remote):
    remotes = run("git remote", capture_output=True).split()
    return remote in remotes

@click.command()
@click.option('--commit-message', prompt="📜 Enter your commit message", help="The Git commit message.")
@click.option('--git-remote', prompt="🛰️ Enter the Git remote to push to", default="origin", show_default=True, help="Git remote name.")
@click.option('--ghp-remote', default="origin", show_default=True, help="Remote for ghp-import deployment.")
def main(commit_message, git_remote, ghp_remote):
    os.chdir(Path(__file__).resolve().parents[1])

    current_branch = run("git rev-parse --abbrev-ref HEAD", capture_output=True).strip()
    git_branch = click.prompt("🌿 Enter the Git branch to push to", default=current_branch, show_default=True)

    if current_branch != git_branch:
        click.secho(f"⚠️  You are on branch '{current_branch}', but trying to push to '{git_branch}'.", fg="yellow")
        if not click.confirm("Continue anyway?", default=False):
            click.secho("🛑 Aborting.", fg="red")
            sys.exit(1)

    if not branch_exists(git_branch):
        click.secho(f"🌱 Local branch '{git_branch}' does not exist.", fg="yellow")
        if click.confirm(f"Create and switch to '{git_branch}'?", default=True):
            run(f"git checkout -b {git_branch}")
        else:
            click.secho("🛑 Aborting.", fg="red")
            sys.exit(1)

    if not remote_exists(git_remote):
        click.secho(f"🔗 Remote '{git_remote}' not found.", fg="yellow")
        if click.confirm(f"Add remote '{git_remote}'?", default=True):
            remote_url = click.prompt("🌍 Enter remote URL (e.g. git@github.com:user/repo.git)")
            run(f"git remote add {git_remote} {remote_url}")
        else:
            click.secho("🛑 Aborting.", fg="red")
            sys.exit(1)

    try:
        run(f"git ls-remote --exit-code --heads {git_remote} {git_branch}", capture_output=True)
        remote_branch_exists = True
    except subprocess.CalledProcessError:
        remote_branch_exists = False

    if git_branch == "main":
        confirm = click.prompt("⚠️  WARNING: pushing to 'main'. Type 'confirm' to continue", default="", show_default=False)
        if confirm != "confirm":
            click.secho("🛑 Cancelled push to 'main'.", fg="red")
            sys.exit(1)

    click.secho("🧼 Cleaning Jupyter Book...", fg="cyan")
    run("jb clean .")
    if os.path.exists("bash/bash_clean.sh"):
        run("bash/bash_clean.sh")

    click.secho("🏗️ Building Jupyter Book...", fg="cyan")
    run("jb build .")

    click.secho("📦 Copying extra folders...", fg="cyan")
    extras = [
        "pdfs", "figures", "media", "testbin", "nis", "myhtml", "dedication", "python", "ai",
        "r", "stata", "bash", "xml", "data", "aperitivo", "antipasto", "primo", "secondo",
        "contorno", "insalata", "formaggio-e-frutta", "dolce", "caffe", "digestivo", "ukubona",
        "the-rug", "spjd-rebuild", "spjd-beta", "ukuvula", "tokens", "ukuvela", "index", "wiki"
    ]
    for d in extras:
        if os.path.isdir(d):
            dest = os.path.join("_build/html", d)
            os.makedirs(dest, exist_ok=True)
            for item in os.listdir(d):
                s = os.path.join(d, item)
                d_ = os.path.join(dest, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d_, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d_)

    click.secho("🌿 Planting flicks...", fg="cyan")
    try:
        run("python python/plant_flicks_frac.py --percent 23")
    except Exception as e:
        click.secho(f"⚠️ Flick planting failed: {e}", fg="yellow")

    click.secho("🧾 Staging changes...", fg="cyan")
    run("git add .")

    click.secho("✍️ Committing...", fg="cyan")
    try:
        run(f"git commit -m \"{commit_message}\"")
    except subprocess.CalledProcessError:
        click.secho("⚠️ No changes to commit.", fg="yellow")

    if remote_branch_exists:
        click.secho("🔄 Fetching remote changes...", fg="cyan")
        try:
            run(f"git fetch {git_remote}")
        except subprocess.CalledProcessError:
            click.secho("🧹 Detected fetch error. Pruning remote refs and retrying...", fg="yellow")
            run(f"git remote prune {git_remote}")
            run(f"git fetch {git_remote}")

        click.secho("🔀 Rebasing local changes...", fg="cyan")
        try:
            run(f"git rebase {git_remote}/{git_branch}")
        except subprocess.CalledProcessError:
            click.secho("⚠️ Rebase failed. Resolve conflicts manually.", fg="red")
            sys.exit(1)
    else:
        click.secho(f"📤 Pushing new branch '{git_branch}' to remote...", fg="yellow")
        run(f"git push -u {git_remote} {git_branch}")

    click.secho(f"⬆️ Pushing to {git_remote}/{git_branch}...", fg="cyan")
    run(f"git push {git_remote} {git_branch}")

    click.secho("🌐 Checking for 'gh-pages' branch on remote...", fg="cyan")
    try:
        run(f"git ls-remote --exit-code --heads {git_remote} gh-pages", capture_output=True)
        click.secho("✅ Remote 'gh-pages' branch exists.", fg="green")
    except subprocess.CalledProcessError:
        click.secho("🆕 Remote 'gh-pages' branch will be created by ghp-import.", fg="yellow")

    click.secho("🚀 Deploying with ghp-import...", fg="cyan")

    if ghp_remote == "gh-pages":
        ghp_remote = "origin"

    run(f"ghp-import -n -p -f -b gh-pages -r {ghp_remote} _build/html")

if __name__ == "__main__":
    main()
