import { fetchEventSource } from '@microsoft/fetch-event-source'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

function readCookie(name: string): string {
  const match = document.cookie
    .split('; ')
    .find((item) => item.startsWith(`${name}=`))
  return match ? decodeURIComponent(match.split('=').slice(1).join('=')) : ''
}

export interface StreamHandlers {
  onEvent: (event: string, data: Record<string, unknown>) => void
  onError: (message: string) => void
}

export function streamApi(path: string, body: Record<string, unknown>, signal: AbortSignal, handlers: StreamHandlers) {
  return fetchEventSource(`${API_BASE_URL}${path}`, {
    method: 'POST',
    credentials: 'include',
    signal,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': readCookie('csrftoken'),
    },
    body: JSON.stringify(body),
    onmessage(message) {
      try {
        handlers.onEvent(message.event, JSON.parse(message.data))
      } catch {
        handlers.onError('无法解析服务器返回的流式数据')
      }
    },
    onerror(error) {
      handlers.onError(error instanceof Error ? error.message : '流式连接失败')
      throw error
    },
  })
}
