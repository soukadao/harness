# Phase 3: アーキテクチャ設計

## 成果物
- `ARCHITECTURE.md` — 現在の設計状態を常に反映した要約
- `docs/adr/` — ADR（アーキテクチャ決定記録）

## 評価基準
- 仕様書の全コンポーネントが設計に反映されているか
- ADRの記述完全性（決定・理由・代替案・影響）
- レイヤー依存関係の明示
- 非機能要件（性能・セキュリティ・スケーラビリティ）への対応有無

## ブロック条件
- ADRが存在しない（重要な設計決定が未記録）
- 仕様の要件に対応するコンポーネントが設計にない
- 循環依存が設計に含まれる
- `ARCHITECTURE.md` が `status: accepted` のADRと整合していない

## ADR仕様

### frontmatterスキーマ
```yaml
---
id: "000"
title: ""
status: proposed
date: YYYY-MM-DD
supersedes: null
superseded_by: null
---
```

### ステータス定義

| ステータス | 意味 |
|-----------|------|
| `proposed` | 提案中・検討中 |
| `accepted` | 採用・現在有効 |
| `deprecated` | 非推奨（代替なし） |
| `superseded` | 別ADRに置き換え済み |
| `rejected` | 検討したが採用しなかった |

### ルール
- ADRはイミュータブル。変更は新ADRを作成し `supersedes` で参照する
- 旧ADRの `superseded_by` に新ADRのidを追記する
- `ARCHITECTURE.md` は `status: accepted` のADRのみを反映する
- テンプレート: `docs/adr/template.md`
