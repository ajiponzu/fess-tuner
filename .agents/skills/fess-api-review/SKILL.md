---
name: fess-api-review
description: Fess 15.6 の公式 API ドキュメントを参照し、AGENTS.md や .agents/skills 配下の Fess 関連 Skill に書かれた API 利用方法を点検・修正するための Skill。エンドポイント、HTTP メソッド、認証ヘッダー、権限、レスポンス判定、破壊的操作の扱いを確認・是正するときに使う。
---

# Fess API Review

## 概要

この Skill は、プロジェクト内の Fess API 利用ルールを Fess 15.6 の公式ドキュメントに合わせて見直すために使う。
標準ではドキュメントと Skill 定義の修正だけを行い、ユーザーが明示しない限り実際の Fess サーバーには API リクエストを送らない。

## 作業手順

1. まずローカルの記述を読む。
   - `AGENTS.md`
   - `.agents/skills/` 配下の Skill 定義
   - `rg -n "Fess|fess|/api/|FESS_|fileconfig|scheduler|labeltype|joblog|failureurl" .agents/skills AGENTS.md` などで見つかる Fess API 関連記述
   - 新しい Fess 関連 Skill が追加されている場合は、その `SKILL.md` / `Skill.md` も対象に含める

2. 正誤判断の前に、Fess 15.6 の公式ドキュメントを確認する。
   - API index: `https://fess.codelibs.org/ja/15.6/api/index.html`
   - Search API: `https://fess.codelibs.org/ja/15.6/api/api-search.html`
   - Label API: `https://fess.codelibs.org/ja/15.6/api/api-label.html`
   - Health API: API index から該当ページを開く
   - Admin API overview: `https://fess.codelibs.org/ja/15.6/api/admin/api-admin-overview.html`
   - FileConfig: `https://fess.codelibs.org/ja/15.6/api/admin/api-admin-fileconfig.html`
   - Scheduler: `https://fess.codelibs.org/ja/15.6/api/admin/api-admin-scheduler.html`
   - 必要に応じて JobLog、FailureUrl、Documents、LabelType などの Admin API ページも確認する

3. ローカル記述と公式ドキュメントを以下の観点で照合する。
   - エンドポイントのパス
   - HTTP メソッド
   - 認証ヘッダーの形式
   - アクセストークンに必要な権限
   - リクエストパラメーターと JSON body
   - レスポンス形式と成功判定
   - ユーザー確認が必要な破壊的操作

4. 公式ドキュメント内に矛盾がある、または対象ページを開けない場合は、必要に応じて同じバージョンの Fess 実装を確認する。
   - 既知の導入バージョンが Fess 15.6 の場合は、GitHub の `fess-15.6.0` または該当 patch tag を優先する。
   - ルートコメントや Action メソッド名は実装上の根拠として扱う。
   - 最終報告では「公式ドキュメント上の記述」と「実装からの判断」を分けて説明する。

5. 必要なファイルだけを編集する。
   - 通常は `AGENTS.md`
   - Fess 関連の `.agents/skills/*/Skill.md` または `SKILL.md`
   - ユーザーが求めない限り、移行元資料、セッション記録、無関係な Skill は変更しない。

6. 修正後に確認する。
   - `rg` で古い記述が残っていないか探す。
   - 例:
     - `Bearer 不要`
     - `Authorization: <token>`
     - `/api/v1/search`
     - `default_crawler/start`
     - `job_log_id`
     - `.Codex/skills`
   - 最後に diff を確認して、修正範囲が依頼内容に収まっていることを確認する。

## Fess 15.6 の基本方針

公式ドキュメントまたはローカル環境で別の事実が確認できない限り、以下を基準にする。

- 公開検索 API は `GET /api/v1/documents` を使う。`/api/v1/search` は使わない。
- ラベルで検索結果を絞り込む場合は `fields.label=<label_value>` を使う。
- ラベル分布を確認する場合は `facet.field=label` を使う。
- 公開ラベル一覧は `GET /api/v1/labels` を使う。
- 管理 API の認証は `Authorization: Bearer <token>` を使う。
- 管理 API の成功判定は原則として `response.status == 0` とする。
- スケジューラー起動は `PUT /api/admin/scheduler/{id}/start` を使う。
- `{id}` はスケジューラージョブ ID であり、固定文字列として扱う前に `/api/admin/scheduler/settings` で確認する。
- ファイルクロール設定にラベルを付ける場合は `labelTypeIds` に LabelType の ID を指定する。
- 公開検索に出す権限は、ローカル環境で別事実がない限り `guest` のようなロール名で扱う。

## 安全ルール

- API 記述の見直し中に、破壊的 API を実行しない。
- 削除、設定更新、ジョブ停止、バックアップ import、ドキュメント削除は、必ずユーザー確認を得てから実行する。
- アクセストークンを出力に含めない。
- 観測結果からの推測は、事実として断定せず「推測」または「実装からの判断」として示す。
- 最終報告には、参照した公式ドキュメントの URL を含める。
