# dep-outdated-checker

npmパッケージの最新バージョンと比較し、古くなったものを検出します。

## 使い方

`package.json` があるディレクトリで実行します。

```bash
# デフォルト設定（180日以上古い minor 以上のバージョン差を検出）
python3 dep-outdated-checker.py

# major 更新のみ、365日以上、特定パッケージを除外、JSON形式で出力
python3 dep-outdated-checker.py --days 365 --severity major --ignore react lodash --format json
```

## 引数

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `--days N` | `180` | 最新リリースがN日以上前なら古いと判定 |
| `--severity` | `minor` | 検出する最小バージョン差（`patch` / `minor` / `major`） |
| `--ignore PKG...` | なし | スキップするパッケージ名（複数指定可） |
| `--format` | `text` | 出力形式（`text` / `json`） |

## 出力

| プレフィックス | 意味 |
|--------------|------|
| `[OK]` | 最新またはバージョン差が閾値未満 |
| `[STALE]` | 古いパッケージ検出（stderr、終了コード1） |
| `[IGNORE]` | `--ignore` で除外されたパッケージ |
| `[WARN]` | バージョン情報の取得失敗 |
