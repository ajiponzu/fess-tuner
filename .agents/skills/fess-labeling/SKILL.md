---
name: fess-labeling
description: Fess 15.6 の管理 API を使って、このプロジェクト用のラベル体系を作成・更新し、FileConfig を整備し、クロール・設定リロード・label_updater による既存インデックスのラベル再計算まで実行する Skill。elpix / pandolabo や docs / source / other のラベル付けを適用・再適用・検証するときに使う。
---

# Fess Labeling

## 概要

この Skill は、Fess の LabelType と FileConfig を API 経由で整備し、検索インデックス上のラベルを再計算する。
実処理は Skill 直下の `apply_labeling.py` に集約している。

## 実行条件

- `.env` に `FESS_BASE_URL` と `FESS_ACCESS_TOKEN` が設定されていること。
- `FESS_ACCESS_TOKEN` は `admin-labeltype`, `admin-fileconfig`, `admin-scheduler` を含む管理 API 権限を持つこと。
- Fess サーバーが起動していること。
- ラベル体系または FileConfig を更新する意図がユーザーに確認されていること。

## 入力

- 必須入力: なし
- 任意入力:
  - ラベル体系の変更方針
  - 対象パスの追加・除外方針
  - クロールまたはラベル再計算の実行可否

## 実行手順

1. この Skill の `SKILL.md` を読む。
2. 必要に応じて `apply_labeling.py` の内容を確認する。
3. 以下を実行する。

   ```powershell
   python .agents/skills/fess-labeling/apply_labeling.py
   ```

4. スクリプトの出力を確認する。
   - LabelType が `created` または `updated` されること。
   - FileConfig が `created` または `updated` されること。
   - 旧 `var-www` FileConfig が残っている場合は `disabled` されること。
   - `default_crawler`, `reload_config`, `label_updater` が起動されること。
   - 最後に `/api/v1/labels` と `facet.field=label` の結果が表示されること。

5. `label_updater` は非同期ジョブのため、必要ならジョブログと検索 API で完了後の状態を確認する。

## 出力

以下を報告する。

- LabelType の作成・更新結果
- FileConfig の作成・更新結果
- 起動した scheduler ジョブ
- `/api/v1/labels` の公開ラベル確認結果
- `facet.field=label` によるラベル分布
- エラーが発生した場合の詳細

## 現在のラベル体系

- project 軸:
  - `elpix`
  - `pandolabo`
- content_type 軸:
  - `docs`
  - `source`
  - `other`

## 注意

- Fess 15.6 のデフォルトでは `form.admin.label.in.config.enabled=false` のため、FileConfig の `labelTypeIds` は保存・反映されないことがある。
- この Skill では LabelType の `includedPaths` / `excludedPaths` を主なラベル付けルールとして使う。
- LabelType の更新後は `reload_config` と `label_updater` を起動しないと、既存インデックスのラベルが再計算されない。
- 旧 `var-www` FileConfig は削除せず、`available=false` にする。
- アクセストークンは出力しない。
- インデックス削除、設定削除、広範囲の設定変更はユーザー確認なしに実行しない。

## 検証観点

- `GET /api/v1/labels` で 5 ラベルが返ること。
- `GET /api/v1/documents?q=*&num=0&facet.field=label&facet.size=50` で `elpix`, `pandolabo`, `docs`, `source`, `other` の分布が見えること。
- `fields.label=<label>` で各ラベルの絞り込み検索ができること。
