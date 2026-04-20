# otel-dev

ローカル開発環境用の観測可能性スタックを管理します。

Vector + VictoriaMetrics/Logs/Traces を Docker で起動し、任意の言語・フレームワークからテレメトリを収集できます。

## アーキテクチャ

```
アプリ（任意の言語）
  ↓ OTLP  localhost:4317（gRPC）/ localhost:4318（HTTP）
Vector
  ├─→ Victoria Metrics  localhost:8428  (PromQL)
  ├─→ Victoria Logs     localhost:9428  (LogQL)
  └─→ Victoria Traces   localhost:9999  (TraceQL)
```

## 使い方

`docker` が使えるディレクトリで実行します。

```bash
# スタック起動
python3 otel-dev.py start

# 状態確認・エンドポイント表示
python3 otel-dev.py status

# 停止
python3 otel-dev.py stop

# データをすべてリセット（ボリューム削除）
python3 otel-dev.py reset
```

## エンドポイント

| サービス | URL | クエリ言語 |
|---------|-----|-----------|
| Victoria Metrics | http://localhost:8428/vmui | PromQL |
| Victoria Logs | http://localhost:9428/select/vmui | LogQL |
| Victoria Traces | http://localhost:9999/vmui | TraceQL |

## アプリ側の設定

OTLP エクスポーターのエンドポイントを以下に向けるだけで収集が始まります。

### Node.js

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 node app.js
```

### Python

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 opentelemetry-instrument python app.py
```

### Go / その他

```
OTLP gRPC: localhost:4317
OTLP HTTP: localhost:4318
```

## ポートのカスタマイズ

環境変数で変更できます。

```bash
OTLP_GRPC_PORT=14317 OTLP_HTTP_PORT=14318 python3 otel-dev.py start
```

| 環境変数 | デフォルト | 用途 |
|---------|-----------|------|
| `OTLP_GRPC_PORT` | `4317` | OTLP gRPC 受信ポート |
| `OTLP_HTTP_PORT` | `4318` | OTLP HTTP 受信ポート |
| `VM_PORT` | `8428` | Victoria Metrics |
| `VL_PORT` | `9428` | Victoria Logs |
| `VT_PORT` | `9999` | Victoria Traces |
