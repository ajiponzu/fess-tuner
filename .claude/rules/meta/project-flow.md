# プロジェクトの進め方

## フロー概要

```mermaid
flowchart TD
    A[作業開始] --> B[サーバー確認\nfess-check]
    B --> C[検索品質の観測\nfess-search]
    C --> D[改善案の立案\nAI が提示]
    D --> E{人間が承認}
    E -->|修正あり| D
    E -->|承認| F[設定変更・クロール実行\nfess-crawl]
    F --> G[効果検証\nfess-search]
    G --> H{改善されたか}
    H -->|不十分| C
    H -->|十分| I[セッション記録\nsession-handover]
    I --> J{次の作業}
    J -->|あり| A
    J -->|なし| K[完了]
```

## 詳細フロー

各フェーズの手順は対応する Skill に記述されている．

| フェーズ                     | Skill              |
| ---------------------------- | ------------------ |
| サーバー確認                 | `fess-check`       |
| 検索・効果検証               | `fess-search`      |
| クロール実行                 | `fess-crawl`       |
| セッション引き継ぎ（終了時） | `session-handover` |
| セッション引き継ぎ（開始時） | `session-override` |

## 進捗管理

- セッション記録: `sessions/` ディレクトリ
