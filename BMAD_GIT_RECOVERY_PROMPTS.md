# BMAD v6 Git Recovery & Automation Fix Prompts

## Problem Analysis
- **Issue**: Massive Git state corruption with 1,817 dirty paths
- **Root Cause**: BMAD automation regenerating `bmad/**` → `src/modules/bmm/**` migration
- **Impact**: Auto-commit scripts failing due to massive file churn
- **Status**: Multiple safety stashes available for recovery

## 🎯 BMAD Codex CLI Recovery Prompts

### Phase 1: Repository State Assessment

```bash
# Prompt 1: Analyze Current Git State
cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import subprocess
import json
from pathlib import Path

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

print("🔍 BMAD v6 Git State Analysis")
print("=" * 50)

# Check stash list
stashes, _ = run_cmd("git stash list")
print(f"📦 Available Stashes:\n{stashes}\n")

# Check dirty files by category
status, _ = run_cmd("git status --porcelain")
dirty_files = status.split('\n') if status else []

bmad_files = [f for f in dirty_files if 'bmad/' in f]
bmm_files = [f for f in dirty_files if 'src/modules/bmm/' in f]
other_files = [f for f in dirty_files if 'bmad/' not in f and 'src/modules/bmm/' not in f]

print(f"📊 File Change Analysis:")
print(f"   BMAD files: {len(bmad_files)}")
print(f"   BMM module files: {len(bmm_files)}")
print(f"   Other files: {len(other_files)}")
print(f"   Total dirty: {len(dirty_files)}")

# Check if this is a migration
if bmad_files and bmm_files:
    print("\n🚨 DETECTED: BMAD → BMM Migration in Progress")
    print("   This appears to be a structural reorganization")
    
print(f"\n📋 Recommendation: {'MIGRATE' if len(bmad_files) > 100 else 'RESTORE'}")
EOF
```

### Phase 2: Clean Recovery Strategy

```bash
# Prompt 2: Execute Clean Recovery
cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import subprocess
import os
from pathlib import Path

def run_cmd(cmd, check=True):
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ Success: {result.stdout.strip()}")
    return True

print("🧹 BMAD v6 Clean Recovery Process")
print("=" * 50)

# Step 1: Create emergency backup
print("\n📦 Step 1: Emergency Backup")
run_cmd("git stash push -u -m 'emergency-backup-before-recovery'")

# Step 2: Hard reset to clean state
print("\n🔄 Step 2: Reset to Clean State")
run_cmd("git reset --hard origin/master")
run_cmd("git clean -fd")

# Step 3: Verify clean state
print("\n✅ Step 3: Verify Clean State")
status_out, _ = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True).stdout, ""
if not status_out.strip():
    print("✅ Repository is now clean")
else:
    print(f"⚠️  Still {len(status_out.strip().split())} dirty files")

# Step 4: Check for BMAD automation triggers
print("\n🔍 Step 4: Check Automation Triggers")
bmad_paths = [
    ".github/workflows",
    "tools/pr_workflow.py", 
    "tools/git-auto-commit-push.sh",
    "bmad/",
    "src/modules/bmm/"
]

for path in bmad_paths:
    if Path(path).exists():
        print(f"📁 Found: {path}")
    else:
        print(f"❌ Missing: {path}")

print("\n🎯 Next: Run Phase 3 to fix automation scripts")
EOF
```

### Phase 3: Fix Automation Scripts

```bash
# Prompt 3: Fix Git Auto-Commit Script
cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import re
from pathlib import Path

print("🔧 BMAD v6 Automation Script Fix")
print("=" * 50)

script_path = Path("tools/git-auto-commit-push.sh")
if not script_path.exists():
    print("❌ Script not found")
    exit(1)

# Read current script
content = script_path.read_text()

# Add exclusion patterns for problematic paths
exclusions = [
    "bmad/",
    "src/modules/bmm/", 
    "frontend/src/components/deals/",
    "*.lock",
    "node_modules/",
    ".git/"
]

# Create improved filtering function
filter_function = '''
# BMAD v6: Filter problematic paths
filter_paths() {
    local paths=("$@")
    local filtered=()
    
    for path in "${paths[@]}"; do
        # Skip problematic patterns
        if [[ "$path" =~ ^(bmad/|src/modules/bmm/|frontend/src/components/deals/|.*\.lock|node_modules/|\.git/) ]]; then
            echo "⚠️  Skipping problematic path: $path" >&2
            continue
        fi
        filtered+=("$path")
    done
    
    printf '%s\\n' "${filtered[@]}"
}
'''

# Insert filter function after shebang
lines = content.split('\n')
shebang_idx = 0
for i, line in enumerate(lines):
    if line.startswith('#!'):
        shebang_idx = i
        break

# Insert filter function
lines.insert(shebang_idx + 1, filter_function)

# Modify the staging logic to use filter
staging_pattern = r'git add -- "\${stage_paths\[@\]}"'
replacement = '''
# Filter paths before staging
filtered_paths=($(filter_paths "${stage_paths[@]}"))
if [ ${#filtered_paths[@]} -eq 0 ]; then
    echo "⚠️  No valid paths to stage after filtering"
    continue
fi
git add -- "${filtered_paths[@]}"'''

content = '\n'.join(lines)
content = re.sub(staging_pattern, replacement, content)

# Write fixed script
script_path.write_text(content)
print("✅ Fixed git-auto-commit-push.sh with path filtering")

# Make executable
import os
os.chmod(script_path, 0o755)
print("✅ Made script executable")

print("\n🎯 Next: Run Phase 4 to test the fix")
EOF
```

