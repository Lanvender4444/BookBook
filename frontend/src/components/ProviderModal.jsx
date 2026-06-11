import { useState, useEffect, useRef } from 'react'
import { useI18n } from '../i18n'
import { api } from '../api'
import useStore from '../store'
import ConfirmModal from '../components/ConfirmModal'

export default function ProviderModal({ open, onClose }) {
  const { t } = useI18n()
  const activeModel = useStore((s) => s.activeModel)
  const loadActiveModel = useStore((s) => s.loadActiveModel)
  const setActiveModel = useStore((s) => s.setActiveModel)

  const [providers, setProviders] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [configuring, setConfiguring] = useState(null)
  const [apiKey, setApiKey] = useState('')
  const [baseUrl, setBaseUrl] = useState('')
  const [models, setModels] = useState([])
  const [customModel, setCustomModel] = useState('')
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState(null)
  const [saving, setSaving] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null)
  const [migrating, setMigrating] = useState(false)
  const [migrateResult, setMigrateResult] = useState(null)

  const modalRef = useRef(null)

  useEffect(() => {
    if (open) loadProviders()
  }, [open])

  useEffect(() => {
    if (!open) {
      setConfiguring(null)
      setMigrateResult(null)
      setTestResult(null)
    }
  }, [open])

  const loadProviders = async () => {
    setLoading(true)
    try {
      const data = await api.listProviders()
      setProviders(data.categories?.flatMap(c => c.providers) || [])
    } catch (e) {
      console.error('Failed to load providers:', e)
    } finally {
      setLoading(false)
    }
  }

  const filtered = search
    ? providers.filter(p => p.name.toLowerCase().includes(search.toLowerCase()) || p.id.toLowerCase().includes(search.toLowerCase()))
    : providers

  const configured = filtered.filter(p => p.is_configured)
  const unconfigured = filtered.filter(p => !p.is_configured)

  const handleConfigure = (provider) => {
    setConfiguring(provider)
    setApiKey(provider.is_configured ? '' : '')
    setBaseUrl(provider.default_base_url || '')
    setModels(provider.is_configured ? (provider.models || provider.default_models || []) : (provider.default_models || []))
    setCustomModel('')
    setTestResult(null)
  }

  const handleCloseConfig = () => {
    setConfiguring(null)
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
      await loadProviders()
      if (!activeModel) {
        await api.setActiveModel(configuring.id, finalModels[0] || '')
        await loadActiveModel()
      } else {
        await loadActiveModel()
      }
      setConfiguring(null)
    } catch (e) {
      console.error('Failed to save provider:', e)
    } finally {
      setSaving(false)
    }
  }

  const handleTest = async () => {
    if (!configuring || !configuring.is_configured) {
      if (!apiKey.trim()) return
      setSaving(true)
      try {
        const finalModels = [...models]
        if (customModel.trim() && !finalModels.includes(customModel.trim())) {
          finalModels.push(customModel.trim())
        }
        await api.configureProvider(configuring.id, apiKey, baseUrl || null, finalModels.length > 0 ? finalModels : null)
        await loadProviders()
        if (!activeModel) {
          await api.setActiveModel(configuring.id, finalModels[0] || '')
          await loadActiveModel()
        } else {
          await loadActiveModel()
        }
      } catch (e) {
        console.error('Failed to save before test:', e)
      } finally {
        setSaving(false)
      }
    }

    setTesting(true)
    setTestResult(null)
    try {
      const result = await api.testProvider(configuring.id)
      setTestResult(result)
      if (result.available_models && result.available_models.length > 0) {
        const currentModels = [...models]
        for (const m of result.available_models) {
          if (!currentModels.includes(m)) currentModels.push(m)
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
      await loadProviders()
      await loadActiveModel()
      if (configuring && configuring.id === showDeleteConfirm) {
        setConfiguring(null)
      }
    } catch (e) {
      console.error('Failed to delete provider:', e)
    }
    setShowDeleteConfirm(null)
  }

  const handleSetActive = async (providerId, modelName) => {
    try {
      await api.setActiveModel(providerId, modelName)
      await loadActiveModel()
    } catch (e) {
      console.error('Failed to set active model:', e)
    }
  }

  const handleMigrate = async () => {
    setMigrating(true)
    setMigrateResult(null)
    try {
      const result = await api.migrateEnvKeys()
      await loadProviders()
      await loadActiveModel()
      setMigrateResult(result)
    } catch (e) {
      setMigrateResult({ migrated: [], message: e.message })
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

  if (!open) return null

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-[92vw] sm:max-w-3xl lg:max-w-4xl max-h-[85vh] flex flex-col" onClick={(e) => e.stopPropagation()} ref={modalRef}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b shrink-0">
          <h2 className="text-lg font-semibold text-gray-900">{t('settings.title')}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Active model bar */}
        {activeModel && (
          <div className="mx-6 mt-4 px-3 py-2 bg-indigo-50 border border-indigo-200 rounded-lg flex items-center gap-2">
            <svg className="w-4 h-4 text-indigo-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm text-indigo-700">
              {t('settings.currentModel')}: <strong>{activeModel.provider_name}</strong> / {activeModel.model_name}
            </span>
          </div>
        )}

        {/* Main content: two columns when configuring */}
        <div className={`flex flex-1 min-h-0 ${configuring ? '' : ''}`}>
          {/* Left: provider list always visible */}
          <div className={`flex flex-col ${configuring ? 'w-1/2 border-r' : 'w-full'} min-h-0`}>
            {/* Search + migrate */}
            <div className="px-4 pt-4 pb-2 flex items-center gap-2 shrink-0">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('settings.searchProvider')}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
              />
              <button
                onClick={handleMigrate}
                disabled={migrating}
                className="px-3 py-2 text-xs bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors whitespace-nowrap disabled:opacity-50"
              >
                {migrating ? t('settings.migrating') : t('settings.migrateEnv')}
              </button>
            </div>

            {migrateResult && (
              <div className={`mx-4 mb-2 px-3 py-2 rounded-lg text-xs ${migrateResult.migrated && migrateResult.migrated.length > 0 ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-blue-50 text-blue-700 border border-blue-200'}`}>
                {migrateResult.migrated && migrateResult.migrated.length > 0
                  ? t('settings.migrateSuccess').replace('{count}', migrateResult.migrated.length)
                  : t('settings.migrateNoKeys')}
              </div>
            )}

            {/* Provider list */}
            <div className="flex-1 overflow-y-auto px-4 pb-4">
              {loading ? (
                <div className="py-8 text-center text-gray-400">{t('settings.loading')}</div>
              ) : (
                <div className="space-y-0.5">
                  {configured.length > 0 && (
                    <>
                      <div className="text-xs font-medium text-gray-400 uppercase tracking-wider px-2 py-1.5 sticky top-0 bg-white">{t('settings.configured')}</div>
                      {configured.map((p) => (
                        <ProviderItem key={p.id} provider={p} activeModel={activeModel} onConfigure={handleConfigure} onDelete={setShowDeleteConfirm} onSetActive={handleSetActive} t={t} isSelected={configuring?.id === p.id} />
                      ))}
                    </>
                  )}
                  {unconfigured.length > 0 && (
                    <>
                      <div className="text-xs font-medium text-gray-400 uppercase tracking-wider px-2 py-1.5 mt-1">{t('settings.availableProviders')}</div>
                      {unconfigured.map((p) => (
                        <ProviderItem key={p.id} provider={p} activeModel={activeModel} onConfigure={handleConfigure} onDelete={setShowDeleteConfirm} onSetActive={handleSetActive} t={t} isSelected={configuring?.id === p.id} />
                      ))}
                    </>
                  )}
                  {filtered.length === 0 && (
                    <div className="py-8 text-center text-gray-400">{t('settings.noResults')}</div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Right: configuration panel */}
          {configuring && (
            <div className="w-1/2 flex flex-col min-h-0 overflow-y-auto">
              <div className="px-5 py-4 flex items-center justify-between border-b shrink-0">
                <div className="flex items-center gap-2">
                  <div className={`w-2.5 h-2.5 rounded-full ${configuring.is_configured ? 'bg-green-500' : 'bg-gray-300'}`} />
                  <h3 className="text-sm font-semibold text-gray-900">{configuring.name}</h3>
                  {configuring.is_configured && (
                    <span className="text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded">{t('settings.configured')}</span>
                  )}
                </div>
                <button onClick={handleCloseConfig} className="text-gray-400 hover:text-gray-600 transition-colors">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="px-5 py-4 space-y-4 flex-1 overflow-y-auto">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">API Key *</label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder={t('settings.apiKeyPlaceholder')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
                  />
                  {configuring.website && (
                    <a href={configuring.website} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-600 hover:underline mt-1 inline-block">
                      {t('settings.getApiKey')} → {configuring.name}
                    </a>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Base URL</label>
                  <input
                    type="text"
                    value={baseUrl}
                    onChange={(e) => setBaseUrl(e.target.value)}
                    placeholder={configuring.default_base_url || ''}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
                  />
                  <p className="text-xs text-gray-400 mt-1">{t('settings.baseUrlHint')}</p>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">{t('settings.models')}</label>
                  <div className="flex flex-wrap gap-1 mb-2">
                    {models.map((m, i) => (
                      <span key={m} className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-xs bg-white border border-gray-200 rounded">
                        {m}
                        <button onClick={() => removeModel(i)} className="text-gray-300 hover:text-red-500 transition-colors">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
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
                      className="flex-1 px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-indigo-100 focus:border-indigo-500"
                      onKeyDown={(e) => e.key === 'Enter' && addCustomModel()}
                    />
                    <button onClick={addCustomModel} className="px-3 py-1.5 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">{t('settings.add')}</button>
                  </div>
                </div>

                {testResult && (
                  <div className={`p-3 rounded-lg text-sm ${testResult.success ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
                    <p className="font-medium">{testResult.success ? t('settings.testSuccess') : t('settings.testFailed')}</p>
                    <p className="mt-1">{testResult.message}</p>
                    {testResult.available_models && testResult.available_models.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-medium mb-1">{t('settings.availableModels')}:</p>
                        <div className="flex flex-wrap gap-1">
                          {testResult.available_models.slice(0, 15).map((m) => (
                            <span key={m} className="px-1.5 py-0.5 text-xs bg-white rounded border">{m}</span>
                          ))}
                          {testResult.available_models.length > 15 && <span className="text-xs">+{testResult.available_models.length - 15}</span>}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="flex gap-2 pt-2">
                  <button
                    onClick={handleTest}
                    disabled={testing || (!configuring.is_configured && !apiKey.trim())}
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
          )}
        </div>
      </div>

      {showDeleteConfirm && (
        <ConfirmModal
          isOpen={true}
          title={t('settings.deleteProvider')}
          message={t('settings.deleteConfirm')}
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteConfirm(null)}
          danger
        />
      )}
    </div>
  )
}

function ProviderItem({ provider, activeModel, onConfigure, onDelete, onSetActive, t, isSelected }) {
  const isCurrent = activeModel && activeModel.provider_id === provider.id

  return (
    <div className={`flex items-center justify-between px-3 py-2.5 rounded-lg transition-colors cursor-pointer ${
      isSelected ? 'bg-indigo-50 ring-1 ring-indigo-200' :
      isCurrent ? 'bg-indigo-50/50' : 'hover:bg-gray-50'
    }`}
      onClick={() => onConfigure(provider)}
    >
      <div className="flex items-center gap-2.5 min-w-0">
        <div className={`w-2 h-2 rounded-full shrink-0 ${provider.is_configured ? 'bg-green-500' : 'bg-gray-300'}`} />
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="text-sm font-medium text-gray-900 truncate">{provider.name}</span>
            {isCurrent && <span className="px-1.5 py-0.5 text-[10px] bg-indigo-600 text-white rounded font-medium">{t('settings.active')}</span>}
          </div>
          {provider.is_configured && provider.masked_api_key && (
            <p className="text-[11px] text-gray-400 truncate">{provider.masked_api_key}</p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-1.5 shrink-0" onClick={(e) => e.stopPropagation()}>
        {provider.is_configured && provider.models && provider.models.length > 0 && (
          <div className="flex gap-1">
            {provider.models.slice(0, 3).map((m) => (
              <button
                key={m}
                onClick={() => onSetActive(provider.id, m)}
                className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
                  isCurrent && activeModel.model_name === m
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-indigo-50 hover:text-indigo-600'
                }`}
              >
                {m.length > 16 ? m.slice(0, 14) + '..' : m}
              </button>
            ))}
            {provider.models.length > 3 && (
              <button
                onClick={() => onConfigure(provider)}
                className="px-1.5 py-0.5 text-[10px] bg-gray-100 text-gray-500 rounded hover:bg-gray-200 transition-colors"
              >
                +{provider.models.length - 3}
              </button>
            )}
          </div>
        )}
        <button
          onClick={() => onConfigure(provider)}
          className={`px-2.5 py-1 text-xs rounded transition-colors ${
            provider.is_configured
              ? 'text-gray-600 hover:bg-gray-100'
              : 'bg-indigo-600 text-white hover:bg-indigo-700'
          }`}
        >
          {provider.is_configured ? t('settings.edit') : t('settings.connect')}
        </button>
        {provider.is_configured && (
          <button
            onClick={() => onDelete(provider.id)}
            className="px-1.5 py-1 text-xs text-gray-400 hover:text-red-500 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        )}
      </div>
    </div>
  )
}