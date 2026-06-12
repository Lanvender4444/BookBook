import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Tauri 打包环境下，页面 origin 是 tauri.localhost，相对路径 fetch('/api/...')
// 不会到达后端（开发模式靠 Vite proxy 才正常）。
// 这里全局拦截 fetch，把 /api 开头的请求改写到后端真实地址。
const isTauri = typeof window !== 'undefined' && !!window.__TAURI_INTERNALS__
if (isTauri) {
  const backendPort =
    window.__BOOKBOOK_BACKEND_PORT__ ||
    (typeof __BACKEND_PORT__ !== 'undefined' ? __BACKEND_PORT__ : 18140)
  const backendOrigin = `http://localhost:${backendPort}`
  const origFetch = window.fetch.bind(window)
  window.fetch = (input, init) => {
    try {
      if (typeof input === 'string' && input.startsWith('/api')) {
        input = backendOrigin + input
      } else if (input instanceof URL && input.pathname.startsWith('/api')) {
        input = backendOrigin + input.pathname + input.search
      } else if (input instanceof Request && new URL(input.url).pathname.startsWith('/api')) {
        input = new Request(backendOrigin + new URL(input.url).pathname + new URL(input.url).search, input)
      }
    } catch (e) {
      // 解析失败则按原样请求
    }
    return origFetch(input, init)
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
