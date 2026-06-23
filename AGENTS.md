# fess-tuner プロジェクト方針

## 目的

ローカルに構築した Fess サーバー（Docker, `http://piserver:8080`）に対して、
API を介して外部からチューニングを行い、**データソースとしての検索品質を継続的に高めること**。

チューニングの中心は**クロール時のラベル付け**であり、ドキュメントに適切なラベルを付与することで
検索精度・絞り込み精度を向上させることを主目的とする。

---

## Codex でのルール配置

Codex では、この `AGENTS.md` をプロジェクト全体の常時適用ルールとして扱う。

- 常時守る方針・制約は `AGENTS.md` に集約する
- 特定作業で再利用する手順は `.agents/skills/<skill-name>/SKILL.md` に置く
- セッション間の記録は `sessions/` に置く
- `.claude/` と `claude *.md` は Claude からの移行元資料であり、Codex の常時ルールとしては期待しない

---

## Fess サーバー環境

### 接続情報

- サーバー URL: `http://piserver:8080`（`.env` の `FESS_BASE_URL` で管理）
  - `.env`のテンプレは下記
  ```
  FESS_BASE_URL=http://xxxxxxxx:8080
  FESS_ADMIN_USER=admin
  FESS_ACCESS_TOKEN=xxxxxxxxxx
  ```
- 実行環境: Docker コンテナ
- Fess バージョン: 15.6
- HTTP クライアントは `requests` ライブラリを使用する

### `.env`

プロジェクトルートに `.env` を置く。このファイルは git 管理対象外。

```env
FESS_BASE_URL=http://piserver:8080
FESS_ACCESS_TOKEN=発行したアクセストークン
```

- `FESS_BASE_URL` を省略した場合は `http://piserver:8080` をデフォルト値として使用する
- `FESS_ACCESS_TOKEN` が未設定の場合、管理 API を使う処理は実行できない

### Access Token

Fess 管理画面で `System > Access Token` を開き、管理 API に必要な権限を持つトークンを発行する。

- Name: 任意（例: `fess-tuner`）
- Permission: `admin-*` または対象 API に応じた権限（例: `admin-scheduler`, `admin-fileconfig`, `admin-labeltype`）

管理 API の認証は `Authorization: Bearer <token>` ヘッダーを使う。

---

## API エンドポイント

### 公開 API（認証不要）

| エンドポイント          | メソッド | 用途                                                  |
| ----------------------- | -------- | ----------------------------------------------------- |
| `/api/v1/health`        | GET      | ヘルスチェック                                        |
| `/api/v1/documents`     | GET      | ドキュメント検索（`?q=<query>&num=<N>`）              |
| `/api/v1/documents/all` | GET      | 全ドキュメント検索（`api.search.scroll=true` が必要） |
| `/api/v1/labels`        | GET      | 公開検索で利用できるラベル一覧                        |

- `/api/v1/search` は存在しないため使用しない
- ラベルで絞り込む場合は `/api/v1/documents?q=<query>&fields.label=<label_value>` を使う
- ラベル分布を確認する場合は `/api/v1/documents?q=<query>&facet.field=label` を使う

### 管理 API（要認証）

| エンドポイント                       | メソッド | 用途                         |
| ------------------------------------ | -------- | ---------------------------- |
| `/api/admin/scheduler/settings`      | GET/PUT  | スケジューラー一覧           |
| `/api/admin/scheduler/{id}/start`    | PUT      | ジョブ即時実行               |
| `/api/admin/scheduler/{id}/stop`     | PUT      | 実行中ジョブ停止             |
| `/api/admin/fileconfig/settings`     | GET/PUT  | ファイル設定一覧             |
| `/api/admin/fileconfig/setting/{id}` | GET      | ファイル設定取得             |
| `/api/admin/fileconfig/setting`      | POST     | ファイル設定作成             |
| `/api/admin/fileconfig/setting`      | PUT      | ファイル設定更新             |
| `/api/admin/fileconfig/setting/{id}` | DELETE   | ファイル設定削除             |
| `/api/admin/labeltype/settings`      | GET/PUT  | ラベルタイプ一覧             |
| `/api/admin/labeltype/setting/{id}`  | GET      | ラベルタイプ取得             |
| `/api/admin/labeltype/setting`       | POST     | ラベルタイプ作成             |
| `/api/admin/labeltype/setting`       | PUT      | ラベルタイプ更新             |
| `/api/admin/labeltype/setting/{id}`  | DELETE   | ラベルタイプ削除             |
| `/api/admin/joblog/logs`             | GET      | ジョブログ一覧               |
| `/api/admin/joblog/log/{id}`         | GET      | ジョブログ詳細               |
| `/api/admin/failureurl/logs`         | GET/PUT  | クロール失敗 URL 一覧        |
| `/api/admin/failureurl/log/{id}`     | GET      | クロール失敗 URL 詳細        |
| `/api/admin/documents`               | DELETE   | クエリ指定でドキュメント削除 |
| `/api/admin/documents/{id}`          | DELETE   | ID 指定でドキュメント削除    |

