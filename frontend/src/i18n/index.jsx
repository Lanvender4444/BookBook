import { createContext, useContext, useState, useCallback } from 'react'

// 动态导入所有翻译文件
const translations = {}
const modules = import.meta.glob('./*.json', { eager: true })
for (const path in modules) {
  const code = path.replace(/^\.\//, '').replace(/\.json$/, '')
  translations[code] = modules[path].default || modules[path]
}

const I18nContext = createContext()

export function I18nProvider({ children }) {
  const [locale, setLocale] = useState(() => {
    return localStorage.getItem('locale') || 'zh-CN'
  })

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
  }, [locale])

  const changeLocale = useCallback((newLocale) => {
    setLocale(newLocale)
    localStorage.setItem('locale', newLocale)
  }, [])

  return (
    <I18nContext.Provider value={{ locale, t, changeLocale }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useI18n() {
  return useContext(I18nContext)
}