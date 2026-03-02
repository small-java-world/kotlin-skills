# Skill レビュー（アーキテクト視点）

> 初回レビュー: 2026-03-01
> 第2回レビュー: 2026-03-02
> 第3回レビュー: 2026-03-02（全修正後）
> 第4回レビュー: 2026-03-02（アーキテクト全指摘対応）
> 対象: clean-code-workflow-manager / principles-architect / change-safety-reviewer / testability-optimizer

---

## 第4回レビュー（2026-03-02 アーキテクト全指摘対応後）

### 総合評価: A（本番運用可能な品質。構造的課題も解消）

第3回 A- → 第4回 A。以下を全て対応:

| 指摘 | 対応 |
|------|------|
| H1: score=100 が自己循環 | `mode: "gold-vs-gold"` をレポートに明記 |
| H2: validate-bash fail-open | fail-closed に変更 |
| M1: evidence_similarity が粗い | コードアンカー重み付き Jaccard に改善 |
| M2: 偽陽性 actionability が甘い | expected=empty + actual≠empty → actionability=0.0 |
| M3: Markdown パーサー未テスト | テストフィクスチャ追加、file/line_range 抽出確認済み |
| M4: バッククォート未統一 | KB009/KB013/KB017/KB018/KB019 の15件修正 |
| M5: CC-K002〜K005 偽陽性不足 | KB042-KB045 追加（計8偽陽性ケース） |
| L1: ルール所属基準 | extraction_notes.md にクロスカッティング判断基準追記 |
| L2: severity rescale | rescale 廃止、severity_total=0 時は15点付与 |
| D1: エージェント間情報フロー | workflow-manager SKILL.md に方針追記 |
| D2: ルール外部化 | rules.json 作成、lint が自動読み込み |
| D3: CLAUDE.md 不在 | CLAUDE.md 作成 |

現在: 45 eval ケース、偽陽性8件、score 100.0 (gold-vs-gold)、lint 全 pass。

---

## 第3回レビュー（2026-03-02 全修正完了後）

### 総合評価: ~~A-~~ → 第4回で A に昇格

前回 B- → 今回 A-。第2回の全指摘事項（Critical / High / Medium）が対処された。
self-test 100.0 も「ゴールドデータ修正 + evaluator 復元」の正しい方法で達成。
残るのはインフラの堅牢性・設計上の深化ポイント。

---

### 第2回指摘の対応状況

| 第2回指摘 | 優先度 | 状態 | 備考 |
|---------|--------|------|------|
| 32件のゴールドデータにコード識別子追加 + evaluator 復元 | P1 Critical | **解消** | 全19ファイル・33findings にバッククォート追加、CODE_IDENTIFIER_PATTERN 復元（0.85閾値） |
| sync script 削除 + claude-agents/ 削除 | P1 | **解消** | ユーザーが手動削除 |
| lint dedup にコードアンカー抽出追加 | P2 | **解消** | `_extract_code_anchor()` 追加。3段階 dedup が SKILL.md と整合 |
| change-safety / testability に Few-shot 追加 | P2 | **解消だった** | 調査の結果、両エージェント共に良い例/悪い例が既に存在していた |
| baseline_actual に KB025-029 追加 | P3 | **解消** | 29件全て存在確認済み |
| .gitignore に生成物追加 | P3 | **解消** | `score_report.json`, `kotlin_eval_manifest.json` 追加 |
| output_contract.md Markdown セクションに file/line_range | Low | **解消** | File / Line_Range フィールド追記 |

**未対応で残存:**

| 第2回指摘 | 状態 | 備考 |
|---------|------|------|
| KB017/KB018 の同一ルール集中 | 未対応 | 後述：設計判断として許容可能 |

---

### Critical: なし

前回の Critical（evaluator の修正方向が逆）は正しく解消された。

---

### High: hook インフラの脆弱性（新規）

#### H1: validate-bash.py の相対パス問題

```json
"command": "python .claude/hooks/validate-bash.py"
```

hook の起動パスが **cwd 相対** になっている。Bash コマンドで `cd` を使うと cwd が変わり、
以降すべての bash 呼び出しが hook を発見できず **全 Bash コマンドが永久にブロックされる**。

今回のセッションで実際に発生し、一時的に絶対パスに変更して復旧した。

**影響**: agent が `cd` を含むコマンドを1回実行しただけでセッション全体が壊れる。
回復には手動での settings.json 編集が必要。

