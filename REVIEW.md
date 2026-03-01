# Skill レビュー（アーキテクト視点）

> 作成日: 2026-03-01
> 対象: clean-code-workflow-manager / principles-architect / change-safety-reviewer / testability-optimizer

---

## 総合評価

**構想は優れているが、「Kotlin実装時のskill」としては致命的に浅い。**
現状は「言語非依存のクリーンコード原則チェッカー」にKotlinのサンプルを載せただけであり、
Kotlinの言語特性・エコシステム・イディオムに根ざした深い知見が欠落している。

---

## 1. 致命的問題: Kotlin固有の深みが決定的に不足

### 現状の15ルールは言語非依存

CC-P001〜CC-P006、CC-C001〜CC-C004、CC-T001〜CC-T005 のどれも、
Java・TypeScript・Go等に一字一句そのまま適用できる。Kotlin固有のルールが **ゼロ**。

### 欠落しているKotlin固有のルール候補

| カテゴリ | 欠落パターン | なぜ重要か |
|---|---|---|
| **Coroutines** | `GlobalScope` 使用、構造化並行性違反、`launch` の例外伝搬漏れ | Kotlin最大の差別化機能。誤用による本番障害が最も多い |
| **Coroutines** | `Flow` の cold/hot 混同、`SharedFlow` の replay 誤設定 | 状態管理バグの温床 |
| **Coroutines** | `withContext` vs `async` の選択ミス | 不要な並行性の導入 |
| **Null Safety** | Platform type (`!` 型) の境界での未処理、`lateinit` 濫用 | `!!` 以外のnull安全性の穴 |
| **Scope Functions** | `let/run/apply/also/with` の過剰チェーン | 可読性を著しく損なうKotlin固有のアンチパターン |
| **Data Class** | `data class` にミュータブルプロパティ(`var`)、継承との組み合わせ | `copy()` と `equals()` の予期しない振る舞い |
| **Sealed Class** | `when` の非網羅的パターンマッチ、`else` による将来の安全網破壊 | コンパイラ保証を台無しにする |
| **DSL** | Kotlin DSL の過剰設計・可読性無視 | KISS違反のKotlin固有形態 |
| **Extension Functions** | 既存型への責務の密輸入、名前空間汚染 | SRPのKotlin固有の崩壊パターン |
| **Delegation** | `by lazy` の thread safety モード選択ミス、`by map` 濫用 | 隠れた副作用の温床 |
| **Spring Boot Kotlin** | `@Transactional` + coroutine の非互換性 | Spring + Kotlin固有の地雷 |

### evalケースも言語的に浅い

KB001〜KB024の入力コードのほとんどは **Javaからの機械的な書き換え** で、
Kotlinらしいコードが少ない。例えば：

- `KB001`: `Map<String, Any>` を返すController → Javaでも全く同じコード
- `KB013`: 同上。sealed classも Result型もKotlinイディオムが活用されていない
- `KB019`: `Instant.now()` + `Random.nextInt()` → Javaそのまま
- `KB024`: `runBlocking` を使っているが、これだけがKotlin固有

**意見**: Kotlin実装スキルを名乗るなら、入力コードが「Kotlinでしか書けないコード」の
ケースが必要。coroutine の `supervisorScope` 漏れ、`Flow.collect` 中のミュータブル状態変更、
`inline fun` + reified の誤用など。

---

## 2. アーキテクチャ設計: 良い点と問題点

### 良い点

- **3専門家 + 1オーケストレータ** の分業は、スキル自身が説くSRP原則に整合している
- **Output Contract** が JSON/Markdown 両対応で、lint・scoring パイプラインと一貫している
- **KB015（偽陽性耐性テスト）** の存在は優秀。多くのレビューツールが見落とす
- **F1ベースのスコアリング** はPrecision/Recall両方を見ており、「大量に指摘して当たりを増やす」戦略を正しくペナルティ化

### 問題点

#### a) ワークフローの重複排除アルゴリズムが脆弱

```
evidence の 80% token overlap で merge
```

これは実際には機能しない。同じSRP違反を「P004: SRPに違反している」と
「C001: 影響範囲が広い」で報告した場合、evidenceは全く異なる文面になるので
重複検出されない。一方で、同じクラスの異なるメソッドの独立した問題が、
クラス名を共有するだけで誤マージされる可能性がある。

**改善案**: evidence の token overlap ではなく、
**対象コード位置（ファイル + 行範囲）** をアンカーにして重複判定すべき。

#### b) サブスキルの独立性宣言と cross-category ルールの矛盾

「サブスキルは独立に実行可能」と言いつつ「cross-category の finding を条件付きで許可」
という設計は曖昧。「自分のprefix のfindingがゼロの場合は cross-category 禁止」という
ルールはあるが、これは **消極的なガード** であって **積極的なガイダンス** ではない。

**改善案**: cross-category は「参照（reference）」として記載できるが、
正式な finding としてはカウントしない、という明確な分離を入れる。

#### c) Scope Lock の実効性が不明

Step 1 の Scope Lock は概念として正しいが、**具体的にどうやってスコープを定義し、
サブスキルに渡すのか** が不明。ファイルパスのリスト？モジュール名？自然言語の説明？
これが曖昧だと、サブスキルがスコープ外の指摘を出すのを防げない。

