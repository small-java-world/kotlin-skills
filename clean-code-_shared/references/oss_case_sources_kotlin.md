# Kotlin OSS ケースソース

Kotlin 評価コーパスの設計インスピレーションとして参照した OSS を記録するドキュメント。
`tests/kotlin_eval/cases` 以下の評価コードはすべて新規作成であり、コピーではない。

## ソースレジストリ

1. **Ktor**
- リポジトリ: https://github.com/ktorio/ktor
- ライセンス: Apache-2.0
- 参照目的:
  1. ルーティング/サービス境界のアイデア
  2. リクエスト処理と依存関係の境界パターン

2. **Spring Petclinic Kotlin**
- リポジトリ: https://github.com/spring-petclinic/spring-petclinic-kotlin
- ライセンス: Apache-2.0
- 参照目的:
  1. サービス/リポジトリのレイヤリングのインスピレーション
  2. トランザクションワークフロー分解のアイデア

3. **OkHttp**
- リポジトリ: https://github.com/square/okhttp
- ライセンス: Apache-2.0
- 参照目的:
  1. イミュータブル設定とビルダー規律のインスピレーション
  2. 副作用の境界と API 可読性のヒント

4. **Kotlin Coding Conventions**
- ドキュメント: https://kotlinlang.org/docs/coding-conventions.html
- 参照目的:
  1. 命名/構造のスタイル一貫性
  2. 慣用的な Kotlin 構文のベースライン

5. **Detekt Rules**
- ドキュメント: https://detekt.dev/docs/rules/style
- 参照目的:
  1. スタイルと保守性ルールのクロスチェック
  2. アンチパターンの命名の参照

## 再利用ポリシー

- OSS の関数/クラス本体をそのままコピーしないこと。
- 1つのソースから完全なシグネチャとクラス構造を複製しないこと。
- 例は教育的かつ合成したものにすること。
- ケースごとのソース参照は `context.md` のメタデータに記載すること。
