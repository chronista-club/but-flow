---
description: 並列開発の状態をVantage Pointダッシュボードに表示。agent一覧、タスクボード、メッセージログの3ペイン。
---

# CW Dashboard — 並列開発ダッシュボード

Vantage Point に並列開発の全体像を表示する。

## 手順

1. Vantage Point のキャンバスを開く（未開の場合）:
   ```
   mcp__vantage-point__open_canvas()
   ```

2. 左右ペインを有効化:
   ```
   mcp__vantage-point__toggle_pane(pane_id: "left", visible: true)
   mcp__vantage-point__toggle_pane(pane_id: "right", visible: true)
   ```

3. **左ペイン: Agent 一覧 + ステータス**

   `wire_sessions` と `wire_status` でデータを取得し、以下の形式で表示:

   ```
   mcp__vantage-point__show(
     pane_id: "left",
     content_type: "html",
     title: "Agents",
     content: <下記HTML>
   )
   ```

   HTML テンプレート:
   ```html
   <style>
     body { font-family: -apple-system, sans-serif; padding: 12px; background: #1a1a2e; color: #e0e0e0; }
     .agent { padding: 8px 12px; margin: 4px 0; border-radius: 6px; background: #16213e; }
     .agent .name { font-weight: 600; font-size: 14px; }
     .agent .meta { font-size: 12px; color: #888; margin-top: 2px; }
     .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
     .idle { background: #2d3436; color: #b2bec3; }
     .busy { background: #0984e3; color: white; }
     .done { background: #00b894; color: white; }
     h3 { color: #74b9ff; margin: 0 0 8px; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
   </style>
   <h3>Agents</h3>
   <!-- 各 agent を .agent ブロックで表示 -->
   <div class="agent">
     <div class="name">worker-issue-42 <span class="badge busy">busy</span></div>
     <div class="meta">tmux: cw-parallel:0.0 | last: 10:05</div>
   </div>
   ```

4. **メインペイン: タスクボード**

   TaskList がある場合はそのタスクを、なければ `cw ls` + `cw status` の情報を表示:

   ```
   mcp__vantage-point__show(
     pane_id: "main",
     content_type: "html",
     title: "Tasks",
     content: <下記HTML>
   )
   ```

   HTML テンプレート:
   ```html
   <style>
     body { font-family: -apple-system, sans-serif; padding: 12px; background: #1a1a2e; color: #e0e0e0; }
     .board { display: flex; gap: 12px; }
     .column { flex: 1; background: #16213e; border-radius: 8px; padding: 10px; }
     .column h4 { margin: 0 0 8px; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
     .pending h4 { color: #fdcb6e; }
     .progress h4 { color: #74b9ff; }
     .completed h4 { color: #55efc4; }
     .task { background: #0d1b2a; padding: 8px; margin: 4px 0; border-radius: 4px; font-size: 13px; }
     .task .owner { font-size: 11px; color: #888; }
   </style>
   <div class="board">
     <div class="column pending">
       <h4>Pending</h4>
       <!-- TaskList の pending タスク -->
     </div>
     <div class="column progress">
       <h4>In Progress</h4>
       <!-- TaskList の in_progress タスク -->
     </div>
     <div class="column completed">
       <h4>Completed</h4>
       <!-- TaskList の completed タスク -->
     </div>
   </div>
   ```

5. **右ペイン: メッセージログ**

   `wire_receive` で最新メッセージを取得し、ログ形式で表示:

   ```
   mcp__vantage-point__show(
     pane_id: "right",
     content_type: "html",
     title: "Messages",
     content: <下記HTML>
   )
   ```

   HTML テンプレート:
   ```html
   <style>
     body { font-family: -apple-system, sans-serif; padding: 12px; background: #1a1a2e; color: #e0e0e0; }
     .msg { padding: 6px 10px; margin: 3px 0; border-radius: 4px; font-size: 12px; border-left: 3px solid #0984e3; background: #16213e; }
     .msg .from { font-weight: 600; color: #74b9ff; }
     .msg .time { color: #636e72; font-size: 11px; }
     .msg .content { margin-top: 2px; }
     h3 { color: #74b9ff; margin: 0 0 8px; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
   </style>
   <h3>Messages</h3>
   <!-- 最新メッセージを時系列で表示 -->
   <div class="msg">
     <span class="from">worker-issue-42</span> <span class="time">10:05</span>
     <div class="content">認証モジュールの実装完了。PR #123 を作成しました。</div>
   </div>
   ```

## 更新タイミング

- 初回表示: コマンド実行時
- 以降: lead agent が適宜 `wire_status` → `show` で更新
- 推奨: タスク完了報告を受けるたびに更新

## 引数

なし（現在のチームの状態を自動取得）
