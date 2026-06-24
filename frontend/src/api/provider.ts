import { apiClient } from './client'
import type { ProviderStatus } from '../types'

export async function getProviderStatus(): Promise<ProviderStatus> {
  const { data } = await apiClient.get<ProviderStatus>('/api/provider/status')
  return data
}

export async function checkProviderHealth(): Promise<ProviderStatus> {
  const { data } = await apiClient.post<ProviderStatus>('/api/provider/health-check')
  return data
}
