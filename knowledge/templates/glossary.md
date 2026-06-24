# Glossary Template

Copy this template to `knowledge/glossary.md` for local investigation use.
The runtime `knowledge/glossary.md` file is intentionally ignored by git.

## GPU / Async

| Japanese | English / Code Terms | Notes |
|---|---|---|
| 非同期 | async, asynchronous | GPU 初期化、GPU 実行、CPU 側待機の区別に注意する |
| 同期 | sync, synchronization | fence / semaphore / timeline と併用して探す |
| 転送 | transfer, upload, copy | resource transfer, transfer queue, staging buffer |
| 描画 | render, rendering, graphics | graphics queue, render pass, graphics pipeline |
| 計算 | compute, computing, computation | compute queue, compute pipeline |
| 並列 | parallel, overlap, concurrent | Transfer/Compute overlap も試す |
| セマフォ | semaphore | binary semaphore, timeline semaphore |
| フェンス | fence | CPU 側待機の文脈が多い |
| キュー | queue | graphics / compute / transfer queue |

## Candidate Terms

- リソース: resource, buffer, image
- 所有権移譲: ownership transfer, queue family ownership transfer
- バリア: barrier, memory barrier, image barrier
