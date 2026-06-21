#!/usr/bin/env python3
import subprocess
import os
import sys

def run_command(cmd, check=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def main():
    print("🚀 Starting GitHub upload process...")
    
    # GitHub credentials
    username = "Aj-Niplex"
    token = "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"
    repo = "Rei-kun-Discord-Bot"
    
    # Git config
    print("⚙️  Configuring git...")
    run_command('git config --global user.name "Aj-Niplex"', check=False)
    run_command('git config --global user.email "aj@niplex.com"', check=False)
    
    # Initialize repo if needed
    print("📦 Initializing repository...")
    if not os.path.exists('.git'):
        out, err, code = run_command('git init', check=False)
        print(f"   {out if out else err}")
    
    # Add remote
    print("🔗 Setting up remote...")
    run_command('git remote remove origin', check=False)
    remote_url = f"https://{username}:{token}@github.com/{username}/{repo}.git"
    out, err, code = run_command(f'git remote add origin {remote_url}', check=False)
    
    # Add all files
    print("📝 Adding files...")
    out, err, code = run_command('git add .', check=False)
    print(f"   Added all files (respecting .gitignore)")
    
    # Commit
    print("💾 Creating commit...")
    commit_msg = "Updated Rei-kun v7.0.0 - Removed slash commands, added animations, restored logging system"
    out, err, code = run_command(f'git commit -m "{commit_msg}"', check=False)
    if code == 0:
        print(f"   ✅ Commit created: {commit_msg}")
    else:
        print(f"   ℹ️  {out if out else err}")
    
    # Push to main
    print("⬆️  Pushing to GitHub...")
    out, err, code = run_command('git push -u origin main --force', check=False)
    
    if code == 0:
        print(f"\n✅ SUCCESS! Code uploaded to:")
        print(f"   https://github.com/{username}/{repo}")
    else:
        # Try master branch
        print("   Trying master branch...")
        out2, err2, code2 = run_command('git push -u origin master --force', check=False)
        if code2 == 0:
            print(f"\n✅ SUCCESS! Code uploaded to:")
            print(f"   https://github.com/{username}/{repo}")
        else:
            print(f"\n❌ Push failed:")
            print(f"   {err if err else out}")
            print(f"   {err2 if err2 else out2}")
            sys.exit(1)
    
    print("\n🎉 GitHub upload complete!")

if __name__ == "__main__":
    main()
