import { useState, useEffect, useRef, useCallback } from 'react'
import { useI18n } from '../i18n'
import { api } from '../api'
import ConfirmModal from '../components/ConfirmModal'

const CATEGORIES = ['writing_guide', 'style', 'reference', 'continuation']

// 标签解析：以 # 为标记（如 "#小说 #悬疑"）；无 # 时兼容逗号分隔
function parseTags(input) {
  if (!input) return []
  const clean = (s) => s.trim().replace(/[,，、;；\s]+$/g, '').trim()
  if (input.includes('#')) {
    return input.split('#').map(clean).filter(Boolean)
  }
  return input.split(/[,，、;；]/).map(clean).filter(Boolean)
}

const FALLBACK = {
  'cards.title': '写作卡',
  'cards.subtitle': '组合「写作指导 + 风格库 + 资料库 + 续写 + 额外需求」，在生成时一键套用',
  'cards.tabCards': '写作卡',
  'cards.tabSources': '知识库',
  'cards.newCard': '新建写作卡',
  'cards.editCard': '编辑写作卡',
  'cards.cardName': '名称',
  'cards.extraReq': '额外需求',
  'cards.extraReqPh': '例如：每章末尾附一个思考题…',
  'cards.builtin': '内置',
  'cards.edit': '编辑',
  'cards.duplicate': '复制',
  'cards.delete': '删除',
  'cards.save': '保存',
  'cards.cancel': '取消',
  'cards.empty': '还没有写作卡，点击右上角新建',
  'cards.deleteConfirm': '确定删除吗？此操作不可恢复。',
  'cards.cat.writing_guide': '写作指导',
  'cards.cat.style': '风格库',
  'cards.cat.reference': '资料库',
  'cards.cat.continuation': '续写',
  'cards.catHint.continuation': '将根据所选文章生成其后续内容',
  'cards.addSource': '投递文档',
  'cards.uploadFile': '上传文件',
  'cards.linkFile': '链接本地文件',
  'cards.pasteText': '粘贴文本',
  'cards.sourceName': '名称',
  'cards.sourcePrompt': '配套 Prompt（可选）',
  'cards.sourcePromptPh': '告诉 AI 如何使用这份文档，例如：严格模仿其叙事节奏',
  'cards.filePath': '文件完整路径',
  'cards.filePathPh': '例如 D:\\docs\\style.md（引用原文件，不复制）',
  'cards.textContent': '文本内容',
  'cards.submit': '提交',
  'cards.reindex': '重建索引',
  'cards.noSources': '该分类下还没有知识源',
  'cards.status.pending': '待索引',
  'cards.status.indexing': '索引中…',
  'cards.status.ready': '已索引(向量)',
  'cards.status.bm25': '已索引(关键词)',
  'cards.status.failed': '索引失败',
  'cards.chunks': '段',
  'cards.formats': '支持 txt / md / pdf / docx / epub',
  'cards.selectHint': '勾选要加入该分类的知识源',
  'cards.tags': '标签',
  'cards.tagsPh': '用 # 标记，如：#小说 #悬疑',
  'cards.allTags': '全部',
  'cards.close': '关闭',
  'cards.viewCard': '写作卡详情',
  'cards.emptyPart': '（无）',
}

function useT() {
  const { t } = useI18n()
  return useCallback(
    (key) => {
      const v = t(key)
      return v === key ? (FALLBACK[key] ?? key) : v
    },
    [t]
  )
}

const STATUS_COLORS = {
  pending: 'bg-gray-100 text-gray-600',
  indexing: 'bg-blue-100 text-blue-700',
  ready: 'bg-green-100 text-green-700',
  bm25: 'bg-emerald-100 text-emerald-700',
  failed: 'bg-red-100 text-red-700',
}

// ---------------- 知识源管理 ----------------

