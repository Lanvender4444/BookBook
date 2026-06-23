"""写入书本时的内容工具：表格生成 + SVG 图生成。

与 search/RAG 不同，这两个是「写作时」工具：模型在章节正文里用约定的
```tool JSON 块调用，我们的代码把它渲染成可嵌入正文的产物：
- table → GFM Markdown 表格（reader 用 remark-gfm 渲染，导出可转 <table>）
- svg   → 由结构化数据确定性生成的 SVG 图（柱状/折线/饼图），或直接嵌入模型给的原始 SVG

调用协议（模型在正文中插入）：
```tool
{"tool": "table", "title": "可选标题", "headers": ["列A","列B"], "rows": [["1","2"],["3","4"]]}
```
```tool
{"tool": "svg", "kind": "bar|line|pie", "title": "图标题", "data": [{"label":"甲","value":10}], "caption": "可选说明"}
```
```tool
{"tool": "svg", "kind": "raw", "svg": "<svg ...>...</svg>", "caption": "可选说明"}
```
"""

import html
import json
import re

TOOL_BLOCK_RE = re.compile(r"```tool\s*\n(.*?)```", re.S)

PALETTE = ["#4f46e5", "#0d9488", "#dc2626", "#d97706", "#7c3aed", "#2563eb", "#059669", "#be185d"]

SVG_W, SVG_H = 640, 380


# ---------------------------------------------------------------- 表格

def render_table_md(spec: dict) -> str:
    headers = [str(h).strip() for h in (spec.get("headers") or [])]
    rows = spec.get("rows") or []
    if not headers or not rows:
        return ""

    def esc(c):
        return str(c).replace("|", "\\|").replace("\n", " ").strip()

    lines = ["| " + " | ".join(esc(h) for h in headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        cells = [esc(c) for c in row]
        # 补齐/截断到表头列数
        cells = (cells + [""] * len(headers))[: len(headers)]
        lines.append("| " + " | ".join(cells) + " |")

    out = "\n".join(lines)
    title = (spec.get("title") or "").strip()
    if title:
        out = f"**{esc(title)}**\n\n{out}"
    return out


# ---------------------------------------------------------------- SVG 图

_SCRIPT_RE = re.compile(r"<script[\s\S]*?</script>", re.I)
_ON_ATTR_RE = re.compile(r'\son\w+\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)', re.I)
_HREF_JS_RE = re.compile(r'(href|xlink:href)\s*=\s*("javascript:[^"]*"|\'javascript:[^\']*\')', re.I)


def sanitize_svg(svg: str) -> str:
    """去掉脚本 / 事件处理 / javascript: 链接，避免嵌入恶意 SVG。"""
    if not svg:
        return ""
    svg = _SCRIPT_RE.sub("", svg)
    svg = _ON_ATTR_RE.sub("", svg)
    svg = _HREF_JS_RE.sub("", svg)
    # 仅保留第一个 <svg>...</svg>
    m = re.search(r"<svg[\s\S]*?</svg>", svg, re.I)
    return m.group(0) if m else ""


def _nums(data):
    out = []
    for d in data:
        try:
            out.append((str(d.get("label", "")), float(d.get("value", 0))))
        except (TypeError, ValueError):
            continue
    return out


def _svg_bar(points, title):
    pad_l, pad_b, pad_t, pad_r = 50, 50, 40, 20
    cw = SVG_W - pad_l - pad_r
    ch = SVG_H - pad_t - pad_b
    vmax = max((v for _, v in points), default=1) or 1
    n = len(points)
    gap = cw / n
    bw = gap * 0.6
    parts = [f'<text x="{SVG_W/2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f2937">{html.escape(title)}</text>']
    parts.append(f'<line x1="{pad_l}" y1="{pad_t+ch}" x2="{pad_l+cw}" y2="{pad_t+ch}" stroke="#9ca3af" stroke-width="1"/>')
    for i, (label, v) in enumerate(points):
        bh = (v / vmax) * ch
        x = pad_l + gap * i + (gap - bw) / 2
        y = pad_t + ch - bh
        color = PALETTE[i % len(PALETTE)]
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{color}" rx="3"/>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="12" fill="#374151">{_fmt(v)}</text>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{pad_t+ch+18:.1f}" text-anchor="middle" font-size="12" fill="#6b7280">{html.escape(label)}</text>')
    return parts


def _svg_line(points, title):
    pad_l, pad_b, pad_t, pad_r = 50, 50, 40, 20
    cw = SVG_W - pad_l - pad_r
    ch = SVG_H - pad_t - pad_b
    vmax = max((v for _, v in points), default=1) or 1
    n = len(points)
    step = cw / max(n - 1, 1)
    parts = [f'<text x="{SVG_W/2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f2937">{html.escape(title)}</text>']
    parts.append(f'<line x1="{pad_l}" y1="{pad_t+ch}" x2="{pad_l+cw}" y2="{pad_t+ch}" stroke="#9ca3af" stroke-width="1"/>')
    coords = []
    for i, (label, v) in enumerate(points):
        x = pad_l + step * i
        y = pad_t + ch - (v / vmax) * ch
        coords.append((x, y))
        parts.append(f'<text x="{x:.1f}" y="{pad_t+ch+18:.1f}" text-anchor="middle" font-size="12" fill="#6b7280">{html.escape(label)}</text>')
    if coords:
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in coords)
        parts.append(f'<path d="{d}" fill="none" stroke="{PALETTE[0]}" stroke-width="2.5"/>')
        for (x, y), (_, v) in zip(coords, points):
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{PALETTE[0]}"/>')
            parts.append(f'<text x="{x:.1f}" y="{y-8:.1f}" text-anchor="middle" font-size="11" fill="#374151">{_fmt(v)}</text>')
    return parts


def _svg_pie(points, title):
    import math

    cx, cy, r = SVG_W * 0.36, SVG_H * 0.56, 120
    total = sum(v for _, v in points) or 1
    parts = [f'<text x="{SVG_W/2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1f2937">{html.escape(title)}</text>']
    ang = -math.pi / 2
    for i, (label, v) in enumerate(points):
        frac = v / total
        a2 = ang + frac * 2 * math.pi
        x1, y1 = cx + r * math.cos(ang), cy + r * math.sin(ang)
        x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        large = 1 if frac > 0.5 else 0
        color = PALETTE[i % len(PALETTE)]
        parts.append(f'<path d="M {cx:.1f} {cy:.1f} L {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f} Z" fill="{color}"/>')
        # 图例
        ly = 70 + i * 24
        parts.append(f'<rect x="{SVG_W*0.66:.0f}" y="{ly}" width="14" height="14" fill="{color}" rx="2"/>')
        parts.append(f'<text x="{SVG_W*0.66+20:.0f}" y="{ly+12}" font-size="13" fill="#374151">{html.escape(label)} ({frac*100:.0f}%)</text>')
        ang = a2
    return parts


def _fmt(v):
    return str(int(v)) if float(v).is_integer() else f"{v:.1f}"


def render_chart_svg(spec: dict) -> str:
    kind = (spec.get("kind") or "bar").lower()
    if kind == "raw":
        return sanitize_svg(spec.get("svg", ""))

    points = _nums(spec.get("data") or [])
    title = (spec.get("title") or "").strip()
    if not points:
        return ""
    if kind == "line":
        body = _svg_line(points, title)
    elif kind == "pie":
        body = _svg_pie(points, title)
    else:
        body = _svg_bar(points, title)
    inner = "\n".join(body)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" '
        f'width="100%" style="max-width:{SVG_W}px;height:auto;background:#fff;border-radius:8px">\n{inner}\n</svg>'
    )


