import { useRef, useEffect, useMemo } from 'react'

const BAUHAUS_COLORS = {
  backgrounds: [
    '#F5F0E8', '#E8E0D0', '#F0E6D3', '#E5DDD0', '#F2EDE5',
    '#EAE2D5', '#F0E8DA', '#E8E4D8', '#F5EFE5', '#EDE5D8',
  ],
  accents: [
    '#E63946', '#1D3557', '#F4A261', '#2A9D8F', '#264653',
    '#E76F51', '#606C38', '#DDA15E', '#BC6C25', '#003049',
    '#D62828', '#FCBF49', '#0077B6', '#023E8A', '#48CAE4',
  ],
  darks: ['#1A1A2E', '#16213E', '#0F3460', '#1B1B2F', '#2C2C3E'],
  lights: ['#FFFFFF', '#F8F9FA', '#E9ECEF', '#F0F0F0', '#FAFAFA'],
}

function seededRandom(seed) {
  let s = seed
  return () => {
    s = (s * 16807 + 0) % 2147483647
    return (s - 1) / 2147483646
  }
}

function hashString(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return Math.abs(hash)
}

function wrapText(ctx, text, maxWidth) {
  const chars = Array.from(text)
  const lines = []
  let currentLine = ''

  for (const char of chars) {
    const testLine = currentLine + char
    const metrics = ctx.measureText(testLine)
    if (metrics.width > maxWidth && currentLine.length > 0) {
      lines.push(currentLine)
      currentLine = char
    } else {
      currentLine = testLine
    }
  }
  if (currentLine) lines.push(currentLine)
  return lines
}

function drawBauhausCover(canvas, title, width = 400, height = 560) {
  const ctx = canvas.getContext('2d')
  const seed = hashString(title)
  const rand = seededRandom(seed)

  canvas.width = width
  canvas.height = height

  const pick = (arr) => arr[Math.floor(rand() * arr.length)]
  const randRange = (min, max) => min + rand() * (max - min)

  const bgColor = pick(BAUHAUS_COLORS.backgrounds)
  ctx.fillStyle = bgColor
  ctx.fillRect(0, 0, width, height)

  const accentColor = pick(BAUHAUS_COLORS.accents)
  const darkColor = pick(BAUHAUS_COLORS.darks)
  const lightColor = pick(BAUHAUS_COLORS.lights)

  const numShapes = Math.floor(randRange(3, 7))
  for (let i = 0; i < numShapes; i++) {
    const shapeType = Math.floor(rand() * 4)
    const x = randRange(-40, width + 40)
    const y = randRange(-40, height + 40)
    const size = randRange(30, 160)
    const alpha = randRange(0.15, 0.55)
    const color = pick([accentColor, darkColor, lightColor, pick(BAUHAUS_COLORS.accents)])

    ctx.save()
    ctx.globalAlpha = alpha

    if (shapeType === 0) {
      ctx.fillStyle = color
      ctx.beginPath()
      ctx.arc(x, y, size / 2, 0, Math.PI * 2)
      ctx.fill()
    } else if (shapeType === 1) {
      ctx.fillStyle = color
      ctx.fillRect(x - size / 2, y - size / 2, size, size)
    } else if (shapeType === 2) {
      ctx.fillStyle = color
      ctx.beginPath()
      ctx.moveTo(x, y - size / 2)
      ctx.lineTo(x + size / 2, y + size / 2)
      ctx.lineTo(x - size / 2, y + size / 2)
      ctx.closePath()
      ctx.fill()
    } else {
      ctx.strokeStyle = color
      ctx.lineWidth = randRange(3, 10)
      ctx.beginPath()
      ctx.ellipse(x, y, size / 2, size / 4, rand() * Math.PI, 0, Math.PI * 2)
      ctx.stroke()
    }

    ctx.restore()
  }

  const lineCount = Math.floor(randRange(2, 5))
  for (let i = 0; i < lineCount; i++) {
    ctx.save()
    ctx.globalAlpha = randRange(0.1, 0.3)
    ctx.strokeStyle = pick([accentColor, darkColor])
    ctx.lineWidth = randRange(1, 4)

    if (rand() > 0.5) {
      const y = randRange(0, height)
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(width, y + randRange(-60, 60))
      ctx.stroke()
    } else {
      const x = randRange(0, width)
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x + randRange(-60, 60), height)
      ctx.stroke()
    }
    ctx.restore()
  }

  const titleAreaTop = height * 0.45
  const titleAreaHeight = height * 0.45
  ctx.fillStyle = bgColor
  ctx.globalAlpha = 0.85
  ctx.fillRect(0, titleAreaTop, width, titleAreaHeight)
  ctx.globalAlpha = 1

  ctx.fillStyle = darkColor
  ctx.fillRect(0, titleAreaTop, width, 3)

  const maxFontSize = 48
  let fontSize = maxFontSize
  ctx.font = `bold ${fontSize}px "Helvetica Neue", Helvetica, Arial, sans-serif`
  const textPadding = 40
  const maxTextWidth = width - textPadding * 2

  let lines = wrapText(ctx, title, maxTextWidth)
  while (lines.length > 4 && fontSize > 18) {
    fontSize -= 2
    ctx.font = `bold ${fontSize}px "Helvetica Neue", Helvetica, Arial, sans-serif`
    lines = wrapText(ctx, title, maxTextWidth)
  }

  const lineHeight = fontSize * 1.3
  const totalTextHeight = lines.length * lineHeight
  const startY = titleAreaTop + (titleAreaHeight - totalTextHeight) / 2 + fontSize

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const metrics = ctx.measureText(line)
    const lineWidth = metrics.width

    const x = (width - lineWidth) / 2
    const y = startY + i * lineHeight

    ctx.save()
    ctx.fillStyle = lightColor
    ctx.globalAlpha = 0.4
    const offset = 2
    ctx.fillText(line, x + offset, y + offset)
    ctx.restore()

    ctx.fillStyle = darkColor
    ctx.fillText(line, x, y)
  }

  const barWidth = 80
  const barHeight = 4
  ctx.fillStyle = accentColor
  ctx.fillRect((width - barWidth) / 2, titleAreaTop + titleAreaHeight - 20, barWidth, barHeight)

  ctx.fillStyle = darkColor
  ctx.globalAlpha = 0.3
  const cornerSize = 30
  ctx.fillRect(15, 15, cornerSize, 4)
  ctx.fillRect(15, 15, 4, cornerSize)

  ctx.fillRect(width - 15 - cornerSize, height - 19, cornerSize, 4)
  ctx.fillRect(width - 19, height - 15 - cornerSize, 4, cornerSize)
  ctx.globalAlpha = 1
}

export default function BauhausCover({ title, width = 400, height = 560, className = '' }) {
  const canvasRef = useRef(null)

  const titleKey = useMemo(() => title || 'Untitled', [title])

  useEffect(() => {
    if (canvasRef.current) {
      drawBauhausCover(canvasRef.current, titleKey, width, height)
    }
  }, [titleKey, width, height])

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
    />
  )
}

export { drawBauhausCover }
