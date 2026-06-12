// 统一下载入口：Tauri 打包版弹原生“另存为”对话框，浏览器走 <a download>
// 返回 true=已保存, false=用户取消
export async function saveDownload(filename, blob) {
  const isTauri = typeof window !== 'undefined' && !!window.__TAURI_INTERNALS__

  if (isTauri) {
    const { save } = await import('@tauri-apps/plugin-dialog')
    const { writeFile } = await import('@tauri-apps/plugin-fs')
    const ext = (filename.split('.').pop() || 'txt').toLowerCase()
    const path = await save({
      defaultPath: filename,
      filters: [{ name: ext.toUpperCase(), extensions: [ext] }],
    })
    if (!path) return false // 用户点了取消
    const data = new Uint8Array(await blob.arrayBuffer())
    await writeFile(path, data)
    return true
  }

  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
  return true
}
