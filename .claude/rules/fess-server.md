# Fess サーバー環境

## 接続情報

- サーバーURL: `http://piserver:8080`（`.env` の `FESS_BASE_URL` で管理）
- 実行環境: Docker コンテナ
- Fess バージョン: 15.6

## API エンドポイント

### 公開 API（認証不要）

| エンドポイント | メソッド | 用途 |
|---|---|---|
| `/api/v1/health` | GET | ヘルスチェック |
| `/api/v1/documents` | GET | ドキュメント検索（`?q=<query>&num=<N>`） |

- `/api/v1/search` は存在しない（誤りやすいので注意）

### 管理 API（要認証）

- 認証方式: `Authorization: <token>` ヘッダー（**Bearer 不要**）
- トークンは Fess 管理画面 > System > Access Token で発行
- トークンの Permission は `{role}admin-api` を設定すること

| エンドポイント | メソッド | 用途 |
|---|---|---|
| `/api/admin/scheduler/settings` | GET | スケジューラー一覧 |
| `/api/admin/scheduler/default_crawler/start` | **PUT** | クロール即時実行 |
| `/api/admin/fileconfig/settings` | GET | ファイル設定一覧 |
| `/api/admin/fileconfig/setting` | POST | ファイル設定作成 |
| `/api/admin/joblog/logs` | GET | クロールジョブログ |
| `/api/admin/failureurl/logs` | GET | クロールエラーログ |

- Fess 15.x では一部操作が POST → PUT に変わっている（特にスケジューラー起動）

## データパス

- クロール対象データの配置先: `/var/www`（Fess コンテナ内から見たパス）
- ファイル設定の `paths` フィールドには `file:///var/www` 形式で指定する
- ホスト側のパスとのマッピングはホスト環境に依存する

## 注意事項

- クロールを実行するまでインデックスは空の状態である
- 管理 API の認可は `api.admin.access.permissions=Radmin-api` の単一設定で全エンドポイントに適用される
- ファイル設定の `permissions` フィールドは検索時のアクセス制御に影響する（`{role}guest` で一般公開）
