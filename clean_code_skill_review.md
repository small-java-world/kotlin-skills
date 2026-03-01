# Clean Code Skill Review

## Findings (severity順)

1. **High**: 「クリーンコードなら指摘ゼロ」を仕様化しているのに、lintがゼロ件をエラー扱いしており評価軸が矛盾。
   - 根拠: `C:\Users\kawan\.codex\skills\clean-code-_shared\scripts\skill_output_lint.py:181`, `:182`, `C:\Users\kawan\.codex\skills\clean-code-_shared\tests\kotlin_eval\cases\KB015\expected_findings.json:2`
   - 影響: False-positive耐性ケースが正解でも `lint_code=2` になり、評価が歪む（self-test 95.33）。
   - 最小修正案: `--allow-empty-findings` をlintに追加し、manifest側でケース単位許可フラグを持たせる。

2. **High**: 採点が未提出ケースを十分に罰しないため、難ケース未提出でも高得点を維持可能。
   - 根拠: `C:\Users\kawan\.codex\skills\clean-code-_shared\scripts\score_kotlin_eval.py:139`, `:195`, `:197`, `:210`
   - 影響: ベンチマーク信頼性低下（提出戦略でスコア操作できる）。
   - 最小修正案: missing case を全軸0点扱い、または未提出1件でもfail。

3. **Medium**: 出力契約と実装の整合不足（`summary` の扱い）。
   - 根拠: `C:\Users\kawan\.codex\skills\clean-code-_shared\references\output_contract.md:7`, `C:\Users\kawan\.codex\skills\clean-code-_shared\scripts\skill_output_lint.py:62`, `C:\Users\kawan\.codex\skills\clean-code-_shared\tests\kotlin_eval\cases\KB013\expected_findings.json:1`
   - 影響: フォーマット揺れで後段連携が壊れやすい。
   - 最小修正案: `summary` を必須化するか、契約を任意に明記してlint/scoreを同期。

4. **Medium**: `rule_id` バリデーションが13ルール外を許容。
   - 根拠: `C:\Users\kawan\.codex\skills\clean-code-_shared\scripts\skill_output_lint.py:32`
   - 影響: 未定義ルール（例 `CC-Z999`）が通過し、ルール体系が崩れる。
   - 最小修正案: 許可リスト固定（P001-005, C001-004, T001-004）で厳密検証。

5. **Medium**: `.claude` 側 workflow 指示に内部矛盾（prefix固定期待とクロスカテゴリ許可）。
   - 根拠: `G:\GrudgeOfTheTranslucentBones_comp\.claude\skills\clean-code-workflow-manager\SKILL.md:40`, `:46`, `:54`, `:82`
   - 影響: 出力安定性が落ちる。
   - 最小修正案: 優先順位を明記（prefix優先、クロスカテゴリは条件付き許可）。

6. **Medium**: advancedケース expected の一部がコード実体より履歴依存/仮定依存。
   - 根拠: `C:\Users\kawan\.codex\skills\clean-code-_shared\tests\kotlin_eval\cases\KB013\expected_findings.json:13`, `KB013\input_bad.kt:25`, `KB014\expected_findings.json:6`, `KB014\input_bad.kt:29`
   - 影響: コード根拠よりコメント叙述を優先する学習バイアスが入る。
   - 最小修正案: expected evidence をコード上の観測事実中心に修正。

7. **Low**: ルール出現分布が偏り（`CC-T001` 多、`CC-P003/CC-P005/CC-T004` 少）。
   - 根拠: 15ケース集計（`CC-T001=9`, `CC-P003=1`, `CC-P005=1`, `CC-T004=1`）。
   - 影響: テスト欠落指摘が過剰になり、原則系識別が弱くなる。
   - 最小修正案: 追加ケースで P003/P005/T004 を増やして分布調整。

## 観点別短評

1. 13ルール設計: 体系は妥当。実装側の厳密性（許可ルール固定）を追加すべき。  
2. `principles_map.md`: 凝集/結合の語彙は実用的で整合性は高い。  
3. `anti_patterns.md`: 分類は良好。ただし評価コーパス反映バランスに偏りあり。  
4. `output_contract.md`: 明快だがlint/scoreとの契約同期が必要。  
5. `SKILL.md`: 指示は概ね十分。`.claude` 側の矛盾解消が必要。  
6. `extraction_notes.md`: スコープ外判断は妥当。  
7. Kotlinケース: 難易度配分は妥当。評価器側のゼロ件仕様と未提出罰則を修正すると精度向上。  

## 追加メモ

- manifest再生成により現在の `case_count` は 15。  
  参照: `C:\Users\kawan\.codex\skills\clean-code-_shared\tests\kotlin_eval\kotlin_eval_manifest.json:4`

