import { create } from 'zustand'

const useStore = create((set) => ({
  books: [],
  currentBook: null,
  generating: false,
  outline: null,
  chapters: [],
  
  setBooks: (books) => set({ books }),
  setCurrentBook: (book) => set({ currentBook: book }),
  setGenerating: (generating) => set({ generating }),
  setOutline: (outline) => set({ outline }),
  addChapter: (chapter) => set((state) => ({ chapters: [...state.chapters, chapter] })),
  resetGeneration: () => set({ generating: false, outline: null, chapters: [] })
}))

export default useStore
