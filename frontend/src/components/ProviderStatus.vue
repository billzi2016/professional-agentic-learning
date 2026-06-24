<script setup lang="ts">
import { Activity, RefreshCw } from '@lucide/vue'
import { computed } from 'vue'

import { useProviderStore } from '../stores/provider'

const provider = useProviderStore()

const label = computed(() => {
  if (!provider.status) return 'provider: checking'
  return `provider: ${provider.status.provider}`
})
</script>

<template>
  <button class="provider-status" type="button" @click="provider.check">
    <span class="status-dot" :class="provider.status?.status ?? 'checking'" />
    <Activity :size="16" aria-hidden="true" />
    <span>{{ label }}</span>
    <small>{{ provider.status?.model ?? 'model checking' }}</small>
    <RefreshCw :size="14" :class="{ spinning: provider.loading }" aria-hidden="true" />
  </button>
</template>
