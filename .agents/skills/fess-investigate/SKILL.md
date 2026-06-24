---
name: fess-investigate
description: >
  Fess の検索 API を使って、ユーザーの質問から複数の検索語を展開し、
  根拠・推測・未確認点を分けて調査回答するための Skill。
---

# Fess Investigate

## 概要

この Skill は、Fess を単発検索ではなく調査用に使う。
ユーザーの質問をそのまま検索するだけでなく、日本語・英語・コード識別子・関連概念へ展開し、複数回検索した結果から回答を組み立てる。

検索の試行錯誤そのものを後で再利用できるように、有効だった検索語と失敗した検索語も記録する。

## 入力

- 必須:
  - 調査したい質問
- 任意:
  - 対象プロジェクト名（例: `elpix`, `pandolabo`）
  - 優先ラベル（例: `docs`, `source`, `other`）
  - 調査ログを保存するかどうか

## 実行手順

1. この Skill の `SKILL.md` を読む。
2. 必要なら `.agents/skills/fess-search/Skill.md` と `search_documents.py` を確認する。
3. 質問を以下の観点で分解する。
   - 固有名詞
   - 日本語技術語
   - 英語技術語
   - コード識別子になりそうな語
   - 関連する API / クラス / ファイル名
4. まず質問に近い直接クエリを実行する。
5. 次に展開クエリを 3 から 8 個程度実行する。
6. 必要に応じて `--label docs`, `--label source`, `--label <project>` で再検索する。
7. 回答では以下を分けて書く。
   - 結論
   - 根拠
   - 推測
   - 未確認点
   - 検索品質上の気づき
8. 調査ログを残す場合は `fess-knowledge` Skill の形式で `knowledge/investigations/` に保存する。

## クエリ展開の例

### GPU / 非同期

```text
非同期, async, asynchronous
同期, sync, synchronization
転送, transfer, upload, copy
描画, render, rendering, graphics
計算, compute, computing, computation
並列, parallel, overlap, concurrent
セマフォ, semaphore
フェンス, fence
キュー, queue
タイムライン, timeline
```

### 検索パターン

```text
<質問の主要語をそのまま>
<project> <主要語>
<日本語語彙> <英語語彙>
<英語語彙> <コード識別子候補>
<関連クラス名> <関連概念>
```

## 出力形式

```markdown
## 結論

...

## 根拠

- ...

## 推測と未確認点

- ...

## 検索ログ

有効だった検索語:
- ...

失敗した検索語:
- ...

次回試す語:
- ...
```

## 注意

- 検索結果に存在しない情報を事実として断定しない。
- スニペットからの推測は推測と明示する。
- コード・設計として対応していることと、実行時に厳密に正しく動くことを分ける。
- Fess 側の設定変更やインデックス削除は行わない。
