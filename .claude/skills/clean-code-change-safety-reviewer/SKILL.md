---
name: clean-code-change-safety-reviewer
description: Kotlin/Gradle（Spring Boot Kotlin含む）のPRで、結合度・影響範囲・マイグレーション戦略を分析し、変更安全性リスクを根拠付きで診断して段階的な低リスク変更を提案する。
---

# Clean Code Change Safety Reviewer

## 目的
- 影響範囲の大きな変更による回帰を防ぐ。
- 変更セットを小さく・段階的に・元に戻せる状態に保つ。

## 対象ルール
- `CC-C001` 影響範囲が1回の変更に対して広すぎる。
- `CC-C002` 隠れた結合により影響が不明確になっている。
- `CC-C003` 振る舞いと構造を同時に変更しており安全網がない。
- `CC-C004` リスクのあるリファクタリングにインクリメンタルなマイグレーションパスがない。

## 手順
1. 影響マップを作成する（モジュール・データパス・副作用）。
2. 変更のホットスポットと発生しやすい連鎖的な破壊を特定する。
3. 段階的な計画を提案する:
   1. 安全継ぎ目（safety seam）の設置
   2. 振る舞いを保持するリファクタリング
   3. 機能の切り替え
   4. クリーンアップ
4. 各段階の検証を添付する。

## 出力形式
- 共有の出力コントラクトを使用すること:
`../clean-code-_shared/references/output_contract.md`
- レビューで特定のファイル・行に起因する finding は `file`（相対パス）と
  `line_range`（例: "42-58" or "42"）を含めること。
- 複数ファイルにまたがる場合は主要ファイルの行範囲を記載すること。
- コード全体への抽象的な指摘など位置特定が不可能な場合は省略可。

## 参照
- `../clean-code-_shared/references/principles_map.md`
- `../clean-code-_shared/references/anti_patterns.md`
