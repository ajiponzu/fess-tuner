# 初期セットアップ

## .env ファイルの作成

リポジトリをクローンした後、プロジェクトルートに `.env` を作成すること。
このファイルは `.gitignore` により git 管理対象外となっている。

```
FESS_BASE_URL=http://piserver:8080
FESS_ADMIN_USER=admin
FESS_ADMIN_PASS=（実際のパスワードを記入）
```

## 注意事項

- `.env` が存在しない場合、各スクリプトは `FESS_BASE_URL=http://piserver:8080`、`FESS_ADMIN_USER=admin`、`FESS_ADMIN_PASS=` をデフォルト値として使用する
- `--user` / `--pass` 引数で実行時に上書きすることも可能
