import { defineStore } from 'pinia'

import { clamp, readNumber, writeNumber } from '../utils/storage'

const SIDEBAR_KEY = 'learning.sidebar.width'
const INPUT_KEY = 'learning.input.height'

export const useLayoutStore = defineStore('layout', {
  state: () => ({
    sidebarWidth: readNumber(SIDEBAR_KEY, 280),
    inputHeight: readNumber(INPUT_KEY, 120),
  }),
  actions: {
    setSidebarWidth(width: number) {
      this.sidebarWidth = clamp(width, 220, 420)
      writeNumber(SIDEBAR_KEY, this.sidebarWidth)
    },
    setInputHeight(height: number) {
      this.inputHeight = clamp(height, 80, 320)
      writeNumber(INPUT_KEY, this.inputHeight)
    },
  },
})