### Phase 4: Test & Validate Fix

```bash
# Prompt 4: Test Fixed Automation
cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import subprocess
import tempfile
from pathlib import Path

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

print("🧪 BMAD v6 Automation Test")
print("=" * 50)

# Step 1: Create test changes
print("\n📝 Step 1: Create Safe Test Changes")
test_file = Path("test_bmad_fix.md")
test_file.write_text("""# BMAD v6 Test File

This is a test file to validate the fixed automation.

- Created: $(date)
- Purpose: Test git-auto-commit-push.sh fixes
- Status: Safe to commit
""")

print(f"✅ Created test file: {test_file}")

# Step 2: Check git status
print("\n🔍 Step 2: Check Git Status")
code, out, err = run_cmd("git status --porcelain")
print(f"Dirty files: {len(out.split()) if out else 0}")

# Step 3: Test PR workflow analysis
print("\n📊 Step 3: Test PR Workflow Analysis")
code, out, err = run_cmd("python tools/pr_workflow.py analyze")
if code == 0:
    print("✅ PR workflow analysis successful")
    print(out[:200] + "..." if len(out) > 200 else out)
else:
    print(f"❌ PR workflow failed: {err}")

# Step 4: Test auto-commit (dry run)
print("\n🚀 Step 4: Test Auto-Commit (Dry Run)")
# Modify script temporarily for dry run
script_path = Path("tools/git-auto-commit-push.sh")
content = script_path.read_text()
dry_run_content = content.replace(
    'git add --', 
    'echo "DRY RUN: would add" --'
).replace(
    'git commit -m',
    'echo "DRY RUN: would commit -m"'
)

with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
    f.write(dry_run_content)
    dry_run_script = f.name

import os
os.chmod(dry_run_script, 0o755)

code, out, err = run_cmd(f"bash {dry_run_script}")
print(f"Dry run result: {code}")
print(f"Output: {out[:300]}..." if len(out) > 300 else out)

# Cleanup
os.unlink(dry_run_script)
test_file.unlink()

print("\n🎯 Test complete. Ready for real automation if dry run successful.")
EOF
```

### Phase 5: Execute Final Automation

```bash
# Prompt 5: Execute Real Automation
cd /mnt/c/Projects/ma-saas-platform && python3 - <<'EOF'
import subprocess
import json
from datetime import datetime

def run_cmd(cmd, check=True):
    print(f"🔧 {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ {result.stderr}")
        return False
    print(f"✅ {result.stdout.strip()}")
    return True

print("🚀 BMAD v6 Final Automation Execution")
print("=" * 50)

# Step 1: Final status check
print("\n🔍 Step 1: Pre-execution Status")
status_result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
dirty_count = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0

if dirty_count > 50:
    print(f"⚠️  Warning: {dirty_count} dirty files detected")
    print("Consider running Phase 2 (Clean Recovery) first")
    exit(1)

print(f"✅ Clean state: {dirty_count} files to process")

# Step 2: Run PR workflow analysis
print("\n📊 Step 2: PR Workflow Analysis")
if not run_cmd("python tools/pr_workflow.py analyze"):
    exit(1)

# Step 3: Execute auto-commit-push
print("\n🚀 Step 3: Execute Auto-Commit-Push")
if not run_cmd("bash tools/git-auto-commit-push.sh"):
    print("❌ Auto-commit failed. Check logs above.")
    exit(1)

# Step 4: Verify success
print("\n✅ Step 4: Verify Success")
run_cmd("git log --oneline -3")
run_cmd("git status")

print(f"\n🎉 BMAD v6 Automation Complete at {datetime.now()}")
print("Repository should now be clean and changes pushed to GitHub")
EOF
```

## 🔧 Quick Recovery Commands

### If you need immediate recovery:
```bash
# Restore from latest backup
cd /mnt/c/Projects/ma-saas-platform
git stash pop stash@{0}  # or backup-bmad

# Or hard reset to clean state
git reset --hard origin/master
git clean -fd
```

### If you want to commit the BMAD migration:
```bash
# Accept the migration and commit it
cd /mnt/c/Projects/ma-saas-platform
git add bmad/ src/modules/bmm/
git commit -m "feat: BMAD v6 structural migration - bmad/ → src/modules/bmm/"
git push origin master
```

## 📋 Usage Instructions

1. **Start with Phase 1** to understand the current state
2. **Use Phase 2** if you want to restore to clean state
3. **Apply Phase 3** to fix the automation scripts
4. **Test with Phase 4** before real execution
5. **Execute Phase 5** for final automation

Each prompt is self-contained and provides clear feedback on success/failure.
