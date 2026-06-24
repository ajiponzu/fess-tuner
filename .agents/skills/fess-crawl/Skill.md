---
name: fess-crawl
description: >
  Fess サーバーのクロールをトリガーし、クロール開始結果を報告する Skill。
---

# Fess Crawl

## 概要

この Skill は、Fess サーバー（`FESS_BASE_URL`）の管理 API にアクセスし、クローラージョブを即時起動する。

- インデックスを最新状態に更新したい場合に使う。
- 認証には `.env` の `FESS_ACCESS_TOKEN` を使う。
- Fess 15.6 の管理 API 認証は `Authorization: Bearer <token>` ヘッダーを使う。
- クロール実行は `PUT /api/admin/scheduler/{id}/start` を使う。
- `{id}` はジョブ ID。`default_crawler` が使えるかは環境依存のため、必要に応じて `GET /api/admin/scheduler/settings` で確認する。

## 実行条件

- Fess サーバーが起動していること。
- `.env` に `FESS_BASE_URL` と `FESS_ACCESS_TOKEN` が設定されていること。
- `FESS_ACCESS_TOKEN` が `admin-scheduler` または必要な管理 API 権限を持つこと。
- クロール実行についてユーザーの意図が明確であること。

## 入力

- 必須入力: なし
- 任意入力: なし

## 実行手順

1. この Skill の `SKILL.md` を読む。
2. `.env` に `FESS_ACCESS_TOKEN` が設定されていることを確認する。
3. 以下のコマンドを実行する。

   ```powershell
   python .agents/skills/fess-crawl/start_crawler.py
   ```

4. レスポンスの `response.status` が `0` であれば成功としてクロール開始を報告する。
5. エラーが返された場合は、内容を報告し `.env` の設定、権限、Docker コンテナの起動状態を確認する。

## 出力

以下を報告する。

- クロール開始の成否
- サーバー URL
- 対象ジョブ ID
- エラーが発生した場合の詳細

## 検証観点

- 管理 API が認証に成功すること。
- スケジューラー起動 API のレスポンスで `response.status` が `0` であること。
- 必要ならジョブログでクロール実行状態を確認できること。

## 注意

- アクセストークンなどの認証情報を出力しない。
- 実際のコマンド出力に存在しない情報を付け加えない。
- クロールはインデックス更新を伴うため、ユーザーの意図なく実行しない。
