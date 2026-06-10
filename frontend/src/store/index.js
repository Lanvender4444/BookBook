import { create } from 'zustand'
import { api } from '../api'

const useStore = create((set, get) => ({
  books: [],
  currentBook: null,
  generating: false,
  outline: null,
  chapters: [],
  activeModel: null,
  providersLoaded: false,

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