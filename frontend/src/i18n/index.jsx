import { createContext, useContext, useState, useCallback, useEffect } from 'react'

const I18nContext = createContext()

export function I18nProvider({ children }) {
  const [locale, setLocale] = useState(() => {
    return localStorage.getItem('locale') || 'zh-CN'
  })
  const [translations, setTranslations] = useState({})
  const [loaded, setLoaded] = useState(false)

  // 异步加载当前语言文件
  useEffect(() => {
    let cancelled = false
    const load = async () => {
      const code = locale
      if (translations[code]) {
        setLoaded(true)
        return
      }
      try {
        const res = await fetch(`/i18n/${code}.json`)
        if (res.ok) {
          const data = await res.json()
          if (!cancelled) {
            setTranslations(prev => ({ ...prev, [code]: data }))
            setLoaded(true)
          }
        } else {
          // 回退：加载中文
          const fallbackRes = await fetch(`/i18n/zh-CN.json`)
          if (fallbackRes.ok) {
            const data = await fallbackRes.json()
            if (!cancelled) {
              setTranslations(prev => ({ ...prev, [code]: data }))
              setLoaded(true)
            }
          }
        }
      } catch (e) {
        console.error('Failed to load translation:', e)
        if (!cancelled) setLoaded(true)
      }
    }
    load()
    return () => { cancelled = true }
  }, [locale])

  const t = useCallback((key, params = {}) => {
    const keys = key.split('.')

    // 优先使用当前语言的翻译
    let value = translations[locale]
    for (const k of keys) {
      value = value?.[k]
    }

    // 如果当前语言没有翻译，回退到中文
    if (typeof value !== 'string') {
      value = translations['zh-CN']
      for (const k of keys) {
        value = value?.[k]
      }
    }

    if (typeof value !== 'string') return key

    return Object.entries(params).reduce(
      (str, [k, v]) => str.replace(new RegExp(`\\{${k}\\}`, 'g'), v),
      value
    )
  }, [locale, translations])

  const changeLocale = useCallback((newLocale) => {
    setLocale(newLocale)
    localStorage.setItem('locale', newLocale)
  }, [])

  // 关键：JSON 加载完成前，不渲染任何子组件
  if (!loaded) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
          <span className="text-sm text-gray-500">Loading translations...</span>
        </div>
      </div>
    )
  }

  return (
    <I18nContext.Provider value={{ locale, t, changeLocale }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useI18n() {
  return useContext(I18nContext)
}
