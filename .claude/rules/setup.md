# 初期セットアップ

## .env ファイルの作成

リポジトリをクローンした後、プロジェクトルートに `.env` を作成すること。
このファイルは `.gitignore` により git 管理対象外となっている。

```
FESS_BASE_URL=http://piserver:8080
FESS_ACCESS_TOKEN=（発行したアクセストークンを記入）
```

## Access Token の発行手順

1. ブラウザで Fess 管理画面（`FESS_BASE_URL/login/`）にログイン
2. **System > Access Token** を開く
3. 右上の「New」をクリックし、以下の設定で作成
   - Name: 任意（例: `fess-tuner`）
   - Permission: `{role}admin-api`
4. 表示された Token 文字列を `FESS_ACCESS_TOKEN` に記入

## 注意事項

- `FESS_ACCESS_TOKEN` が未設定の場合、`fess-crawl` は起動時にエラーで終了する
- `FESS_BASE_URL` を省略した場合は `http://piserver:8080` がデフォルト値として使用される
