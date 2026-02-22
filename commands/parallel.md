---
description: tmuxを使って複数ワーカーでClaude Codeセッションを並列起動。ccwire自動登録付き。
---

# CW Parallel — 並列セッション起動

## 手順

1. 起動対象の決定:
   - 引数でワーカー名が指定された場合 → それらを使用
   - 指定がない場合 → `cw ls` で一覧を表示し、起動するワーカーを選択

2. tmuxセッションの構成を決定:
   - 2ワーカー: 左右2ペイン
   - 3ワーカー: 左 + 右上下
   - 4ワーカー: 2x2グリッド

3. tmuxセッション `cw-parallel` を作成（既存なら確認の上で再作成）:

   **重要**: 各ペインで claude を起動する際、ccwire 自動登録用の環境変数を設定する。

   ```bash
   # 例: 2ワーカーの場合
   tmux new-session -d -s cw-parallel -c "$(cw path issue-42)"
   tmux split-window -h -t cw-parallel -c "$(cw path issue-43)"

   # 各ペインでClaude Codeを起動（ccwire自動登録 + tmuxターゲット付き）
   tmux send-keys -t cw-parallel:0.0 'CCWIRE_SESSION_NAME=worker-issue-42 CCWIRE_TMUX_TARGET=cw-parallel:0.0 claude' Enter
   tmux send-keys -t cw-parallel:0.1 'CCWIRE_SESSION_NAME=worker-issue-43 CCWIRE_TMUX_TARGET=cw-parallel:0.1 claude' Enter
   ```

4. セッションにアタッチ:
   ```bash
   tmux attach -t cw-parallel
   ```

5. 起動完了メッセージ:
   ```
   並列セッションを起動しました:
     Pane 0: issue-42 (feature/issue-42) — ccwire: worker-issue-42
     Pane 1: issue-43 (feature/issue-43) — ccwire: worker-issue-43

   tmux attach -t cw-parallel でアクセスできます。
   各ワーカーは ccwire に自動登録されます（wire_sessions で確認可能）。
   ```

## 環境変数

各ワーカーに渡す環境変数:

| 変数 | 値 | 用途 |
|------|-----|------|
| `CCWIRE_SESSION_NAME` | `worker-{name}` | ccwire 自動セッション登録 |
| `CCWIRE_TMUX_TARGET` | `cw-parallel:{window}.{pane}` | tmux 通知先 |

## 引数

- `<worker-names...>`: 起動するワーカー名（スペース区切り、省略時は対話選択）

## ワーカー間通信

各ワーカーは ccwire に自動登録されるため、以下の通信が可能:

```
# ワーカー間メッセージ
wire_send(to: "worker-issue-43", content: "認証モジュールの変更完了。依存OK")

# ステータス更新
wire_status(status: "busy")

# リーダーへの質問（AskUserQuestion は使わない）
wire_send(to: "lead", content: "質問: DB スキーマの方針を確認したい", type: "task_request")
```

## 注意

- tmuxがインストールされていない場合はエラー
- 各ペインは独立したClaude Codeセッション（互いに干渉しない）
- ワーカーは AskUserQuestion を使わず、質問は ccwire でリーダーに送信すること
