# BidKing 估价助手（数格子流 · 伊森）

竞拍之王（BidKing）仓库估价网页工具：单文件、无依赖、深色、localStorage 存档。

- **在线使用**：https://circleooneblood.github.io/bidking/
- `index.html` — 工具本体（基础模式 = 颜色单价 × 比例；进阶模式 = 均格/均价推断 + 图鉴组合求解 + 联合候选）
- `tujian.md` — 图鉴数据 master（紫 103 件、金 100 件），格式一行一件：`名称，价格，占格`
- `sync_tujian.py` — 本地把 tujian.md 同步进工具的数据块
- `extract_tujian.py` — 从游戏图鉴截图自动提取物品占格（PIL + numpy）

仅供游戏辅助参考。
