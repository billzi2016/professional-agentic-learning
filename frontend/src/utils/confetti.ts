import confetti from 'canvas-confetti'

export function fireSuccessConfetti(): void {
  void confetti({
    particleCount: 120,
    spread: 72,
    origin: { y: 0.72 },
    colors: ['#0f766e', '#2563eb', '#f59e0b', '#ef4444'],
  })
}