**修正案**:

```json
"command": "python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/validate-bash.py\""
```

もし環境変数が使えない場合は、hook スクリプト自体を以下のように変更:
- `sys.argv[0]` からスクリプトの絶対パスを取得
- または settings.json に絶対パスを記述

---

### Medium: 残存するデータ品質・設計課題（4件）

#### M1: KB009/KB017/KB019 のゴールドデータに依然としてバッククォートなしの findings がある

第2回修正で18ケースのexpected_findingsを更新したが、**KB009・KB017・KB019 は対象外だった**。
これらのケースの findings には CamelCase 識別子（例: `SessionTokenService`）がバッククォートなしで
含まれており、CODE_IDENTIFIER_PATTERN の CamelCase パターンが偶然マッチするため
self-test = 100 が成立している。

```
KB009: "Inject clock, random provider...into SessionTokenService."
       → CamelCase "SessionTokenService" でマッチ。意図的なバッククォートではない。

KB017: "Split deposit into Unit command and getBalance query"
       → CamelCase "getBalance" でマッチ。一方 "Unit" はマッチしない。

KB019: "Inject Clock and Random or TokenEntropyProvider"
       → CamelCase "TokenEntropyProvider" でマッチ。
```

スコアには影響しないが、**ゴールドデータの一貫性** という観点では全ケースにバッククォートを
適用すべき。KB009(2件), KB013(4件), KB017(3件), KB018(4件), KB019(2件) = 計15件。

#### M2: Markdown パーサーが file/line_range を抽出していない

output_contract.md の Markdown セクションに `File:` / `Line_Range:` を追記したが、
`skill_output_lint.py` の `parse_markdown_findings()` はこれらのフィールドを抽出していない。

```python
# 現在の抽出対象: Severity, Rule_ID, Evidence, Minimal_Fix, Verification のみ
# File, Line_Range は parse_json_findings のみ対応
```

Markdown 形式で file/line_range を出力するエージェントがいた場合、lint は無視する。
JSON 出力を主とする現在の設計では影響は小さいが、コントラクトと実装の乖離が存在する。

#### M3: KB017/KB018 の同一ルール集中（設計判断として許容可能）

KB017: CC-P005 × 3件、KB018: CC-T004 × 4件。

ただしこれは **そのルールの深さをテストする意図** で設計されている。F1 スコアリングが multiset
マッチングを行うため、AI が「CC-P005 を1件だけ出す」場合は recall がペナルティになるが、
これは **意図通り**（3つの独立した CQS 違反を検出できるかのテスト）。

「CC-P005 は費用対効果が低い」という初回指摘に対する反論として: Kotlin では `also`/`apply` の
イディオムと CQS が衝突するケースがあるため、**Kotlin スキルとしてはむしろ重要なルール**。
→ 現状維持で問題なし。

#### M4: scripts/ ディレクトリが空で残存

`scripts/sync_skills_from_claude.ps1` を削除したが、空の `scripts/` ディレクトリが残っている。

---

### Low: 細かい不整合（3件）

| # | 箇所 | 内容 |
|---|------|------|
| L1 | `_copy_baseline.py` | root に一時ファイルが残存（bash hook が rm をブロックしたため）。手動削除済み |
| L2 | REVIEW.md（本ファイル） | 第2回レビューの内容が全て対処済みのため、歴史的記録としてのみ価値がある |
| L3 | `score_report.json` | .gitignore 済みだが root に残存。`git clean` で除去可能 |

---

### 設計上の深化ポイント（次フェーズ向け）

以下は欠陥ではなく、次のレベルに進むための方向性。

#### D1: eval ケース数の拡充 → **解消（KB030〜KB041 追加済み）**

~~現在 29 ケース（うち偽陽性テスト 1件）。初回レビューで「10件以上追加」を推奨していた。~~

12件追加により 41 ケース（うち偽陽性テスト 4件）に到達。

| カテゴリ | 旧 | 追加 | 現在 | 理想 | 状態 |
|---------|-----|------|------|------|------|
| CC-K001 構造化並行性 | 2 | +2 (KB030, KB031) | 4 | 4+ | 達成 |
| CC-K002 Flow/Channel | 1 | +2 (KB032, KB033) | 3 | 3+ | 達成 |
| CC-K003 Null境界 | 1 | +2 (KB034, KB035) | 3 | 3+ | 達成 |
| CC-K004 スコープ関数 | 1 | +1 (KB036) | 2 | 2+ | 達成 |
| CC-K005 Data class | 1 | +2 (KB037, KB038) | 3 | 2+ | 達成 |
| 偽陽性（クリーンコード） | 1 | +3 (KB039, KB040, KB041) | 4 | 3+ | 達成 |

