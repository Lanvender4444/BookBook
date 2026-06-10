// 发送系统级通知（右下角弹窗），支持 Tauri 打包版和 Web 版
export async function sendSystemNotification(title, body, onClick = null) {
  const isTauri = typeof window !== 'undefined' && !!(window.__TAURI_INTERNALS__)

  if (isTauri) {
    try {
      const { sendNotification, isPermissionGranted, requestPermission } = await import('@tauri-apps/plugin-notification')
      let permissionGranted = await isPermissionGranted()
      if (!permissionGranted) {
        const permission = await requestPermission()
        permissionGranted = permission === 'granted'
      }
      if (permissionGranted) {
        sendNotification({ title, body })
        // Tauri 通知点击由 Rust 端处理，这里只做记录
        if (onClick) {
          window.__bookbook_notification_click = onClick
        }
      }
    } catch (e) {
      console.error('Tauri notification failed:', e)
    }
  } else {
    // 浏览器 Web Notification API
    if (!('Notification' in window)) {
      console.warn('Browser does not support notifications')
      return
    }
    const send = () => {
      const notification = new Notification(title, {
        body,
        icon: '/icon.png',
        tag: 'bookbook-completion',
      })
      if (onClick) {
        notification.onclick = () => {
          notification.close()
          window.focus()
          onClick()
        }
      }
    }
    if (Notification.permission === 'granted') {
      send()
    } else if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission()
      if (permission === 'granted') {
        send()
      }
    }
  }
}

// 预请求通知权限（可在页面加载时调用）
export async function requestNotificationPermission() {
  const isTauri = typeof window !== 'undefined' && !!(window.__TAURI_INTERNALS__)

  if (isTauri) {
    try {
      const { isPermissionGranted, requestPermission } = await import('@tauri-apps/plugin-notification')
      const granted = await isPermissionGranted()
      if (!granted) {
        await requestPermission()
      }
    } catch (e) {
      console.error('Failed to request Tauri notification permission:', e)
    }
  } else {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission()
    }
  }
}
