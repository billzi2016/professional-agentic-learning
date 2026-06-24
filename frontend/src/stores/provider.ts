import { defineStore } from 'pinia'

import { checkProviderHealth, getProviderStatus } from '../api/provider'
import type { ProviderStatus } from '../types'

export const useProviderStore = defineStore('provider', {
  state: () => ({
    status: null as ProviderStatus | null,
    loading: false,
    heartbeatId: 0 as number,
  }),
  actions: {
    async load() {
      this.loading = true
      try {
        this.status = await getProviderStatus()
      } finally {
        this.loading = false
      }
    },
    async check() {
      this.loading = true
      try {
        this.status = await checkProviderHealth()
      } finally {
        this.loading = false
      }
    },
    startHeartbeat() {
      if (this.heartbeatId) return

      // Provider 状态应该是自动心跳，不依赖用户手工点击。
      // 首次进入页面立即实测一次，后续定时检查，让红绿灯反映真实模型状态。
      void this.check()
      this.heartbeatId = window.setInterval(() => {
        void this.check()
      }, 30_000)
    },
    stopHeartbeat() {
      if (!this.heartbeatId) return
      window.clearInterval(this.heartbeatId)
      this.heartbeatId = 0
    },
  },
})