# ---------------------------------------------------------------- 主入口

def apply_content_tools(md: str) -> str:
    """把章节正文里的 ```tool 块替换为渲染结果（表格 / SVG 图）。"""
    if not md or "```tool" not in md:
        return md

    def repl(m):
        raw = m.group(1).strip()
        try:
            spec = json.loads(raw)
        except json.JSONDecodeError:
            return ""  # 解析失败则丢弃该块，不污染正文
        tool = (spec.get("tool") or "").lower()
        caption = (spec.get("caption") or "").strip()
        if tool == "table":
            return render_table_md(spec)
        if tool == "svg":
            svg = render_chart_svg(spec)
            if not svg:
                return ""
            out = "```svg\n" + svg + "\n```"
            if caption:
                out += f"\n\n*图：{caption}*"
            return out
        return ""

    return TOOL_BLOCK_RE.sub(repl, md)


def content_tools_prompt() -> str:
    """注入章节 system prompt 的工具说明。"""
    return (
        "【可用的内容工具（按需使用，不要滥用）】\n"
        "当内容适合用表格或图表表达时，你可以在正文中插入下面的工具块，系统会自动渲染：\n"
        "1) 表格：\n"
        '```tool\n{"tool": "table", "title": "标题(可选)", "headers": ["列1","列2"], "rows": [["a","b"],["c","d"]]}\n```\n'
        "2) 图表（柱状 bar / 折线 line / 饼图 pie）：\n"
        '```tool\n{"tool": "svg", "kind": "bar", "title": "图标题", "data": [{"label":"甲","value":10},{"label":"乙","value":20}], "caption": "说明(可选)"}\n```\n'
        "规则：工具块必须是合法 JSON；标签/标题用本书语言；只在确实有助于读者理解时使用，纯叙事/抒情段落不要硬插图表。"
    )
