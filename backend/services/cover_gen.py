"""算法生成书籍封面 PNG（Pillow），供 PDF / DOCX / EPUB 导出嵌入。

与前端 BookCover.jsx 同思路：以书名+id 为种子的确定性随机，
调色板 + 图案算法 + 书名艺术字拼贴。不要求与前端像素一致，只求风格一致、同书稳定。
"""

import io
import math
import random
import sys
from pathlib import Path

W, H = 600, 800

PALETTES = [
    {"bg": ("#1e1b4b", "#312e81"), "accents": ["#a5b4fc", "#f472b6", "#facc15"], "text": "#ffffff"},
    {"bg": ("#7f1d1d", "#991b1b"), "accents": ["#fca5a5", "#fde047", "#fdba74"], "text": "#fff7ed"},
    {"bg": ("#064e3b", "#065f46"), "accents": ["#6ee7b7", "#fde68a", "#a7f3d0"], "text": "#ecfdf5"},
    {"bg": ("#0c4a6e", "#075985"), "accents": ["#7dd3fc", "#fbbf24", "#f0abfc"], "text": "#f0f9ff"},
    {"bg": ("#581c87", "#6b21a8"), "accents": ["#e9d5ff", "#fb7185", "#fcd34d"], "text": "#faf5ff"},
    {"bg": ("#27272a", "#18181b"), "accents": ["#f59e0b", "#ef4444", "#e4e4e7"], "text": "#fafafa"},
    {"bg": ("#fef3c7", "#fde68a"), "accents": ["#b45309", "#1c1917", "#dc2626"], "text": "#451a03"},
    {"bg": ("#ecfeff", "#cffafe"), "accents": ["#0e7490", "#1e293b", "#e11d48"], "text": "#164e63"},
    {"bg": ("#831843", "#9d174d"), "accents": ["#f9a8d4", "#fde047", "#c7d2fe"], "text": "#fdf2f8"},
    {"bg": ("#14532d", "#166534"), "accents": ["#bbf7d0", "#fb923c", "#fef08a"], "text": "#f0fdf4"},
]


def _hash(s: str) -> int:
    h = 2166136261
    for ch in s or "":
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def _hex_rgba(hex_color: str, alpha: int = 255):
    hex_color = hex_color.lstrip("#")
    return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), alpha)


def _find_font():
    """找一个支持中日韩的系统字体；找不到就退化到默认字体。"""
    candidates = []
    if sys.platform == "win32":
        fonts = Path("C:/Windows/Fonts")
        candidates = [fonts / n for n in ("msyhbd.ttc", "msyh.ttc", "simhei.ttf", "simsun.ttc", "arialbd.ttf", "arial.ttf")]
    elif sys.platform == "darwin":
        candidates = [Path("/System/Library/Fonts/PingFang.ttc"), Path("/System/Library/Fonts/STHeiti Medium.ttc")]
    else:
        candidates = [
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def _bg_gradient(draw, p):
    c1 = _hex_rgba(p["bg"][0])
    c2 = _hex_rgba(p["bg"][1])
    for y in range(H):
        t = y / H
        col = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,)
        draw.line([(0, y), (W, y)], fill=col)


