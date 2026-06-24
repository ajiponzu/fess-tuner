---
name: fess-check
description: >
  Fess サーバーのヘルスチェックを行い、サーバーの稼働状態を確認・報告する Skill。
---

# Fess Check

## 概要

この Skill は、Fess サーバー（`FESS_BASE_URL`）に対してヘルスチェックリクエストを送信し、サーバーが正常に稼働しているか確認する。

- Docker コンテナ上で動作する Fess サーバーの状態確認に使用する。
- `fess-search` や `fess-crawl` を実行する前の前提確認として使う。
- エンドポイント: `GET /api/v1/health`（認証不要・公開 API）

## 実行条件

- `.env` の `FESS_BASE_URL` が設定されていること。
- `FESS_BASE_URL` には接続先 Fess の URL を記載する。
- `FESS_BASE_URL` が未設定の場合は、ローカル実行向け fallback として `http://localhost:8080` を使う。

## 入力

- 必須入力: なし
- 任意入力: なし

## 実行手順

1. この Skill の `SKILL.md` を読む。
2. 以下のコマンドを実行する。

   ```powershell
   python .agents/skills/fess-check/check_health.py
   ```

3. コマンドの出力を確認する。
4. HTTP ステータスコードが `200` かつ `data.status` が `green` であれば、サーバー稼働中と報告する。
5. リクエストが失敗した場合は、エラー内容と確認すべき事項を報告する。

## 出力

以下を簡潔に報告する。

- Fess サーバーの稼働状態（正常 / 異常）
- HTTP ステータスコード
- サーバー URL
- エラーが発生した場合の詳細

## 検証観点

- HTTP ステータスコードが `200` であること。
- レスポンスの `data.status` が `green` であること。
- レスポンスの `data.timed_out` が `false` であること。

## 注意

- 実際のコマンド出力に存在しない情報を付け加えない。
- 異常時は推測で原因を断定せず、Docker コンテナ起動状態、URL、ネットワーク到達性など確認すべき点を示す。
