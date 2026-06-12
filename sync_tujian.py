#!/usr/bin/env python3
"""把 tujian.md 的紫色/金色条目同步进页面的 TUJIAN 数据块。

用法: python3 sync_tujian.py   （在项目根目录跑）
tujian.md 是 master，每次增改条目后跑一遍即可。
本地页面叫 v2.html，仓库里叫 index.html，脚本两个都认。
"""
import re, os, sys

root = os.path.dirname(os.path.abspath(__file__))
PAGE = 'v2.html' if os.path.exists(os.path.join(root, 'v2.html')) else 'index.html'
md = open(os.path.join(root, 'tujian.md'), encoding='utf-8').read()

def section(title):
    m = re.search(r'#\s*' + title + r'\s*\n(.*?)(?=\n#|\Z)', md, re.S)
    rows, skipped = [], 0
    if m:
        for line in m.group(1).strip().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = [x.strip() for x in re.split('[，,]', line)]
            if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit():
                skipped += 1
                continue
            rows.append(f"['{parts[0]}',{int(parts[1])},{int(parts[2])}]")
    return rows, skipped

blocks, report = [], []
for title, var in [('紫色', 'TUJIAN_PURPLE'), ('金色', 'TUJIAN_GOLD')]:
    rows, skipped = section(title)
    body = ('[\n  ' + ',\n  '.join(rows) + '\n  ]') if rows else '[]'
    blocks.append(f'const {var}={body};')
    report.append(f'{title} {len(rows)} 件' + (f'（跳过 {skipped} 行）' if skipped else ''))

js = '\n  '.join(blocks)
path = os.path.join(root, PAGE)
html = open(path, encoding='utf-8').read()
new = re.sub(r'/\*TUJIAN_START\*/.*?/\*TUJIAN_END\*/',
             '/*TUJIAN_START*/\n  ' + js + '\n  /*TUJIAN_END*/',
             html, flags=re.S)
open(path, 'w', encoding='utf-8').write(new)
print(f'同步 → {PAGE}：' + '，'.join(report))
