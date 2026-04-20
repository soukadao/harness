# adr-checker

ADRのfrontmatterを抽出・検証・フィルタリングします。

## 使い方

`docs/adr/` があるディレクトリで実行します。

```bash
# 整合性検証
python3 adr-checker.py --validate

# 全ADRを一覧表示
python3 adr-checker.py

# ステータスでフィルタリング
python3 adr-checker.py --status accepted
python3 adr-checker.py --status superseded

# JSON形式で出力
python3 adr-checker.py --status accepted --format json
```

## 引数

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `--dir PATH` | `docs/adr` | ADRディレクトリ |
| `--status STATUS` | なし | フィルタするステータス |
| `--format` | `text` | 出力形式（`text` / `json`） |
| `--validate` | なし | 整合性検証を実行 |

## 出力

| プレフィックス | 意味 |
|--------------|------|
| `[OK]` | 検証通過 |
| `[VIOLATION]` | 整合性エラー（stderr、終了コード1） |
| `[WARN]` | ディレクトリ未存在など |

## 検証内容

| チェック | 説明 |
|---------|------|
| 必須フィールド | `id`, `title`, `status`, `date` の未記入 |
| ステータス値 | 定義外のステータス |
| id重複 | 同一idの重複 |
| 参照整合性 | `supersedes` / `superseded_by` の参照先が存在するか |
| ステータス整合性 | `superseded` なのに `superseded_by` が未設定など |
