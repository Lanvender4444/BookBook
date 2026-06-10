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
    <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-8 pb-8 overflow-y-auto" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 my-auto" onClick={(e) => e.stopPropagation()} ref={modalRef}>
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">{t('settings.title')}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="px-6 py-4">
          {activeModel && (
            <div className="mb-4 px-3 py-2 bg-indigo-50 border border-indigo-200 rounded-lg flex items-center gap-2">
              <svg className="w-4 h-4 text-indigo-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm text-indigo-700">
                {t('settings.currentModel')}: <strong>{activeModel.provider_name}</strong> / {activeModel.model_name}
              </span>
            </div>
          )}

          <div className="mb-3 flex items-center gap-2">
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
            <div className={`mb-3 px-3 py-2 rounded-lg text-xs ${migrateResult.migrated && migrateResult.migrated.length > 0 ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-blue-50 text-blue-700 border border-blue-200'}`}>
              {migrateResult.migrated && migrateResult.migrated.length > 0
                ? t('settings.migrateSuccess').replace('{count}', migrateResult.migrated.length)
                : t('settings.migrateNoKeys')}
            </div>
          )}

          {loading ? (
            <div className="py-8 text-center text-gray-400">{t('settings.loading')}</div>
          ) : (
            <div className="space-y-1 max-h-[60vh] overflow-y-auto">
              {configured.length > 0 && (
                <>
                  <div className="text-xs font-medium text-gray-400 uppercase tracking-wider px-2 py-1.5">{t('settings.configured')}</div>
                  {configured.map((p) => (
                    <ProviderItem key={p.id} provider={p} activeModel={activeModel} onConfigure={handleConfigure} onDelete={setShowDeleteConfirm} onSetActive={handleSetActive} t={t} />
                  ))}
                </>
              )}
              {unconfigured.length > 0 && (
                <>
                  <div className="text-xs font-medium text-gray-400 uppercase tracking-wider px-2 py-1.5 mt-2">{t('settings.availableProviders')}</div>
                  {unconfigured.map((p) => (
                    <ProviderItem key={p.id} provider={p} activeModel={activeModel} onConfigure={handleConfigure} onDelete={setShowDeleteConfirm} onSetActive={handleSetActive} t={t} />
                  ))}
                </>
              )}
              {filtered.length === 0 && (
                <div className="py-8 text-center text-gray-400">{t('settings.noResults')}</div>
              )}
            </div>
          )}
        </div>

        {configuring && (
          <div className="border-t px-6 py-4 bg-gray-50 rounded-b-xl">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">{t('settings.configure')} {configuring.name}</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">API Key *</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={t('settings.apiKeyPlaceholder')}
                  className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
                />
                {configuring.website && (
                  <a href={configuring.website} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-600 hover:underline mt-0.5 inline-block">
                    {t('settings.getApiKey')} →
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
                  className="w-full px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
                />
                <p className="text-xs text-gray-400 mt-0.5">{t('settings.baseUrlHint')}</p>
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
                    className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-indigo-100 focus:border-indigo-500"
                    onKeyDown={(e) => e.key === 'Enter' && addCustomModel()}
                  />
                  <button onClick={addCustomModel} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">{t('settings.add')}</button>
                </div>
              </div>

              {testResult && (
                <div className={`p-2 rounded-lg text-xs ${testResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                  <p className="font-medium">{testResult.success ? t('settings.testSuccess') : t('settings.testFailed')}</p>
                  <p className="mt-0.5">{testResult.message}</p>
                </div>
              )}

              <div className="flex gap-2 pt-1">
                <button onClick={handleTest} disabled={testing} className="px-3 py-1.5 text-xs border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50">
                  {testing ? t('settings.testing') : t('settings.testConnection')}
                </button>
                <button onClick={handleSave} disabled={saving || !apiKey.trim()} className="flex-1 px-3 py-1.5 text-xs bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50">
                  {saving ? t('settings.saving') : t('settings.save')}
                </button>
              </div>
            </div>
          </div>
        )}
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

function ProviderItem({ provider, activeModel, onConfigure, onDelete, onSetActive, t }) {
  const isCurrent = activeModel && activeModel.provider_id === provider.id

  return (
    <div className={`flex items-center justify-between px-3 py-2.5 rounded-lg transition-colors ${isCurrent ? 'bg-indigo-50 border border-indigo-100' : 'hover:bg-gray-50'}`}>
      <div className="flex items-center gap-2.5 min-w-0">
        <div className={`w-2 h-2 rounded-full shrink-0 ${provider.is_configured ? 'bg-green-500' : 'bg-gray-300'}`} />
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="text-sm font-medium text-gray-900 truncate">{provider.name}</span>
            {isCurrent && <span className="px-1.5 py-0.5 text-[10px] bg-indigo-600 text-white rounded font-medium">{t('settings.active')}</span>}
            {provider.is_configured && !isCurrent && <span className="px-1.5 py-0.5 text-[10px] bg-green-100 text-green-700 rounded">{t('settings.configured')}</span>}
          </div>
          {provider.is_configured && provider.masked_api_key && (
            <p className="text-[11px] text-gray-400 truncate">{provider.masked_api_key}</p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-1.5 shrink-0">
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
                {m.length > 18 ? m.slice(0, 16) + '...' : m}
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
        {provider.website && (
          <a
            href={provider.website}
            target="_blank"
            rel="noopener noreferrer"
            className="px-1.5 py-1 text-[10px] text-gray-400 hover:text-indigo-500 transition-colors"
            title={t('settings.getApiKey')}
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
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