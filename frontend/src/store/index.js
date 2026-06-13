import { create } from 'zustand'
import { api } from '../api'

// 音效开关：默认关闭，持久化到 localStorage
const SOUND_KEY = 'bookbook.soundEnabled'
const readSoundEnabled = () => {
  try {
    return localStorage.getItem(SOUND_KEY) === 'true'
  } catch {
    return false
  }
}

const useStore = create((set, get) => ({
  books: [],
  currentBook: null,
  generating: false,
  outline: null,
  chapters: [],
  activeModel: null,
  providersLoaded: false,
  soundEnabled: readSoundEnabled(),

  setSoundEnabled: (enabled) => {
    try { localStorage.setItem(SOUND_KEY, enabled ? 'true' : 'false') } catch {}
    set({ soundEnabled: enabled })
  },
  toggleSound: () => {
    const next = !get().soundEnabled
    try { localStorage.setItem(SOUND_KEY, next ? 'true' : 'false') } catch {}
    set({ soundEnabled: next })
  },

  setBooks: (books) => set({ books }),
  setCurrentBook: (book) => set({ currentBook: book }),
  setGenerating: (generating) => set({ generating }),
  setOutline: (outline) => set({ outline }),
  addChapter: (chapter) => set((state) => ({ chapters: [...state.chapters, chapter] })),
  resetGeneration: () => set({ generating: false, outline: null, chapters: [] }),

  loadActiveModel: async () => {
    try {
      const data = await api.getActiveModel()
      set({ activeModel: data.active, providersLoaded: true })
    } catch {
      set({ providersLoaded: true })
    }
  },

  setActiveModel: (model) => set({ activeModel: model }),
}))

export default useStore