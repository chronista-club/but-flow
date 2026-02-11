---
description: Bulk staging helper for GitButler. Handles directory-based staging, pattern matching, and interactive filtering for large changesets.
---

Help me stage multiple files to a GitButler branch efficiently.

## Step 1: Parse arguments

If $ARGUMENTS contains:
- Directory path (e.g., `backend/libs`) → stage all files in that directory
- Pattern (e.g., `*.py`, `**/*.go`) → find matching files and stage them
- Nothing → show interactive selection

## Step 2: Gather unassigned changes

Run `but status --json` and extract all `unassignedChanges`.

## Step 3: Filter files

Based on the argument:
- **Directory**: Filter files where `filePath` starts with the directory
- **Pattern**: Use glob matching on `filePath`
- **Interactive**: Show top 20 files and ask for confirmation

## Step 4: Determine target branch

If $ARGUMENTS contains a branch name/ID at the end, use it.
Otherwise, ask which branch to stage to (show active branches).

## Step 5: Bulk staging strategy（ID変動対応版）

`but stage` を実行すると、残りのファイルの cliId が変わる。
毎回 `but status --json` を再取得して最新のIDを使うこと。

### Python方式（推奨: 大量ファイル時）

```bash
python3 -c "
import subprocess, json
TARGET_DIR = 'TARGET_DIR_HERE'
BRANCH = 'BRANCH_NAME_HERE'
files = [f for f in json.loads(subprocess.run(['but','status','--json'], capture_output=True, text=True).stdout).get('unassignedChanges',[]) if f['filePath'].startswith(TARGET_DIR)]
for f in files:
    # 毎回最新のIDを取得（stageするとIDが変わるため）
    status = json.loads(subprocess.run(['but','status','--json'], capture_output=True, text=True).stdout)
    current = next((u for u in status.get('unassignedChanges',[]) if u['filePath'] == f['filePath']), None)
    if current:
        subprocess.run(['but','stage', current['cliId'], BRANCH])
"
```

### シェルループ方式（少量ファイル時）

```bash
# 毎回ステータスを再取得してID変動に対応
for filepath in file1.go file2.go; do
  cli_id=$(but status --json | jq -r --arg p "$filepath" '.unassignedChanges[] | select(.filePath == $p) | .cliId')
  [ -n "$cli_id" ] && but stage "$cli_id" BRANCH_NAME
done
```

### パイプ方式（最もシンプル、ただしID変動リスクあり）

少量ファイルで高速に済ませたい場合のみ。ファイル数が多いとID変動でエラーになる。

```bash
but status --json 2>/dev/null | jq -r '.unassignedChanges[] | select(.filePath | startswith("TARGET_DIR")) | .cliId' | while read cli_id; do
  but stage "$cli_id" BRANCH_NAME 2>&1 | grep -E "(Staged|Failed)" || true
done
```

**Critical**: Always use **branch name**, NOT branch ID. `but stage` requires the full branch name.

## Step 6: Verify and report

After staging:
- Run `but status` to show the result
- Count staged files
- Report any failures

## Examples

```bash
# Stage entire directory
/but-flow:stage-bulk backend/libs feature/my-branch

# Stage by pattern
/but-flow:stage-bulk "**/*.py" feature/python-updates

# Interactive mode
/but-flow:stage-bulk
```

## Error handling

If staging fails:
- Check if branch exists with `but branch list`
- Verify files aren't already staged
- Suggest using full branch name instead of ID
- If IDs are mismatched, re-run `but status --json` to get fresh IDs
