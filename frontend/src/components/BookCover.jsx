// 算法生成书籍封面：图案 + 艺术字书名拼贴
// 以书名（+id）为种子做确定性随机，同一本书的封面永远一致。

function hashStr(s) {
  let h = 2166136261
  for (let i = 0; i < (s || '').length; i++) {
    h ^= s.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return h >>> 0
}

// mulberry32 种子随机
function rng(seed) {
  let a = seed >>> 0
  return () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const PALETTES = [
  { bg: ['#1e1b4b', '#312e81'], accents: ['#a5b4fc', '#f472b6', '#facc15'], text: '#ffffff' },
  { bg: ['#7f1d1d', '#991b1b'], accents: ['#fca5a5', '#fde047', '#fdba74'], text: '#fff7ed' },
  { bg: ['#064e3b', '#065f46'], accents: ['#6ee7b7', '#fde68a', '#a7f3d0'], text: '#ecfdf5' },
  { bg: ['#0c4a6e', '#075985'], accents: ['#7dd3fc', '#fbbf24', '#f0abfc'], text: '#f0f9ff' },
  { bg: ['#581c87', '#6b21a8'], accents: ['#e9d5ff', '#fb7185', '#fcd34d'], text: '#faf5ff' },
  { bg: ['#27272a', '#18181b'], accents: ['#f59e0b', '#ef4444', '#e4e4e7'], text: '#fafafa' },
  { bg: ['#fef3c7', '#fde68a'], accents: ['#b45309', '#1c1917', '#dc2626'], text: '#451a03' },
  { bg: ['#ecfeff', '#cffafe'], accents: ['#0e7490', '#1e293b', '#e11d48'], text: '#164e63' },
  { bg: ['#831843', '#9d174d'], accents: ['#f9a8d4', '#fde047', '#c7d2fe'], text: '#fdf2f8' },
  { bg: ['#14532d', '#166534'], accents: ['#bbf7d0', '#fb923c', '#fef08a'], text: '#f0fdf4' },
]

const FONTS = [
  'Georgia, serif',
  '"Trebuchet MS", sans-serif',
  '"Courier New", monospace',
  '"Microsoft YaHei", "PingFang SC", sans-serif',
  '"SimSun", "Songti SC", serif',
]

// ---------------- 图案算法 ----------------

function patternCircles(r, p, W, H) {
  const els = []
  const n = 4 + Math.floor(r() * 5)
  for (let i = 0; i < n; i++) {
    const cx = r() * W, cy = r() * H * 0.7
    const rad = 18 + r() * 70
    const color = p.accents[Math.floor(r() * p.accents.length)]
    els.push(
      r() > 0.4
        ? <circle key={`c${i}`} cx={cx} cy={cy} r={rad} fill={color} opacity={0.16 + r() * 0.22} />
        : <circle key={`c${i}`} cx={cx} cy={cy} r={rad} fill="none" stroke={color} strokeWidth={2 + r() * 4} opacity={0.3 + r() * 0.3} />
    )
  }
  return els
}

function patternStripes(r, p, W, H) {
  const els = []
  const n = 5 + Math.floor(r() * 6)
  const angle = -30 + r() * 60
  for (let i = 0; i < n; i++) {
    const y = (H / n) * i + r() * 18
    const color = p.accents[Math.floor(r() * p.accents.length)]
    els.push(
      <rect key={`s${i}`} x={-60} y={y} width={W + 120} height={4 + r() * 16}
        fill={color} opacity={0.14 + r() * 0.22}
        transform={`rotate(${angle} ${W / 2} ${H / 2})`} />
    )
  }
  return els
}

function patternTriangles(r, p, W, H) {
  const els = []
  const n = 5 + Math.floor(r() * 6)
  for (let i = 0; i < n; i++) {
    const x = r() * W, y = r() * H * 0.75, s = 24 + r() * 64
    const rot = r() * 360
    const color = p.accents[Math.floor(r() * p.accents.length)]
    els.push(
      <polygon key={`t${i}`}
        points={`${x},${y - s / 2} ${x - s / 2},${y + s / 2} ${x + s / 2},${y + s / 2}`}
        fill={color} opacity={0.15 + r() * 0.25}
        transform={`rotate(${rot} ${x} ${y})`} />
    )
  }
  return els
}

function patternGrid(r, p, W, H) {
  const els = []
  const cell = 36 + Math.floor(r() * 26)
  for (let x = cell / 2; x < W; x += cell) {
    for (let y = cell / 2; y < H * 0.72; y += cell) {
      if (r() > 0.55) continue
      const color = p.accents[Math.floor(r() * p.accents.length)]
      const kind = r()
      if (kind < 0.33) els.push(<circle key={`g${x}-${y}`} cx={x} cy={y} r={cell * 0.22} fill={color} opacity={0.4} />)
      else if (kind < 0.66) els.push(<rect key={`g${x}-${y}`} x={x - cell * 0.2} y={y - cell * 0.2} width={cell * 0.4} height={cell * 0.4} fill={color} opacity={0.35} transform={`rotate(45 ${x} ${y})`} />)
      else els.push(<line key={`g${x}-${y}`} x1={x - cell * 0.25} y1={y + cell * 0.25} x2={x + cell * 0.25} y2={y - cell * 0.25} stroke={color} strokeWidth={3} opacity={0.45} />)
    }
  }
  return els
}

function patternWaves(r, p, W, H) {
  const els = []
  const n = 4 + Math.floor(r() * 4)
  for (let i = 0; i < n; i++) {
    const baseY = (H * 0.8 / n) * i + 20
    const amp = 10 + r() * 26
    const color = p.accents[Math.floor(r() * p.accents.length)]
    let d = `M -10 ${baseY}`
    for (let x = 0; x <= W + 20; x += 30) {
      d += ` Q ${x + 15} ${baseY + (x / 30 % 2 === 0 ? -amp : amp)} ${x + 30} ${baseY}`
    }
    els.push(<path key={`w${i}`} d={d} fill="none" stroke={color} strokeWidth={2 + r() * 3.5} opacity={0.3 + r() * 0.3} />)
  }
  return els
}

function patternRays(r, p, W, H) {
  const els = []
  const cx = r() * W, cy = r() * H * 0.35
  const n = 9 + Math.floor(r() * 10)
  for (let i = 0; i < n; i++) {
    const ang = (Math.PI * 2 * i) / n + r() * 0.2
    const len = 80 + r() * 200
    const color = p.accents[Math.floor(r() * p.accents.length)]
    els.push(
      <line key={`r${i}`} x1={cx} y1={cy}
        x2={cx + Math.cos(ang) * len} y2={cy + Math.sin(ang) * len}
        stroke={color} strokeWidth={1.5 + r() * 3} opacity={0.25 + r() * 0.3} />
    )
  }
  els.push(<circle key="rc" cx={cx} cy={cy} r={10 + r() * 22} fill={p.accents[0]} opacity={0.5} />)
  return els
}

const PATTERNS = [patternCircles, patternStripes, patternTriangles, patternGrid, patternWaves, patternRays]

// ---------------- 书名艺术字拼贴 ----------------

function titleCollage(title, r, p, W, H) {
  const els = []
  const t = (title || '无题').slice(0, 16)
  // CJK 逐字拼贴；拉丁文按词
  const isCJK = /[一-鿿぀-ヿ가-힯]/.test(t)
  const units = isCJK ? [...t] : t.split(/\s+/).filter(Boolean)
  const maxUnits = isCJK ? 10 : 5
  const shown = units.slice(0, maxUnits)

  const bandTop = H * 0.46
  const bandH = H * 0.4
  const perRow = isCJK ? Math.min(shown.length, shown.length > 4 ? 4 : shown.length) : 1
  const rows = Math.ceil(shown.length / perRow)

  shown.forEach((u, i) => {
    const row = Math.floor(i / perRow)
    const col = i % perRow
    const cellW = W / perRow
    const cx = cellW * col + cellW / 2 + (r() - 0.5) * 10
    const cy = bandTop + (bandH / rows) * row + (bandH / rows) / 2 + (r() - 0.5) * 8
    const base = isCJK ? Math.min(cellW * 0.62, bandH / rows * 0.7) : Math.min((W * 0.86) / Math.max(u.length * 0.6, 1), 40)
    const size = base * (0.8 + r() * 0.45)
    const rot = (r() - 0.5) * 16
    const font = FONTS[Math.floor(r() * FONTS.length)]
    const useAccent = r() > 0.62
    const fill = useAccent ? p.accents[Math.floor(r() * p.accents.length)] : p.text
    const outlined = r() > 0.8

    els.push(
      <text key={`tt${i}`} x={cx} y={cy}
        fontSize={size} fontFamily={font} fontWeight={r() > 0.5 ? 'bold' : 'normal'}
        fill={outlined ? 'none' : fill}
        stroke={outlined ? fill : 'none'} strokeWidth={outlined ? 1.4 : 0}
        textAnchor="middle" dominantBaseline="central"
        transform={`rotate(${rot} ${cx} ${cy})`}
        style={{ paintOrder: 'stroke' }}
      >
        {u}
      </text>
    )
  })

  // 标题被截断时加省略号
  if (units.length > maxUnits) {
    els.push(
      <text key="ell" x={W / 2} y={bandTop + bandH + 8} fontSize={13} fill={p.text} opacity={0.7} textAnchor="middle">…</text>
    )
  }
  return els
}

function BookCover({ book, className = '', rounded = 'rounded-t-lg' }) {
  const W = 300, H = 400
  const seed = hashStr(`${book?.title || ''}::${book?.id || ''}`)
  const r = rng(seed)
  const p = PALETTES[seed % PALETTES.length]
  const pattern = PATTERNS[Math.floor(r() * PATTERNS.length)]

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="xMidYMid slice"
      className={`block w-full h-full ${rounded} ${className}`}
      role="img"
      aria-label={book?.title || ''}
    >
      <defs>
        <linearGradient id={`bg-${seed}`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor={p.bg[0]} />
          <stop offset="100%" stopColor={p.bg[1]} />
        </linearGradient>
      </defs>
      <rect width={W} height={H} fill={`url(#bg-${seed})`} />
      {pattern(r, p, W, H)}
      {/* 标题区轻微压暗，保证文字可读 */}
      <rect x={0} y={H * 0.42} width={W} height={H * 0.48} fill={p.bg[0]} opacity={0.35} />
      {titleCollage(book?.title, r, p, W, H)}
      {/* 书脊侧光 */}
      <rect x={0} y={0} width={10} height={H} fill="#000" opacity={0.18} />
      <rect x={10} y={0} width={3} height={H} fill="#fff" opacity={0.12} />
    </svg>
  )
}

export default BookCover
