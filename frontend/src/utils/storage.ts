export function readNumber(key: string, fallback: number): number {
  const raw = localStorage.getItem(key)
  const value = raw ? Number(raw) : Number.NaN
  return Number.isFinite(value) ? value : fallback
}

export function writeNumber(key: string, value: number): void {
  localStorage.setItem(key, String(value))
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}
