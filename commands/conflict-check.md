---
description: 並列ワーカーの変更を比較し、シンボルレベルでマージコンフリクトの可能性を早期検知する。
---

# CC Nav Conflict Check — コンフリクト早期検知

## 手順

### ccwatch が利用可能な場合（推奨）

ccwatch はシンボルレベル（関数・メソッド単位）の衝突を検知できる。

1. `ccwatch check --repo .` を実行
2. ccwatch が自動的に ccws ワーカーを検出し、変更シンボルの重複を解析
3. 衝突があれば exit code 1 で報告される

```bash
ccwatch check --repo .
# 出力例:
# 検出した worktree: 3
#   - issue-42 (feature/issue-42)
#   - issue-43 (feature/issue-43)
#
# ⚠ 1 件のシンボル衝突を検出:
#   src/auth/middleware.ts function `validateToken` (L10-L25)
#     変更者: issue-42, issue-43
```

### ccwatch が未インストールの場合（フォールバック）

ファイルレベルの簡易チェックを行う。

1. `ccws ls` でアクティブなワーカー一覧を取得

2. 各ワーカーの変更ファイル一覧を収集:
   ```bash
   cd $(ccws path <name>)
   git diff --name-only main...HEAD
   ```

3. 変更ファイルの重複を検出:
   - 2つ以上のワーカーが同じファイルを変更している場合 → 警告

4. 結果を表示:
   ```
   ## コンフリクト検知結果

   issue-42 x issue-43: 重複なし
   issue-42 x issue-44: 2ファイルが重複
     - src/auth/middleware.ts
     - src/auth/types.ts

   推奨: issue-44 のマージは issue-42 のマージ後に行ってください。
   ```

## ccwire 連携

ccwire 登録済みなら、コンフリクトがある場合に該当ワーカーへ wire_send で警告を送信する。

## 引数

なし（全ワーカーを自動チェック）

## 推奨利用タイミング

- Wave 切り替え前
- PR 作成前
- リーダーが `/ccnav:dashboard` を更新する際

## ccwatch インストール

```bash
cargo install --git https://github.com/chronista-club/ccwatch
```