- Fess 15.x では一部操作が POST ではなく PUT。特にスケジューラー起動は `PUT` を使う
- スケジューラー起動の `{id}` はジョブ ID。`default_crawler` は環境依存の ID として扱い、必要なら `/api/admin/scheduler/settings` で確認する
- 公式 API ガイド本文では JobLog / FailureUrl の一部パスが `/api/admin/joblog`, `/api/admin/failureurl` と説明されているが、Fess 15.6.0 の実装では `/logs` / `/log/{id}` が定義されているため、実行時はローカル環境で確認する
- 管理 API のレスポンスは通常 `response.status` が `0` のとき成功として扱う
- ドキュメント削除、設定削除、ジョブ停止、設定更新は破壊的または影響範囲が大きいため、ユーザー確認なしに実行しない

---

## データパスとクロール設定

- クロール対象データの配置先: `/var/www`（Fess コンテナ内から見たパス）
- ファイル設定の `paths` フィールドには `file:///var/www` 形式で指定する
- ホスト側のパスとのマッピングはホスト環境に依存する
- クロールを実行するまでインデックスは空の状態である
- ファイル設定の `permissions` は検索時のアクセス制御に影響する
- 公開検索 API から検索できるようにする場合は `guest` を使う
- ファイル設定にラベルを付ける場合は `labelTypeIds` に `/api/admin/labeltype/settings` で確認したラベルタイプ ID を指定する

---

## Skill

| Skill              | 用途                                   |
| ------------------ | -------------------------------------- |
| `fess-check`       | サーバー死活確認（前提チェック）       |
| `fess-search`      | 検索クエリを投げて結果を確認           |
| `fess-crawl`       | クロール（インデックス更新）をトリガー |
| `session-override` | 前回セッションの引き継ぎ               |
| `session-handover` | 今回セッションの記録                   |

Skill を使うときは、該当する `.agents/skills/<skill-name>/SKILL.md` を読んでから実行する。

---

## チューニングの考え方

### ラベル付けが主軸

クロール設定においてドキュメントに適切なラベルを付与することが最も重要な施策である。
ラベルにより検索結果の分類・絞り込みが可能になり、検索の有用性が大きく向上する。

### 改善サイクル

1. **観測 → 仮説 → 変更 → 検証** のサイクルを回す
   - `fess-search` で現状の検索品質を観測
   - ラベル設定・クロール設定の改善点を特定
   - 設定変更案を提示し、必要に応じてユーザー確認を得る
   - 設定を変更し、再クロールをトリガー
   - 同じクエリで再検索して効果を確認

2. **定量的な評価を重視する**
   - 改善前後でヒット件数・上位 URL・ラベル分布の変化を記録する

3. **破壊的変更は行わない**
   - インデックス削除・設定の大幅変更はユーザー確認を得てから実施する

---

## 作業フロー

1. 作業開始時に `fess-check` でサーバー稼働を確認する
2. 前回セッションがあれば `session-override` で引き継ぐ
3. 今回の目標クエリ・改善対象を確認する
4. `fess-search` で検索品質を観測する
5. 改善案を立案し、必要な承認を得る
6. 設定変更・クロール実行を行う
7. 同じ検索条件で効果検証する
8. 終了時に必要なら `session-handover` で記録する

---

## AI の役割

- Fess API を用いた観測・分析（ヘルスチェック・検索・クロール実行）
- 検索結果の品質評価と改善案の提示
- ラベル付け施策の立案・優先順位付け
- Skill の実行と結果解釈
- セッション記録の作成・引き継ぎ

## ユーザーの役割（AI は代行しない）

- ラベル体系・チューニング方針の最終決定
- 設定変更の承認（特に破壊的変更）
- Fess 管理画面での手動操作が必要な設定
- セッション記録のレビューと次回方針の確定

## AI への制約

- ユーザー確認なしに破壊的変更（インデックス削除・設定の大幅変更）を実行しない
- 観測結果から得た仮説を事実として断定しない
- チューニング方針をユーザーの意図なく独自に決定しない
- 結果だけでなく、判断に使った根拠も人間が理解できる粒度で示す

---

## ファイル配置 (随時更新)

```text
fess-tuner/
├── AGENTS.md                 # Codex 向けプロジェクト方針
├── .agents/
│   └── skills/               # Codex で使う Skill 定義
│       ├── fess-check/
│       ├── fess-search/
│       ├── fess-crawl/
│       ├── session-handover/
│       └── session-override/
├── .claude/                  # Claude からの移行元資料
└── sessions/                 # セッション記録（git 管理外）
```
