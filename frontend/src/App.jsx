import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { I18nProvider, useI18n } from './i18n'
import Generate from './pages/Generate'
import Library from './pages/Library'
import Reader from './pages/Reader'
import Network from './pages/Network'
import History from './pages/History'
import useStore from './store'
import { useState, useRef, useEffect } from 'react'

const UI_LANGUAGES = [
  { value: "zh-CN", label: "中文（简体）" },
  { value: "zh-TW", label: "中文（繁體）" },
  { value: "ja", label: "日本語" },
  { value: "ko", label: "한국어" },
  { value: "en", label: "English" },
  { value: "es", label: "español" },
  { value: "fr", label: "français" },
  { value: "de", label: "Deutsch" },
  { value: "it", label: "italiano" },
  { value: "pt-BR", label: "português (Brasil)" },
  { value: "pt-PT", label: "português (Portugal)" },
  { value: "ru", label: "русский" },
  { value: "ar", label: "العربية" },
  { value: "ar-EG", label: "العربية (العامية المصرية)" },
  { value: "hi", label: "हिन्दी" },
  { value: "bn", label: "বাংলা" },
  { value: "pa", label: "ਪੰਜਾਬੀ" },
  { value: "gu", label: "ગુજરાતી" },
  { value: "or", label: "ଓଡ଼ିଆ" },
  { value: "ta", label: "தமிழ்" },
  { value: "te", label: "తెలుగు" },
  { value: "kn", label: "ಕನ್ನಡ" },
  { value: "ml", label: "മലയാളം" },
  { value: "si", label: "සිංහල" },
  { value: "th", label: "ไทย" },
  { value: "vi", label: "Tiếng Việt" },
  { value: "id", label: "Indonesia" },
  { value: "ms", label: "Melayu" },
  { value: "tr", label: "Türkçe" },
  { value: "pl", label: "polski" },
  { value: "nl", label: "Nederlands" },
  { value: "sv", label: "svenska" },
  { value: "da", label: "dansk" },
  { value: "fi", label: "suomi" },
  { value: "nb", label: "norsk bokmål" },
  { value: "nn", label: "norsk nynorsk" },
  { value: "cs", label: "čeština" },
  { value: "sk", label: "slovenčina" },
  { value: "hu", label: "magyar" },
  { value: "ro", label: "română" },
  { value: "bg", label: "български" },
  { value: "uk", label: "українська" },
  { value: "el", label: "Ελληνικά" },
  { value: "he", label: "עברית" },
  { value: "ur", label: "اردو" },
  { value: "fa", label: "فارسی" },
  { value: "am", label: "አማርኛ" },
  { value: "ne", label: "नेपाली" },
  { value: "mr", label: "मराठी" },
  { value: "mai", label: "मैथिली" },
  { value: "kok", label: "कोंकणी" },
  { value: "sr", label: "српски" },
  { value: "mk", label: "македонски" },
  { value: "be", label: "беларуская" },
  { value: "ka", label: "ქართული" },
  { value: "hy", label: "հայերեն" },
  { value: "ps", label: "پښتو" },
  { value: "sd", label: "سنڌي" },
  { value: "af", label: "Afrikaans" },
  { value: "az", label: "azərbaycan" },
  { value: "ca", label: "català" },
  { value: "ceb", label: "Cebuano" },
  { value: "eu", label: "euskara" },
  { value: "fil", label: "Filipino" },
  { value: "gl", label: "galego" },
  { value: "hr", label: "hrvatski" },
  { value: "is", label: "íslenska" },
  { value: "jv", label: "Jawa" },
  { value: "la", label: "Latin" },
  { value: "lv", label: "latviešu" },
  { value: "lt", label: "lietuvių" },
  { value: "sw", label: "Kiswahili" },
  { value: "ht", label: "créole haïtien" },
  { value: "es-419", label: "español (Latinoamérica)" },
  { value: "es-MX", label: "español (México)" },
  { value: "fr-CA", label: "français (Canada)" },
  { value: "my", label: "မြန်မာ" }
]

function LanguageSwitcher() {
  const { locale, changeLocale } = useI18n()
  const [isOpen, setIsOpen] = useState(false)
  const [search, setSearch] = useState('')
  const ref = useRef(null)
  const searchRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setIsOpen(false)
        setSearch('')
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (isOpen && searchRef.current) {
      searchRef.current.focus()
    }
  }, [isOpen])

  const currentLang = UI_LANGUAGES.find(l => l.value === locale)
  const filteredLanguages = UI_LANGUAGES.filter(l =>
    l.label.toLowerCase().includes(search.toLowerCase()) ||
    l.value.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 text-sm text-gray-600 hover:text-indigo-600 hover:bg-gray-100 rounded-md transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
        </svg>
        <span>{currentLang?.label || '中文（简体）'}</span>
        <svg className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-1 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-50 overflow-hidden">
          <div className="p-2 border-b">
            <input
              ref={searchRef}
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索语言..."
              className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div className="max-h-72 overflow-y-auto">
            {filteredLanguages.map((lang) => (
              <button
                key={lang.value}
                onClick={() => { changeLocale(lang.value); setIsOpen(false); setSearch('') }}
                className={`w-full px-3 py-2 text-sm text-left transition-colors
                  ${locale === lang.value 
                    ? 'bg-indigo-50 text-indigo-700' 
                    : 'text-gray-700 hover:bg-gray-50'}`}
              >
                {lang.label}
              </button>
            ))}
            {filteredLanguages.length === 0 && (
              <div className="px-3 py-2 text-sm text-gray-400">无匹配语言</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function NavBar() {
  const { t } = useI18n()
  
  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <img src="/icon.png" alt="Logo" className="h-8 w-8 mr-2" />
            <span className="text-xl font-bold text-indigo-600">AI eBook Generator</span>
          </div>
          <div className="flex items-center space-x-1">
            <a href="/generate" className="px-3 py-2 text-sm text-gray-700 hover:text-indigo-600 hover:bg-gray-100 rounded-md transition-colors">{t('nav.generate')}</a>
            <a href="/history" className="px-3 py-2 text-sm text-gray-700 hover:text-indigo-600 hover:bg-gray-100 rounded-md transition-colors">{t('nav.history')}</a>
            <a href="/library" className="px-3 py-2 text-sm text-gray-700 hover:text-indigo-600 hover:bg-gray-100 rounded-md transition-colors">{t('nav.library')}</a>
            <a href="/network" className="px-3 py-2 text-sm text-gray-700 hover:text-indigo-600 hover:bg-gray-100 rounded-md transition-colors">{t('nav.network')}</a>
            <div className="ml-2 pl-2 border-l border-gray-200">
              <LanguageSwitcher />
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

function App() {
  const loadActiveModel = useStore((s) => s.loadActiveModel)

  useEffect(() => {
    loadActiveModel()
  }, [])

  return (
    <Router>
      <I18nProvider>
        <div className="min-h-screen bg-gray-50">
          <NavBar />
          <Routes>
            <Route path="/" element={<Generate />} />
            <Route path="/generate" element={<Generate />} />
            <Route path="/history" element={<History />} />
            <Route path="/library" element={<Library />} />
            <Route path="/reader/:id" element={<Reader />} />
            <Route path="/network" element={<Network />} />
          </Routes>
        </div>
      </I18nProvider>
    </Router>
  )
}

export default App
