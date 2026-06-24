import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
})

function readCookie(name: string): string {
  const match = document.cookie
    .split('; ')
    .find((item) => item.startsWith(`${name}=`))
  return match ? decodeURIComponent(match.split('=').slice(1).join('=')) : ''
}

apiClient.interceptors.request.use((config) => {
  const method = config.method?.toUpperCase()
  if (method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    config.headers.set('X-CSRFToken', readCookie('csrftoken'))
  }
  return config
})

export async function initializeCsrf(): Promise<void> {
  await apiClient.get('/api/csrf')
}
