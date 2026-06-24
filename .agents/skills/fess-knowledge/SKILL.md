---
name: fess-knowledge
description: >
  Fess 調査結果を Markdown のナレッジとして knowledge/ に蓄積し、
  Q&A・根拠・有効クエリ・失敗クエリ・次回検索ヒントを再利用できる形で保存する Skill。
---

# Fess Knowledge

## 概要

この Skill は、Fess を使った調査結果を Markdown として保存する。
目的は、回答内容だけでなく検索の試行錯誤を残し、人間と AI の双方が次回以降の調査で再利用できるようにすること。

## 実行条件

- `knowledge/` が存在すること。
- `knowledge/templates/investigation.md` が存在すること。
- 保存する内容に `.env` やアクセストークンなどの秘密情報が含まれていないこと。

## 保存先

```text
knowledge/
├── README.md
├── glossary.md              # ローカル運用ファイル（git 管理外）
├── templates/
│   ├── investigation.md
│   └── glossary.md
└── investigations/
    └── YYYY-MM-DD-topic.md  # ローカル運用ファイル（git 管理外）
```

## 入力

- 必須:
  - 調査した質問
  - 回答の要約
  - 根拠文書
  - 有効だった検索語
  - 失敗した検索語
- 任意:
  - 未確認点
  - 次回試す検索語
  - Fess チューニング候補
  - glossary に追加する用語対応

## 実行手順

1. この Skill の `SKILL.md` を読む。
2. `knowledge/investigations/` がなければ作成する。
3. `knowledge/templates/investigation.md` を雛形として調査ログを作る。
4. ファイル名は `YYYY-MM-DD-topic.md` とし、topic は英数字とハイフン中心の短い名前にする。
5. `knowledge/glossary.md` がなければ `knowledge/templates/glossary.md` を参考に作る。
6. 必要に応じて `knowledge/glossary.md` に用語対応を追加する。

## 出力

以下のいずれか、または両方を作成・更新する。

- `knowledge/investigations/YYYY-MM-DD-topic.md`
- `knowledge/glossary.md`

## 検証観点

- 調査ログに Question / Answer / Evidence / Useful Queries / Failed Queries が含まれていること。
- 事実、推測、未確認点が分かれていること。
- 検索結果全文ではなく、文書名と要点だけが保存されていること。
- 接続先 Fess に依存する実データが git 管理対象になっていないこと。

## 調査ログ形式

```markdown
# <調査タイトル>

## Question

<ユーザーの質問>

## Answer

<短い結論>

## Evidence

- `<文書名>`: <根拠の要約>

## Confidence

- High / Medium / Low
- 理由: <確度の理由>

## Useful Queries

- `<query>`

## Failed Queries

- `<query>`

## Search Hints

- <次回同種の質問で試す検索語>

## Open Questions

- <未確認点>

## Fess Tuning Notes

- <synonym / label / 除外候補など>
```

## glossary の方針

- 追加は少量にする。
- まだ確信がない語は `Candidate Terms` に置く。
- Fess synonym へ反映する前の実験メモとして扱う。
- `knowledge/glossary.md` は接続先 Fess の内容に依存するため git 管理しない。

## 注意

- 調査ログは事実・推測・未確認点を分けて書く。
- 検索結果全文を貼り付けず、文書名と要点を残す。
- `.env` やアクセストークンなどの秘密情報は記録しない。