function SourcePanel({ sources, reload }) {
  const tt = useT()
  const [category, setCategory] = useState('writing_guide')
  const [mode, setMode] = useState(null) // upload | link | text
  const [form, setForm] = useState({ name: '', prompt: '', path: '', content: '' })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [confirmDelete, setConfirmDelete] = useState(null)
  const fileRef = useRef(null)

  const filtered = sources.filter((s) => s.category === category)

  const resetForm = () => {
    setForm({ name: '', prompt: '', path: '', content: '' })
    setMode(null)
    setError('')
  }

  const submit = async () => {
    setBusy(true)
    setError('')
    try {
      if (mode === 'upload') {
        const file = fileRef.current?.files?.[0]
        if (!file) throw new Error(tt('cards.uploadFile'))
        await api.uploadSource(file, category, { name: form.name, prompt: form.prompt })
      } else if (mode === 'link') {
        await api.linkSource(form.path, category, { name: form.name, prompt: form.prompt })
      } else if (mode === 'text') {
        await api.createTextSource(form.name || 'untitled', category, form.content, { prompt: form.prompt })
      }
      resetForm()
      await reload()
    } catch (e) {
      setError(String(e.message || e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="flex gap-2 mb-4 flex-wrap">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => { setCategory(c); resetForm() }}
            className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
              category === c ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tt(`cards.cat.${c}`)}
          </button>
        ))}
      </div>

      {category === 'continuation' && (
        <p className="text-xs text-amber-600 mb-3">{tt('cards.catHint.continuation')}</p>
      )}

      <div className="flex gap-2 mb-4">
        {['upload', 'link', 'text'].map((m) => (
          <button
            key={m}
            onClick={() => setMode(mode === m ? null : m)}
            className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${
              mode === m ? 'border-indigo-500 text-indigo-600 bg-indigo-50' : 'border-gray-200 text-gray-600 hover:border-gray-300'
            }`}
          >
            {tt(m === 'upload' ? 'cards.uploadFile' : m === 'link' ? 'cards.linkFile' : 'cards.pasteText')}
          </button>
        ))}
        <span className="text-xs text-gray-400 self-center ml-2">{tt('cards.formats')}</span>
      </div>

      {mode && (
        <div className="border border-gray-200 rounded-lg p-4 mb-4 space-y-3 bg-gray-50">
          {mode === 'upload' && (
            <input ref={fileRef} type="file" accept=".txt,.md,.markdown,.pdf,.docx,.epub" className="text-sm" />
          )}
          {mode === 'link' && (
            <input
              type="text"
              value={form.path}
              onChange={(e) => setForm({ ...form, path: e.target.value })}
              placeholder={tt('cards.filePathPh')}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md"
            />
          )}
          {mode === 'text' && (
            <textarea
              value={form.content}
              onChange={(e) => setForm({ ...form, content: e.target.value })}
              placeholder={tt('cards.textContent')}
              className="w-full h-28 px-3 py-2 text-sm border border-gray-300 rounded-md"
            />
          )}
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder={tt('cards.sourceName')}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md"
          />
          <input
            type="text"
            value={form.prompt}
            onChange={(e) => setForm({ ...form, prompt: e.target.value })}
            placeholder={tt('cards.sourcePromptPh')}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md"
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2">
            <button
              onClick={submit}
              disabled={busy}
              className="px-4 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400"
            >
              {tt('cards.submit')}
            </button>
            <button onClick={resetForm} className="px-4 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-md">
              {tt('cards.cancel')}
            </button>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {filtered.length === 0 && <p className="text-sm text-gray-400 py-6 text-center">{tt('cards.noSources')}</p>}
        {filtered.map((s) => (
          <div key={s.id} className="flex items-center gap-3 border border-gray-200 rounded-lg px-4 py-3 bg-white">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm text-gray-800 truncate">{s.name}</span>
                {s.builtin && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-100 text-purple-700">{tt('cards.builtin')}</span>
                )}
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${STATUS_COLORS[s.index_status] || ''}`}>
                  {tt(`cards.status.${s.index_status}`)}
                  {s.chunk_count > 0 && ` · ${s.chunk_count}${tt('cards.chunks')}`}
                </span>
                {s.link_mode === 'link' && <span className="text-[10px] text-gray-400">🔗</span>}
              </div>
              {s.prompt && <p className="text-xs text-gray-400 truncate mt-0.5">{s.prompt}</p>}
              {s.index_status === 'failed' && s.index_error && (
                <p className="text-xs text-red-500 truncate mt-0.5">{s.index_error}</p>
              )}
            </div>
            <button
              onClick={async () => { await api.reindexSource(s.id); reload() }}
              className="text-xs text-indigo-600 hover:underline shrink-0"
            >
              {tt('cards.reindex')}
            </button>
            {!s.builtin && (
              <button onClick={() => setConfirmDelete(s)} className="text-xs text-red-500 hover:underline shrink-0">
                {tt('cards.delete')}
              </button>
            )}
          </div>
        ))}
      </div>

      <ConfirmModal
        isOpen={!!confirmDelete}
        danger
        title={tt('cards.delete')}
        message={tt('cards.deleteConfirm')}
        onConfirm={async () => {
          try { await api.deleteSource(confirmDelete.id) } catch (e) {}
          setConfirmDelete(null)
          reload()
        }}
        onCancel={() => setConfirmDelete(null)}
      />
    </div>
  )
}