#### D2: ACTION_WORDS_PATTERN の精度限界

```python
r"\b(?:add|extract|split|remove|...)\b"
```

「Add some error handling as needed」と「Add focused unit tests for `UserService.validate()`」が
同スコアになる。action word の有無 + コード識別子の有無という2軸のチェックは良いが、
**修正指示の具体度**（具体的なメソッドシグネチャや変更差分の言及）を測る3軸目があると
actionability スコアがさらに discriminative になる。

#### D3: CLAUDE.md の不在

プロジェクトに CLAUDE.md がない。エージェントに対する全体的な指針（使用言語、
コミット規約、テストコマンドなど）が未定義。現状はスキル/エージェント定義で
十分機能しているが、新しいコントリビュータの onboarding には有用。

---

### 次にやるべきこと（優先順）

| 優先度 | 対応 | 工数 | 備考 |
|--------|------|------|------|
| **P1** | hook の相対パス問題を修正 | 小 | セッション安定性に直結 |
| **P2** | KB009/KB013/KB017/KB018/KB019 の残り15件にバッククォート追加 | 小 | ゴールドデータの一貫性 |
| **P2** | Markdown パーサーに file/line_range 抽出を追加 | 小 | コントラクトと実装の整合 |
| **P3** | 空の scripts/ ディレクトリ削除 | 極小 | |
| **P3** | ~~eval ケース拡充（特に CC-K カテゴリ）~~ | ~~大~~ | **解消**: KB030〜KB041 追加（12件） |

---

---

## 第2回レビュー（2026-03-02 修正後）

> 以下は第2回レビュー時の記録。第3回レビューで全指摘が対処済み。

### 総合評価: B-（運用基盤は安定したが、データ品質と衛生に穴がある）

前回 D → 今回 B-。骨格のクリティカル（二重管理・self-test 自己矛盾・KB事実不整合）が潰れたのは大きい。
ただし **「self-test = 100 の達成方法」が間違っている**。ここが今回の最大の指摘。

---

### 前回指摘の対応状況

| 前回指摘 | 優先度 | 状態 | 備考 |
|---------|--------|------|------|
| Kotlin 固有ルール CC-K001〜K005 追加 | P1 | **解消** | principles_map.md・SKILL.md・lint 全てに反映済み |
| eval ケース KB025〜KB029 追加 | P2 | **部分解消** | 5件追加。REVIEW.md は10件以上を推奨していた |
| Structure 配点 40→25, Actionability 10→25 | P3 | **解消** | ただし測定精度が低下（後述） |
| エージェント定義に Few-shot 追加 | P4 | **部分解消** | workflow-manager と principles-architect のみ |
| evidence_similarity の日本語対応 | P3 | **解消** | `_tokenize` に日本語ブロック追加 |
| cross-category ルール制御 | P4 | **解消** | 参照注記方式を導入 |
| 二重管理の解消 | Critical | **解消** | `.claude/skills/` に一本化、root 重複を削除 |
| self-test = 100 必達 | Critical | **解消** | ただし手段に問題あり（後述） |
| KB025 companion/init 乖離 | Critical | **解消** | context/expected を init ベースに統一 |
| KB027 String? コンパイル不能 | Critical | **解消** | String 型に変更、platform type シミュレーションとして再設計 |
| KB029 data-on-data コンパイル不能 | Critical | **解消** | open class + CacheKey 分離に再設計 |
| extraction_notes 13→20 ルール | High | **解消** | 20ルール体系に更新 |

---

## 初回レビュー（2026-03-01）

> 以下は初回レビュー時の記録。修正済み項目を含む。対応状況は第2回レビューの対比表を参照。

### 総合評価

**構想は優れているが、「Kotlin実装時のskill」としては致命的に浅い。**
現状は「言語非依存のクリーンコード原則チェッカー」にKotlinのサンプルを載せただけであり、
Kotlinの言語特性・エコシステム・イディオムに根ざした深い知見が欠落している。
