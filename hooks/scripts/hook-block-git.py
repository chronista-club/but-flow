#!/usr/bin/env python3
"""
GitButler Workflow Hook: git コマンドをブロックし but への誘導を行う
PreToolUse (Bash matcher) 用

stdinからJSON受信 → tool_input.command を検査 → git操作ならブロック
"""
import json
import sys
import re

# ブロック対象: git の書き込み系・状態変更系コマンド（branch は個別判定）
BLOCKED_GIT_COMMANDS = re.compile(
    r'^\s*git\s+'
    r'(checkout|switch|stash|add|commit|push|pull|merge|rebase|reset|cherry-pick|revert|tag|init)'
    r'(\s|$)'
)

# git branch の読み取り専用サブコマンドは許可
BRANCH_READONLY = re.compile(
    r'^\s*git\s+branch\s+'
    r'(--show-current|--list|-l|--contains|--merged|--no-merged|-r|--remotes|-a|--all|-v|--verbose)'
    r'(\s|$)'
)

# git branch（引数なし = 一覧表示）も許可
BRANCH_LIST_ONLY = re.compile(r'^\s*git\s+branch\s*$')

# git branch の書き込み操作はブロック
BRANCH_WRITE = re.compile(
    r'^\s*git\s+branch\s+'
    r'(-[dDmMcC]|--delete|--move|--copy|--force|--set-upstream|--unset-upstream|--edit-description)'
    r'(\s|$)'
)

# 許可: 読み取り専用の git コマンド（log, diff, show, status, blame 等）
# → ブロックしない（but にない機能もあるため）

# 許可: git を内部的に使うツール（gh, git-cz 等）
# → コマンドが 'git' で始まらないので自然に通過

def is_blocked_branch_command(segment):
    """git branch コマンドの読み取り/書き込みを判定する"""
    if not re.match(r'^\s*git\s+branch(\s|$)', segment):
        return False

    # 引数なし（一覧表示）は許可
    if BRANCH_LIST_ONLY.match(segment):
        return False

    # 読み取り専用サブコマンドは許可
    if BRANCH_READONLY.match(segment):
        return False

    # 明示的な書き込み操作はブロック
    if BRANCH_WRITE.match(segment):
        return True

    # それ以外の git branch <args>（新規ブランチ作成等）もブロック
    return True

def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # パース失敗時はブロックしない（安全側に倒す）
        sys.exit(0)

    # tool_input.command を取得
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    # パイプやセミコロンで連結されたコマンドも検査
    # "ls && git commit -m 'test'" のようなケースをキャッチ
    segments = re.split(r'[;&|]+', command)

    for segment in segments:
        segment = segment.strip()

        # git branch は個別判定
        if is_blocked_branch_command(segment):
            msg = (
                f"Blocked: 'git branch' (write operation) — "
                f"This project uses GitButler. Use 'but branch' instead of 'git branch'.\n"
                f"Read-only commands (--show-current, --list, -v, etc.) are allowed.\n"
                f"Details: .claude/skills/gitbutler-workflow/SKILL.md"
            )
            print(msg, file=sys.stderr)
            sys.exit(2)

        # その他のブロック対象コマンド
        if BLOCKED_GIT_COMMANDS.match(segment):
            msg = (
                f"Blocked: '{segment.split()[0]} {segment.split()[1]}' — "
                f"This project uses GitButler. Use 'but' instead of 'git'.\n"
                f"Run: but {segment.split()[1]} ...\n"
                f"Details: .claude/skills/gitbutler-workflow/SKILL.md"
            )
            print(msg, file=sys.stderr)
            sys.exit(2)

    # 許可
    sys.exit(0)

if __name__ == "__main__":
    main()
