---
name: fess-search
description: >
  Fess サーバーに対してドキュメント検索を実行し、検索結果を読みやすい形式で報告する Skill。
---

# Fess Search

## 概要

この Skill は、ユーザーが指定した検索クエリを Fess サーバー（`FESS_BASE_URL`）に送信し、マッチしたドキュメントを確認する。

- インデックスされたドキュメントの内容確認や情報検索に使う。
- 検索件数は `--num` で調整する。
- ラベルで絞り込む場合は `fields.label=<label_value>` を使う。
- ラベル分布を確認する場合は `facet.field=label` を使う。
- エンドポイント: `GET /api/v1/documents`（認証不要・公開 API）
- `/api/v1/search` は存在しないため使用しない。

## 実行条件

- Fess サーバーが起動していること。
- `.env` の `FESS_BASE_URL` が設定されていること。
- `FESS_BASE_URL` には接続先 Fess の URL を記載する。
- `FESS_BASE_URL` が未設定の場合は、ローカル実行向け fallback として `http://localhost:8080` を使う。

## 入力

- 必須入力:
  - 検索クエリ（例: `python`, `gpu_context`, `pandolabo`）
- 任意入力:
  - `--num N`: 取得する検索結果の件数（省略時: 5）
  - `--label LABEL`: `fields.label` によるラベル絞り込み

## 実行手順

1. この Skill の `SKILL.md` を読む。
2. ユーザーが指定したクエリと任意オプションを確認する。
3. 以下のコマンドを実行する。

   ```powershell
   python .agents/skills/fess-search/search_documents.py <query> --num 5
   ```

4. ラベルで絞り込む場合は以下のように実行する。

   ```powershell
   python .agents/skills/fess-search/search_documents.py <query> --num 5 --label <label>
   ```

5. レスポンスの `record_count` と `data` 配列を確認する。
6. タイトル、URL、スニペットを一覧で報告する。

## 出力

以下を報告する。

- 検索クエリ
- 総ヒット件数（`record_count`）
- 各検索結果のタイトル（`title`）
- URL（`url_link`）
- スニペット（`digest`）

## 検証観点

- HTTP ステータスコードが `200` であること。
- `record_count` が取得できること。
- `data` 配列の `title`, `url_link`, `digest` を確認できること。

## 注意

- 検索結果に存在しない情報を補完・推測して追記しない。
- HTML エンティティ（`&#034;` など）は必要に応じて読みやすく解釈する。
- 結果が 0 件の場合は、該当ドキュメントが見つからなかったことを明示し、必要なら別クエリを提案する。
