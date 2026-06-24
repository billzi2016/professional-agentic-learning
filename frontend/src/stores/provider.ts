import { defineStore } from 'pinia'

import { checkProviderHealth, getProviderStatus } from '../api/provider'
import type { ProviderStatus } from '../types'

export const useProviderStore = defineStore('provider', {
  state: () => ({
    status: null as ProviderStatus | null,
    loading: false,
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
  },
})
