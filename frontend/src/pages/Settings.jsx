import { useState, useEffect } from 'react'
import { useI18n } from '../i18n'
import { api } from '../api'
import ConfirmModal from '../components/ConfirmModal'

function Settings() {
  const { t, locale } = useI18n()
  const [categories, setCategories] = useState([])
  const [activeModel, setActiveModel] = useState(null)
  const [loading, setLoading] = useState(true)
  const [configuring, setConfiguring] = useState(null)
  const [apiKey, setApiKey] = useState('')
  const [baseUrl, setBaseUrl] = useState('')
  const [models, setModels] = useState([])
  const [customModel, setCustomModel] = useState('')
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState(null)
  const [saving, setSaving] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedCategory, setExpandedCategory] = useState(null)
  const [migrating, setMigrating] = useState(false)
  const [migrateResult, setMigrateResult] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [providersData, activeData] = await Promise.all([
        api.listProviders(),
        api.getActiveModel()
      ])
      setCategories(providersData.categories || [])
      setActiveModel(activeData.active)

      const configuredCats = []
      for (const cat of providersData.categories) {
        const hasConfigured = cat.providers.some(p => p.is_configured)
        if (hasConfigured) {
          configuredCats.push(cat.id)
        }
      }
      if (configuredCats.length > 0) {
        setExpandedCategory(configuredCats[0])
      }
    } catch (e) {
      console.error('Failed to load providers:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleConfigure = (provider) => {
    setConfiguring(provider)
    setApiKey('')
    setBaseUrl(provider.default_base_url || '')
    setModels(provider.default_models || [])
    setCustomModel('')
    setTestResult(null)
  }

  const handleSave = async () => {
    if (!apiKey.trim()) return
    setSaving(true)
    try {
      const finalModels = [...models]
      if (customModel.trim() && !finalModels.includes(customModel.trim())) {
        finalModels.push(customModel.trim())
      }
      await api.configureProvider(configuring.id, apiKey, baseUrl || null, finalModels.length > 0 ? finalModels : null)
      await loadData()
      if (!activeModel) {
        await api.setActiveModel(configuring.id, finalModels[0] || '')
        const activeData = await api.getActiveModel()
        setActiveModel(activeData.active)
      }
      setConfiguring(null)
    } catch (e) {
      console.error('Failed to save provider:', e)
    } finally {
      setSaving(false)
    }
  }

  const handleTest = async () => {
    if (!configuring) return
    setTesting(true)
    setTestResult(null)
    try {
      const result = await api.testProvider(configuring.id)
      setTestResult(result)
      if (result.available_models && result.available_models.length > 0) {
        const currentModels = [...models]
        for (const m of result.available_models) {
          if (!currentModels.includes(m)) {
            currentModels.push(m)
          }
        }
        setModels(currentModels)
      }
    } catch (e) {
      setTestResult({ success: false, message: e.message })
    } finally {
      setTesting(false)
    }
  }

  const handleDelete = async () => {
    if (!showDeleteConfirm) return
    try {
      await api.deleteProvider(showDeleteConfirm)
      await loadData()
      if (activeModel && activeModel.provider_id === showDeleteConfirm) {
        const activeData = await api.getActiveModel()
        setActiveModel(activeData.active)
      }
    } catch (e) {
      console.error('Failed to delete provider:', e)
    }
    setShowDeleteConfirm(null)
  }

  const handleSetActive = async (providerId, modelName) => {
    try {
      await api.setActiveModel(providerId, modelName)
      const activeData = await api.getActiveModel()
      setActiveModel(activeData.active)
    } catch (e) {
      console.error('Failed to set active model:', e)
    }
  }

  const handleMigrate = async () => {
    setMigrating(true)
    setMigrateResult(null)
    try {
      const result = await api.migrateEnvKeys()
      setMigrateResult(result)
      await loadData()
    } catch (e) {
      setMigrateResult({ message: e.message, migrated: [] })
    } finally {
      setMigrating(false)
    }
  }

  const removeModel = (index) => {
    setModels(models.filter((_, i) => i !== index))
  }

  const addCustomModel = () => {
    if (customModel.trim() && !models.includes(customModel.trim())) {
      setModels([...models, customModel.trim()])
      setCustomModel('')
    }
  }

  const filterProviders = (providers) => {
    if (!searchQuery) return providers
    const q = searchQuery.toLowerCase()
    return providers.filter(p =>
      p.name.toLowerCase().includes(q) || p.id.toLowerCase().includes(q)
    )
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center text-gray-500">{t('settings.loading')}</div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t('settings.title')}</h1>
        <button
          onClick={handleMigrate}
          disabled={migrating}
          className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          {migrating ? t('settings.migrating') : t('settings.migrateEnv')}
        </button>
      </div>

      {migrateResult && (
        <div className={`mb-4 p-3 rounded-lg text-sm ${migrateResult.migrated && migrateResult.migrated.length > 0 ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'}`}>
          {migrateResult.migrated && migrateResult.migrated.length > 0
            ? t('settings.migrateSuccess').replace('{count}', migrateResult.migrated.length)
            : t('settings.migrateNoKeys')}
        </div>
      )}

      {activeModel && (
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-indigo-700 font-medium">
              {t('settings.currentModel')}: <strong>{activeModel.provider_name}</strong> / {activeModel.model_name}
            </span>
          </div>
        </div>
      )}

      <div className="mb-4">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={t('settings.searchProvider')}
          className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
        />
      </div>

      {categories.map((category) => {
        const filtered = filterProviders(category.providers)
        if (filtered.length === 0) return null

        const isExpanded = expandedCategory === category.id
        const hasConfigured = category.providers.some(p => p.is_configured)

        return (
          <div key={category.id} className="mb-4">
            <button
              onClick={() => setExpandedCategory(isExpanded ? null : category.id)}
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-700">{category.name}</span>
                {hasConfigured && (
                  <span className="px-1.5 py-0.5 text-xs bg-green-100 text-green-700 rounded">
                    {t('settings.configured')}
                  </span>
                )}
              </div>
              <svg className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {isExpanded && (
              <div className="mt-2 space-y-2">
                {filtered.map((provider) => (
                  <div
                    key={provider.id}
                    className={`border rounded-lg p-4 transition-colors ${
                      provider.is_configured ? 'bg-white border-green-200' : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-2.5 h-2.5 rounded-full ${provider.is_configured ? 'bg-green-500' : 'bg-gray-300'}`} />
                        <div>
                          <h3 className="font-medium text-gray-900">{provider.name}</h3>
                          <p className="text-xs text-gray-500 mt-0.5">
                            {provider.api_type === 'anthropic' ? 'Anthropic API' :
                             provider.api_type === 'gemini' ? 'Google AI API' :
                             provider.api_type === 'openai_compatible' ? 'OpenAI-compatible API' :
                             provider.api_type}
                            {provider.is_configured && provider.masked_api_key && (
                              <span className="ml-2 text-gray-400">({provider.masked_api_key})</span>
                            )}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {provider.is_configured && activeModel && activeModel.provider_id === provider.id && (
                          <span className="px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded-md font-medium">
                            {t('settings.active')}
                          </span>
                        )}
                        {provider.website && (
                          <a
                            href={provider.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-2 py-1 text-xs text-gray-500 hover:text-indigo-600 transition-colors"
                          >
                            {t('settings.getApiKey')} →
                          </a>
                        )}
                        <button
                          onClick={() => handleConfigure(provider)}
                          className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                        >
                          {provider.is_configured ? t('settings.edit') : t('settings.connect')}
                        </button>
                        {provider.is_configured && (
                          <button
                            onClick={() => setShowDeleteConfirm(provider.id)}
                            className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md transition-colors"
                          >
                            {t('settings.remove')}
                          </button>
                        )}
                      </div>
                    </div>

                    {provider.is_configured && provider.models && provider.models.length > 0 && (
                      <div className="mt-3 ml-5.5">
                        <div className="flex flex-wrap gap-1.5">
                          {provider.models.map((m) => (
                            <button
                              key={m}
                              onClick={() => handleSetActive(provider.id, m)}
                              className={`px-2 py-1 text-xs rounded-md transition-colors ${
                                activeModel && activeModel.provider_id === provider.id && activeModel.model_name === m
                                  ? 'bg-indigo-600 text-white'
                                  : 'bg-gray-100 text-gray-600 hover:bg-indigo-50 hover:text-indigo-600'
                              }`}
                            >
                              {m}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )
      })}

      {configuring && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setConfiguring(null)}>
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                {t('settings.configure')} {configuring.name}
              </h2>
              <button onClick={() => setConfiguring(null)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Key <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={t('settings.apiKeyPlaceholder')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
                />
                {configuring.website && (
                  <a
                    href={configuring.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block mt-1 text-xs text-indigo-600 hover:underline"
                  >
                    {t('settings.getApiKey')} → {configuring.name}
                  </a>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Base URL
                </label>
                <input
                  type="text"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  placeholder={configuring.default_base_url || 'https://api.example.com/v1'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
                />
                <p className="text-xs text-gray-400 mt-1">{t('settings.baseUrlHint')}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('settings.models')}
                </label>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {models.map((m, i) => (
                    <span key={m} className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-md">
                      {m}
                      <button onClick={() => removeModel(i)} className="text-gray-400 hover:text-red-500">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={customModel}
                    onChange={(e) => setCustomModel(e.target.value)}
                    placeholder={t('settings.addModelPlaceholder')}
                    className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
                    onKeyDown={(e) => e.key === 'Enter' && addCustomModel()}
                  />
                  <button
                    onClick={addCustomModel}
                    className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    {t('settings.add')}
                  </button>
                </div>
              </div>

              {testResult && (
                <div className={`p-3 rounded-lg text-sm ${testResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                  <p className="font-medium">{testResult.success ? t('settings.testSuccess') : t('settings.testFailed')}</p>
                  <p className="mt-1">{testResult.message}</p>
                  {testResult.available_models && testResult.available_models.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs font-medium">{t('settings.availableModels')}:</p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {testResult.available_models.slice(0, 20).map((m) => (
                          <span key={m} className="px-1.5 py-0.5 text-xs bg-white rounded border">{m}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div className="flex gap-2 pt-2">
                <button
                  onClick={handleTest}
                  disabled={testing || !apiKey.trim()}
                  className="px-4 py-2 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  {testing ? t('settings.testing') : t('settings.testConnection')}
                </button>
                <button
                  onClick={handleSave}
                  disabled={saving || !apiKey.trim()}
                  className="flex-1 px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                  {saving ? t('settings.saving') : t('settings.save')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <ConfirmModal
          isOpen={true}
          title={t('settings.deleteProvider')}
          message={t('settings.deleteConfirm')}
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteConfirm(null)}
        />
      )}
    </div>
  )
}

export default Settings