def _pattern(layer_draw, r: random.Random, p):
    kind = r.randrange(5)
    accents = p["accents"]
    if kind == 0:  # 圆
        for _ in range(4 + r.randrange(5)):
            cx, cy = r.random() * W, r.random() * H * 0.7
            rad = 36 + r.random() * 140
            color = _hex_rgba(r.choice(accents), int(50 + r.random() * 70))
            bbox = [cx - rad, cy - rad, cx + rad, cy + rad]
            if r.random() > 0.4:
                layer_draw.ellipse(bbox, fill=color)
            else:
                layer_draw.ellipse(bbox, outline=color, width=4 + r.randrange(6))
    elif kind == 1:  # 斜条纹
        for i in range(6 + r.randrange(6)):
            y = (H / 8) * i + r.random() * 40 - 100
            thick = 8 + r.random() * 30
            color = _hex_rgba(r.choice(accents), int(40 + r.random() * 60))
            layer_draw.polygon(
                [(-50, y), (W + 50, y - 160), (W + 50, y - 160 + thick), (-50, y + thick)],
                fill=color,
            )
    elif kind == 2:  # 三角
        for _ in range(6 + r.randrange(6)):
            x, y = r.random() * W, r.random() * H * 0.72
            s = 50 + r.random() * 130
            ang = r.random() * math.pi * 2
            pts = []
            for k in range(3):
                a = ang + k * 2 * math.pi / 3
                pts.append((x + math.cos(a) * s / 2, y + math.sin(a) * s / 2))
            layer_draw.polygon(pts, fill=_hex_rgba(r.choice(accents), int(40 + r.random() * 65)))
    elif kind == 3:  # 网格点
        cell = 70 + r.randrange(50)
        for gx in range(cell // 2, W, cell):
            for gy in range(cell // 2, int(H * 0.72), cell):
                if r.random() > 0.55:
                    continue
                color = _hex_rgba(r.choice(accents), 110)
                rad = cell * 0.22
                if r.random() < 0.5:
                    layer_draw.ellipse([gx - rad, gy - rad, gx + rad, gy + rad], fill=color)
                else:
                    layer_draw.rectangle([gx - rad, gy - rad, gx + rad, gy + rad], fill=color)
    else:  # 放射线
        cx, cy = r.random() * W, r.random() * H * 0.35
        n = 10 + r.randrange(10)
        for i in range(n):
            ang = 2 * math.pi * i / n + r.random() * 0.2
            ln = 160 + r.random() * 400
            color = _hex_rgba(r.choice(accents), int(60 + r.random() * 70))
            layer_draw.line(
                [(cx, cy), (cx + math.cos(ang) * ln, cy + math.sin(ang) * ln)],
                fill=color, width=3 + r.randrange(5),
            )
        layer_draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=_hex_rgba(accents[0], 150))


def _title_collage(img, draw, r: random.Random, p, title: str, font_path):
    from PIL import Image, ImageFont, ImageDraw

    raw = (title or "无题").strip()
    is_cjk = any("一" <= c <= "鿿" or "぀" <= c <= "ヿ" or "가" <= c <= "힯" for c in raw)
    units = list(raw) if is_cjk else [w for w in raw.split() if w]

    # 仅在极长时才截断，尽量完整显示（字号随长度自适应缩小）
    max_units = 24 if is_cjk else 10
    truncated = len(units) > max_units
    if truncated:
        units = units[:max_units]
    if not units:
        units = ["?"]
    n = len(units)

    # 文字区域：纵向居中（约 30%~88%）
    area_x = W * 0.08
    area_w = W * 0.84
    area_top = H * 0.30
    area_h = H * 0.58

    # 根据字符数决定网格，使整块标题铺满区域且接近正方形
    if is_cjk:
        if n <= 3:
            cols, rows = n, 1
        else:
            aspect = area_w / area_h
            cols = max(2, min(n, round(math.sqrt(n * aspect))))
            rows = math.ceil(n / cols)
    else:
        cols, rows = 1, n

    cell_w = area_w / cols
    cell_h = area_h / rows

    # 基准字号：CJK 由格子尺寸决定；拉丁由最长单词宽度 + 行高决定，确保不溢出
    if is_cjk:
        base = min(min(cell_w, cell_h) * 0.82, H * 0.30)
    else:
        max_word_len = max((len(w) for w in units), default=1)
        by_width = area_w / (max_word_len * 0.58)
        by_height = cell_h * 0.8
        base = min(by_width, by_height, H * 0.18)

    for i, u in enumerate(units):
        row, col = divmod(i, cols)
        items_in_row = min(cols, n - row * cols)
        row_start_x = area_x + (area_w - cell_w * items_in_row) / 2
        cx = row_start_x + cell_w * col + cell_w / 2 + (r.random() - 0.5) * cell_w * 0.10
        cy = area_top + cell_h * row + cell_h / 2 + (r.random() - 0.5) * cell_h * 0.08
        size = max(8, int(base * (0.9 + r.random() * 0.2)))
        color = _hex_rgba(r.choice(p["accents"])) if r.random() > 0.62 else _hex_rgba(p["text"])
        rot = (r.random() - 0.5) * 12

        try:
            font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        # 单字/词画到独立小图再旋转，贴回主图（拼贴感），文字在小图内居中
        pad = size
        tile = Image.new("RGBA", (size * max(len(u), 1) + pad * 2, size + pad * 2), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        try:
            bbox = td.textbbox((0, 0), u, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tx = (tile.width - tw) / 2 - bbox[0]
            ty = (tile.height - th) / 2 - bbox[1]
        except Exception:
            tx = ty = pad
        td.text((tx, ty), u, font=font, fill=color)
        tile = tile.rotate(rot, expand=True, resample=Image.BICUBIC)
        crop = tile.getbbox()
        if crop:
            tile = tile.crop(crop)
        img.alpha_composite(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)))


def generate_cover_png(title: str, book_id: str = "") -> bytes:
    """生成 600x800 封面 PNG bytes。Pillow 缺失时抛 ImportError，由调用方降级。"""
    from PIL import Image, ImageDraw

    seed = _hash(f"{title or ''}::{book_id or ''}")
    r = random.Random(seed)
    p = PALETTES[seed % len(PALETTES)]

    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    _bg_gradient(draw, p)

    # 图案画在半透明图层上
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _pattern(ImageDraw.Draw(layer), r, p)
    img.alpha_composite(layer)

    # 标题区压暗（覆盖自适应文字区域）
    shade = Image.new("RGBA", (W, int(H * 0.64)), _hex_rgba(p["bg"][0], 82))
    img.alpha_composite(shade, (0, int(H * 0.26)))

    _title_collage(img, draw, r, p, title, _find_font())

    # 书脊侧光
    d2 = ImageDraw.Draw(img)
    d2.rectangle([0, 0, 18, H], fill=(0, 0, 0, 46))
    d2.rectangle([18, 0, 24, H], fill=(255, 255, 255, 30))

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


def try_generate_cover(title: str, book_id: str = "") -> bytes | None:
    """安全版：任何异常（如未装 Pillow、无字体）都返回 None，导出继续无封面。"""
    try:
        return generate_cover_png(title, book_id)
    except Exception as e:
        print(f"[Cover] generate failed: {e}")
        return None
