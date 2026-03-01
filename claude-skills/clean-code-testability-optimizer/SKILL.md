# Clean Code Testability Optimizer

## 目的
- 最小限の十分な自動テストを追加してコード変更を安全にする。
- 明確な意図を持つ、決定論的で読みやすいテストを優先する。

## 対象ルール
- `CC-T001` 変更した振る舞いに対して回帰テストがない。
- `CC-T002` テストが過度に広い・不安定・または遅い。
- `CC-T003` テストしにくい密結合によりロジックのテストが困難。
- `CC-T004` テスト名/アサーションが振る舞いを表現していない。

## 手順
1. 変更された振る舞いとリスク境界を特定する。
2. 最小限のテストセットを提案する:
   1. ローカルロジックに対する単体テスト
   2. 連携境界に対する結合テスト
   3. 重要なユーザーフローにのみ E2E テスト
3. コードがテストしにくい場合は継ぎ目の抽出を推奨する。
4. 合否を判断するアサーションと実行時間の予算を定義する。

## 出力形式
`G:\GrudgeOfTheTranslucentBones_comp\.claude\skills\clean-code-_shared\references\output_contract.md` の形式に従うこと。

## 参照（必ず読むこと）
- `G:\GrudgeOfTheTranslucentBones_comp\.claude\skills\clean-code-_shared\references\principles_map.md`
- `G:\GrudgeOfTheTranslucentBones_comp\.claude\skills\clean-code-_shared\references\anti_patterns.md`