---

## 3. ルール設計の精度

### CC-P005 (CQS) の費用対効果が低い

CQS違反は実務でほとんど主要な問題にならない。特にKotlinでは、`also` や `apply` で
副作用とチェーンを意図的に組み合わせるイディオムがあり、CQSの厳格な適用はKotlinの
慣習と衝突する。**15ルール中の1枠をCQSに使うのは贅沢**。

### CC-C002 の結合度6レベルは理論的すぎる

内容結合・共通結合・外部結合・制御結合・スタンプ結合・データ結合の分類は
教科書的には正しいが、LLMがこの粒度で正確に分類できるかは疑問。
**結合度レベルの正確な分類よりも、「この変更が壊すかもしれない箇所のリスト」
という実用的な出力の方が価値が高い**。

### principles_map.md の CC-P001 拡張は良い

プリミティブ型濫用と不要なミュータブル状態をKISS配下に入れたのは実用的。
ただし「value class / inline class の導入」は **Kotlin固有** のアドバイスであり、
これこそKotlin固有ルールとして独立させるべき深みがある。

---

## 4. スコアリングシステムの設計

### 重み配分 40/35/15/10 の根拠が不明

| 軸 | 配点 | 疑問 |
|---|---|---|
| Structure (lint通過) | 40 | **高すぎる**。JSONフォーマットが正しいだけで40%は甘い |
| Rule F1 | 35 | 妥当 |
| Severity Match | 15 | 妥当だがグリーディマッチングの精度が心配 |
| Actionability | 10 | **低すぎる**。実務では「何をすればいいか」が最も重要 |

### evidence_similarity の Jaccard 係数は粗い

```python
re.findall(r"[a-z0-9_]+")
```

英語と日本語が混在する場合、このパターンは日本語トークンを完全に無視する。
日本語で書かれた evidence は常に similarity = 0 になる。

### ACTION_WORDS_PATTERN が表層的

```python
r"\b(?:add|extract|split|remove|...)\b"
```

「Add some error handling as needed」でも「Add focused unit tests for boundary validation」
でも同じスコアになる。action word の有無だけでなく、**具体性のレベル** を測る必要がある。

---

## 5. anti_patterns.md の品質

### 良い点

- 「モックの過剰使用」「動的な期待値」「AAAの複数サイクル」は実務で頻出する的確な指摘
- 「レビュー品質」セクションでメタレベルの品質基準を定義しているのは自己参照的で良い

### 問題点

Kotlin固有のアンチパターンが皆無。以下が欠落：

- スコープ関数の連鎖地獄（`x.let { it.also { ... }.run { ... } }` 等）
- `companion object` の責務肥大化
- `object` シングルトンのテスト困難性
- `init` ブロックでの副作用

---

## 6. 運用面の課題

### エージェント定義が薄すぎる

```markdown
あなたは **Clean Code Principles Architect** です。
`.claude/skills/clean-code-principles-architect/SKILL.md` の手順に従って動作してください。
```

これだけでは出力品質は SKILL.md の解釈に完全に依存する。
**Few-shot example** をエージェント定義内に含めるか、
「良い出力の特徴」と「悪い出力の特徴」を明示すべき。

### ツール制約が厳しすぎる

サブエージェントに `Read, Grep, Glob` しか許可していない。
実際のPRレビューでは **ビルドの実行** や **テストの実行** ができないと
「verification が実行可能か」を検証できない。Bash ツールの制限付き許可が必要。

---

## 7. 改善提案（優先度順）

### P1（必須）: Kotlin固有ルールの追加

最低限以下を追加：

| ルールID | 内容 |
|---|---|
| `CC-K001` | 構造化並行性違反（GlobalScope、例外伝搬漏れ） |
| `CC-K002` | Flow/Channel の誤用（cold/hot混同、collect中の副作用） |
| `CC-K003` | Null安全性の境界漏れ（Platform type、lateinit） |
| `CC-K004` | スコープ関数の過剰チェーン |
| `CC-K005` | Data class の契約違反（var、継承） |

### P2（必須）: evalケースのKotlin深度向上

coroutine、Flow、sealed class、extension function を中心としたケースを10件以上追加。
「Javaでも書ける」コードだけのケースは全体の30%以下に抑える。

### P3（推奨）: スコアリングの改善

- Structure の配点を 40→25 に下げ、Actionability を 10→25 に上げる
- evidence_similarity に日本語トークン対応を追加
- Actionability に具体性スコア（固有名詞・コード参照の有無）を導入

### P4（推奨）: エージェント定義の強化

- Few-shot example を各エージェント定義に1〜2件追加
- 「良い finding」と「悪い finding」の対比を明示
- サブエージェントへの Bash ツールの制限付き許可

---

## 一言でまとめると

**「Clean Codeの一般原則をKotlinに適用するスキル」ではなく
「Kotlinの言語特性を活かしたClean Codeスキル」になるべき。**
現状は書籍でいえば「Chapter 1: 汎用原則」だけ書いて
「Chapter 2〜10: Kotlin実践編」が白紙の状態。
骨格は良いので、Kotlin固有の深みを入れれば本物になる。