// ---------------- 写作卡编辑 ----------------

const CARD_FIELDS = [
  ['writing_guide', 'writing_guide_ids'],
  ['style', 'style_ids'],
  ['reference', 'reference_ids'],
  ['continuation', 'continuation_ids'],
]

function Modal({ open, onClose, children }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-2xl w-[640px] max-w-[92vw] max-h-[82vh] overflow-y-auto p-6">
        {children}
      </div>
    </div>
  )
}

function CardEditor({ card, sources, onSave, onCancel }) {
  const tt = useT()
  const [draft, setDraft] = useState({
    name: card?.name || '',
    writing_guide_ids: card?.writing_guide_ids || [],
    style_ids: card?.style_ids || [],
    reference_ids: card?.reference_ids || [],
    continuation_ids: card?.continuation_ids || [],
    extra_requirements: card?.extra_requirements || '',
    tags: card?.tags || [],
  })
  const [tagsInput, setTagsInput] = useState((card?.tags || []).map((t) => `#${t}`).join(' '))
  const [error, setError] = useState('')

  const toggle = (field, id) => {
    setDraft((d) => ({
      ...d,
      [field]: d[field].includes(id) ? d[field].filter((x) => x !== id) : [...d[field], id],
    }))
  }

  return (
    <div className="space-y-4">
      <input
        type="text"
        value={draft.name}
        onChange={(e) => setDraft({ ...draft, name: e.target.value })}
        placeholder={tt('cards.cardName')}
        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md font-medium"
      />

      <div>
        <p className="text-sm font-medium text-gray-700 mb-1.5">{tt('cards.tags')}</p>
        <input
          type="text"
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
          placeholder={tt('cards.tagsPh')}
          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md"
        />
      </div>

      {CARD_FIELDS.map(([cat, field]) => {
        const options = sources.filter((s) => s.category === cat)
        return (
          <div key={cat}>
            <p className="text-sm font-medium text-gray-700 mb-1.5">
              {tt(`cards.cat.${cat}`)}
              {cat === 'continuation' && (
                <span className="font-normal text-xs text-amber-600 ml-2">{tt('cards.catHint.continuation')}</span>
              )}
            </p>
            {options.length === 0 ? (
              <p className="text-xs text-gray-400">{tt('cards.noSources')}</p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {options.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => toggle(field, s.id)}
                    className={`px-2.5 py-1 text-xs rounded-full border transition-colors ${
                      draft[field].includes(s.id)
                        ? 'bg-indigo-600 text-white border-indigo-600'
                        : 'bg-white text-gray-600 border-gray-300 hover:border-indigo-400'
                    }`}
                  >
                    {s.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        )
      })}

      <div>
        <p className="text-sm font-medium text-gray-700 mb-1.5">{tt('cards.extraReq')}</p>
        <textarea
          value={draft.extra_requirements}
          onChange={(e) => setDraft({ ...draft, extra_requirements: e.target.value })}
          placeholder={tt('cards.extraReqPh')}
          className="w-full h-20 px-3 py-2 text-sm border border-gray-300 rounded-md"
        />
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="flex gap-2">
        <button
          onClick={async () => {
            try {
              await onSave({ ...draft, tags: parseTags(tagsInput) })
            } catch (e) {
              setError(String(e.message || e))
            }
          }}
          className="px-4 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          {tt('cards.save')}
        </button>
        <button onClick={onCancel} className="px-4 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-md">
          {tt('cards.cancel')}
        </button>
      </div>
    </div>
  )
}

function CardPanel({ cards, sources, reload }) {
  const tt = useT()
  const [viewing, setViewing] = useState(null) // 点开的卡（弹窗展示）
  const [editing, setEditing] = useState(null) // 'new' | card object（弹窗内编辑）
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [tagFilter, setTagFilter] = useState('')

  const sourceName = (id) => sources.find((s) => s.id === id)?.name || id
  const allTags = [...new Set(cards.flatMap((c) => c.tags || []))]
  const filteredCards = tagFilter ? cards.filter((c) => (c.tags || []).includes(tagFilter)) : cards

  const save = async (draft) => {
    if (editing === 'new') await api.createCard(draft)
    else await api.updateCard(editing.id, draft)
    setEditing(null)
    setViewing(null)
    await reload()
  }

  const closeModal = () => { setViewing(null); setEditing(null) }

  return (
    <div>
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        {allTags.length > 0 && (
          <>
            <button
              onClick={() => setTagFilter('')}
              className={`px-2.5 py-1 text-xs rounded-full transition-colors ${
                tagFilter === '' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {tt('cards.allTags')}
            </button>
            {allTags.map((tag) => (
              <button
                key={tag}
                onClick={() => setTagFilter(tagFilter === tag ? '' : tag)}
                className={`px-2.5 py-1 text-xs rounded-full transition-colors ${
                  tagFilter === tag ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                #{tag}
              </button>
            ))}
          </>
        )}
        <div className="flex-1" />
        <button
          onClick={() => setEditing('new')}
          className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          + {tt('cards.newCard')}
        </button>
      </div>

      {filteredCards.length === 0 && (
        <p className="text-sm text-gray-400 py-10 text-center">{tt('cards.empty')}</p>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {filteredCards.map((c) => (
          <button
            key={c.id}
            onClick={() => setViewing(c)}
            className="text-left border border-gray-200 rounded-xl p-4 bg-gradient-to-br from-white to-indigo-50/40 shadow-sm hover:shadow-md hover:-translate-y-0.5 hover:border-indigo-300 transition-all"
          >
            <div className="flex items-start gap-2 mb-2">
              <h3 className="font-semibold text-gray-800 flex-1 leading-snug">{c.name}</h3>
              {c.builtin && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-100 text-purple-700 shrink-0">{tt('cards.builtin')}</span>
              )}
            </div>
            {(c.tags || []).length > 0 && (
              <div className="flex flex-wrap gap-1 mb-2">
                {c.tags.map((tag) => (
                  <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-100 text-indigo-700">#{tag}</span>
                ))}
              </div>
            )}
            <p className="text-xs text-gray-400">
              {CARD_FIELDS.filter(([, f]) => (c[f] || []).length > 0)
                .map(([cat]) => tt(`cards.cat.${cat}`))
                .join(' · ') || tt('cards.emptyPart')}
            </p>
          </button>
        ))}
      </div>

      {/* 中型弹窗：查看 / 编辑写作卡 */}
      <Modal open={!!viewing || !!editing} onClose={closeModal}>
        {editing ? (
          <>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {editing === 'new' ? tt('cards.newCard') : tt('cards.editCard')}
            </h2>
            <CardEditor
              card={editing === 'new' ? null : editing}
              sources={sources}
              onSave={save}
              onCancel={closeModal}
            />
          </>
        ) : viewing ? (
          <>
            <div className="flex items-start gap-2 mb-1">
              <h2 className="text-lg font-semibold text-gray-900 flex-1">{viewing.name}</h2>
              {viewing.builtin && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-100 text-purple-700">{tt('cards.builtin')}</span>
              )}
            </div>
            {(viewing.tags || []).length > 0 && (
              <div className="flex flex-wrap gap-1 mb-4">
                {viewing.tags.map((tag) => (
                  <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-100 text-indigo-700">#{tag}</span>
                ))}
              </div>
            )}
            <div className="space-y-3 mb-5">
              {CARD_FIELDS.map(([cat, field]) => (
                <div key={cat}>
                  <p className="text-xs font-medium text-gray-400 uppercase mb-1">{tt(`cards.cat.${cat}`)}</p>
                  {(viewing[field] || []).length > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {(viewing[field] || []).map((id) => (
                        <span key={id} className="px-2.5 py-1 text-xs rounded-full bg-gray-100 text-gray-700">
                          {sourceName(id)}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-gray-300">{tt('cards.emptyPart')}</p>
                  )}
                </div>
              ))}
              <div>
                <p className="text-xs font-medium text-gray-400 uppercase mb-1">{tt('cards.extraReq')}</p>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {viewing.extra_requirements || <span className="text-gray-300">{tt('cards.emptyPart')}</span>}
                </p>
              </div>
            </div>
            <div className="flex gap-2 justify-end border-t pt-4">
              {!viewing.builtin && (
                <button
                  onClick={() => setEditing(viewing)}
                  className="px-4 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                >
                  {tt('cards.edit')}
                </button>
              )}
              <button
                onClick={async () => { await api.duplicateCard(viewing.id); closeModal(); reload() }}
                className="px-4 py-1.5 text-sm border border-gray-300 text-gray-600 rounded-md hover:bg-gray-50"
              >
                {tt('cards.duplicate')}
              </button>
              {!viewing.builtin && (
                <button
                  onClick={() => setConfirmDelete(viewing)}
                  className="px-4 py-1.5 text-sm border border-red-200 text-red-500 rounded-md hover:bg-red-50"
                >
                  {tt('cards.delete')}
                </button>
              )}
              <button onClick={closeModal} className="px-4 py-1.5 text-sm text-gray-500 hover:bg-gray-100 rounded-md">
                {tt('cards.close')}
              </button>
            </div>
          </>
        ) : null}
      </Modal>

      <ConfirmModal
        isOpen={!!confirmDelete}
        danger
        title={tt('cards.delete')}
        message={tt('cards.deleteConfirm')}
        onConfirm={async () => {
          try { await api.deleteCard(confirmDelete.id) } catch (e) {}
          setConfirmDelete(null)
          closeModal()
          reload()
        }}
        onCancel={() => setConfirmDelete(null)}
      />
    </div>
  )
}

// ---------------- 页面 ----------------

function Cards() {
  const tt = useT()
  const [tab, setTab] = useState('cards')
  const [sources, setSources] = useState([])
  const [cards, setCards] = useState([])

  const reload = useCallback(async () => {
    try {
      const [s, c] = await Promise.all([api.listSources(), api.listCards()])
      setSources(Array.isArray(s) ? s : [])
      setCards(Array.isArray(c) ? c : [])
    } catch (e) {
      console.error(e)
    }
  }, [])

  useEffect(() => {
    reload()
    // 索引是后台任务，轮询刷新状态
    const timer = setInterval(() => {
      setSources((prev) => {
        if (prev.some((s) => s.index_status === 'indexing' || s.index_status === 'pending')) reload()
        return prev
      })
    }, 3000)
    return () => clearInterval(timer)
  }, [reload])

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">{tt('cards.title')}</h1>
      <p className="text-sm text-gray-500 mb-6">{tt('cards.subtitle')}</p>

      <div className="flex gap-1 border-b border-gray-200 mb-6">
        {['cards', 'sources'].map((tb) => (
          <button
            key={tb}
            onClick={() => setTab(tb)}
            className={`px-4 py-2 text-sm -mb-px border-b-2 transition-colors ${
              tab === tb
                ? 'border-indigo-600 text-indigo-600 font-medium'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tt(tb === 'cards' ? 'cards.tabCards' : 'cards.tabSources')}
          </button>
        ))}
      </div>

      {tab === 'sources' ? (
        <SourcePanel sources={sources} reload={reload} />
      ) : (
        <CardPanel cards={cards} sources={sources} reload={reload} />
      )}
    </div>
  )
}

export default Cards
