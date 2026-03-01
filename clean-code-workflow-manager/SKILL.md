---
name: clean-code-workflow-manager
description: Kotlin/Gradle（Spring Boot Kotlin・coroutines含む）のコードレビューを、原則・変更安全性・テスタビリティの3専門エージェントに振り分け、根拠付き findings と最小修正・検証手順を統合出力するワークフローマネージャー。
---

# Clean Code Workflow Manager

## Purpose
- Convert "write cleaner code" requests into reproducible, reviewable outputs.
- Route work across three subskills in this order:
  1. `clean-code-principles-architect`
  2. `clean-code-change-safety-reviewer`
  3. `clean-code-testability-optimizer`

## Inputs
- Target code, PR diff, or design memo
- Runtime/context constraints (language, framework, deadlines, compatibility)
- Optional: team conventions

## Output Contract (mandatory)
- Return findings as either:
  1. JSON (`findings[]`)
  2. Markdown findings list
- Each finding must include:
  1. `severity` (`critical|high|medium|low`)
  2. `rule_id`
  3. `evidence`
  4. `minimal_fix`
  5. `verification`

See:
- `../clean-code-_shared/references/output_contract.md`
- `../clean-code-_shared/references/extraction_notes.md`

## Workflow

### Step 1: Scope Lock (親が実施)
- **実施主体: workflow-manager（親）**
- Before invoking any subskill, define:
  - **In-scope**: files, modules, or change sets explicitly under review.
  - **Out-of-scope**: unrelated files, future requirements, style-only fixes not requested.
- Pass the scope definition to all three subskills as context.
- Subskills must not generate findings outside the declared scope.

### Step 2: Principles Pass
- Invoke `clean-code-principles-architect` with the scoped input.
- Rules: CC-P001 (KISS), CC-P002 (YAGNI), CC-P003 (DRY), CC-P004 (SRP), CC-P005 (CQS), CC-P006 (Naming).

### Step 3: Change-Safety Pass
- Invoke `clean-code-change-safety-reviewer` with the scoped input.
- Rules: CC-C001–CC-C004.
- **Note**: Runs independently from Step 2; does not require Step 2 output as input.
  If a prior finding from Step 2 is useful context (e.g., SRP violation also implies blast-radius risk),
  you may reference it, but subskill outputs are not mandatory inputs to each other.

### Step 4: Testability Pass
- Invoke `clean-code-testability-optimizer` with the scoped input.
- Rules: CC-T001–CC-T005.
- Same independence rule as Step 3 applies.

### Step 5: Synthesis (親が実施)
- **実施主体: workflow-manager（親）**
- Merge all findings from Steps 2–4.
- **Deduplication algorithm**:
  1. Group findings by `rule_id`.
  2. Within a group, if two findings share ≥80% token overlap in `evidence`, merge them:
     - Keep the entry with the **higher severity**.
     - Concatenate `minimal_fix` if complementary; otherwise keep the more specific one.
  3. If two findings have different `rule_id` but identical `evidence`, keep both
     (cross-rule overlap is intentional and adds value).
- Emit the merged, deduplicated list sorted by severity (critical → high → medium → low).

### Output Quality Check (親が実施)
- After synthesis, run the lint tool on the output before returning to the user:
```powershell
python ../clean-code-_shared/scripts/skill_output_lint.py `
  --input <output-file> `
  --profile clean-code
```
- Fix any `ERROR` before returning. `WARN` items should be reviewed and addressed if feasible.

## Subskill Execution Notes

- **Subskills run independently** (Steps 2–4 can execute in parallel when no sequential dependency exists).
- **Rule output priority**:
  1. **Primary duty**: Each subskill must prioritise findings under its own prefix (P/C/T).
  2. **Cross-category (conditionally allowed)**: A subskill may emit a rule_id from another prefix only when the evidence clearly crosses category boundaries (e.g., SRP (CC-P004) violation also implies blast-radius risk (CC-C001)).
  3. **Prohibited**: A subskill must never emit only cross-category findings while having zero findings under its own prefix (primary duty abandonment).

## Validation
- Lint generated output:
```powershell
python ../clean-code-_shared/scripts/skill_output_lint.py `
  --input <output-file> `
  --profile clean-code
```

Exit codes:
- `0`: pass
- `1`: warnings only
- `2`: fail

## Kotlin evaluation corpus
- Build manifest:
```powershell
python ../clean-code-_shared/scripts/build_kotlin_eval_manifest.py
```
- Run corpus self-test:
```powershell
python ../clean-code-_shared/scripts/run_kotlin_eval_tests.py --self-test
```
- Score real outputs:
```powershell
python ../clean-code-_shared/scripts/score_kotlin_eval.py `
  --manifest ../clean-code-_shared/tests/kotlin_eval/kotlin_eval_manifest.json `
  --actual-dir <dir-containing-KBxxx-json-or-md> `
  --out ../clean-code-_shared/tests/kotlin_eval/score_report.json
```

## Related subskills
- `../clean-code-principles-architect/SKILL.md`
- `../clean-code-change-safety-reviewer/SKILL.md`
- `../clean-code-testability-optimizer/SKILL.md`
