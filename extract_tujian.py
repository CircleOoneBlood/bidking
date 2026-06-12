#!/usr/bin/env python3
"""BidKing 图鉴截图 → 物品占格提取。

用法: python3 extract_tujian.py <截图1.png> [截图2.png ...]

假设截图是 2x2 张卡片的图鉴页（手工裁剪允许几像素误差）。
每张卡片右下角的 6x6 点阵图标 = 物品形状（亮格为占格）。
输出: 每张卡片的占格数 + ASCII 形状；并在 /tmp/tujian_sheets/ 存
      放大图标拼图，供人工核对。
"""
import sys, os
from PIL import Image
import numpy as np

GRID = 6           # 图标点阵 6x6
BASE_CW = 475.0    # 基准卡片宽（950px 截图）
BASE_PITCH = 7.5   # 基准点阵间距

def patch_sum(ii, y, x, r=1):
    """3x3 patch 和（integral image 加速）"""
    y0, y1 = y - r, y + r + 1
    x0, x1 = x - r, x + r + 1
    return ii[y1, x1] - ii[y0, x1] - ii[y1, x0] + ii[y0, x0]

def detect_icon(card):
    """在卡片右下搜索 6x6 点阵：让「点中心亮度 − 格间隙亮度」最大。
    返回 (lit 6x6 bool, cell 均值矩阵, 窗口内 bbox)。"""
    H, W = card.shape
    win = card[int(H*0.46):int(H*0.80), int(W*0.78):W].astype(np.float64)
    wy, wx = int(H*0.46), int(W*0.78)
    ii = np.pad(win, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    pitch0 = BASE_PITCH * (W / BASE_CW)
    best = None
    for pitch in (pitch0*0.94, pitch0, pitch0*1.06):
        span = int(pitch*GRID) + 1
        for oy in range(0, win.shape[0]-span):
            for ox in range(0, win.shape[1]-span):
                dots = gaps = 0.0
                for i in range(GRID):
                    for j in range(GRID):
                        cy, cx = int(oy+i*pitch+pitch/2), int(ox+j*pitch+pitch/2)
                        dots += patch_sum(ii, cy, cx)
                        gaps += win[int(oy+i*pitch), int(ox+j*pitch)]
                score = dots/ (GRID*GRID*9) - gaps/(GRID*GRID)
                if best is None or score > best[0]:
                    best = (score, oy, ox, pitch)
    _, oy, ox, pitch = best
    m = np.zeros((GRID, GRID))
    for i in range(GRID):
        for j in range(GRID):
            cy, cx = int(oy+i*pitch+pitch/2), int(ox+j*pitch+pitch/2)
            m[i, j] = patch_sum(ii, cy, cx) / 9.0
    dim = np.median(m)            # 形状占少数格 → 中位数≈未占格亮度
    lit = m > dim + max(40.0, (m.max()-dim)*0.5)
    span = int(pitch*GRID)+2
    bbox = (wx+ox, wy+oy, wx+ox+span, wy+oy+span)
    return lit, m, bbox

def main(paths):
    os.makedirs('/tmp/tujian_sheets', exist_ok=True)
    for path in paths:
        im = Image.open(path)
        g = np.array(im.convert('L'))
        H, W = g.shape
        ch, cw = H/2, W/2
        crops = []
        print(f'=== {os.path.basename(path)} ({W}x{H}) ===')
        for r in range(2):
            for c in range(2):
                card = g[int(r*ch):int((r+1)*ch), int(c*cw):int((c+1)*cw)]
                lit, m, bb = detect_icon(card)
                n = int(lit.sum())
                shape = '\n'.join('  '+''.join('#' if v else '.' for v in row) for row in lit)
                print(f'[r{r}c{c}] 占格 = {n}')
                print(shape)
                x0, y0 = int(c*cw)+bb[0], int(r*ch)+bb[1]
                crop = Image.fromarray(g[y0:y0+(bb[3]-bb[1]), x0:x0+(bb[2]-bb[0])])
                crops.append(crop.resize((crop.width*6, crop.height*6), Image.NEAREST))
        # 拼图：4 个图标横排
        cw_, chh = max(c.width for c in crops), max(c.height for c in crops)
        sheet = Image.new('L', ((cw_+12)*4, chh+8), 255)
        for k, cr in enumerate(crops):
            sheet.paste(cr, (k*(cw_+12)+6, 4))
        out = f'/tmp/tujian_sheets/{os.path.splitext(os.path.basename(path))[0]}.png'
        sheet.save(out)
        print(f'核对拼图: {out}')

if __name__ == '__main__':
    main(sys.argv[1:])
