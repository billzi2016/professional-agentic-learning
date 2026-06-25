import dayjs from 'dayjs'

function collectPageBreaks(root: HTMLElement, canvasHeight: number): number[] {
  const rootRect = root.getBoundingClientRect()
  const scale = canvasHeight / Math.max(root.scrollHeight, 1)
  const selectors = [
    '.message-row',
    '.quiz-card',
    '.message',
    '.markdown-body > h1',
    '.markdown-body > h2',
    '.markdown-body > h3',
    '.markdown-body > p',
    '.markdown-body > ul',
    '.markdown-body > ol',
    '.markdown-body > pre',
    '.markdown-body > blockquote',
  ]

  const breaks = new Set<number>([0, canvasHeight])
  root.querySelectorAll<HTMLElement>(selectors.join(',')).forEach((node) => {
    const rect = node.getBoundingClientRect()
    const bottom = Math.round((rect.bottom - rootRect.top) * scale)
    if (bottom > 0 && bottom < canvasHeight) {
      breaks.add(bottom)
    }
  })

  return [...breaks].sort((a, b) => a - b)
}

function findSafeSliceEnd(breaks: number[], start: number, hardEnd: number, canvasHeight: number): number {
  if (hardEnd >= canvasHeight) return canvasHeight

  const minimumUsefulSlice = 260
  const edgePadding = 40
  const candidates = breaks.filter((point) => point > start + minimumUsefulSlice && point <= hardEnd - edgePadding)
  return candidates.at(-1) ?? hardEnd
}

function cropCanvas(source: HTMLCanvasElement, sourceY: number, height: number): HTMLCanvasElement {
  const target = document.createElement('canvas')
  target.width = source.width
  target.height = height
  const context = target.getContext('2d')
  if (!context) {
    throw new Error('PDF 导出失败：无法创建分页画布')
  }
  context.drawImage(source, 0, sourceY, source.width, height, 0, 0, source.width, height)
  return target
}

export async function exportElementToPdf(element: HTMLElement, title: string): Promise<void> {
  const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
    import('html2canvas'),
    import('jspdf'),
  ])

  const exportNode = element.cloneNode(true) as HTMLElement
  exportNode.classList.add('pdf-export-surface')
  document.body.appendChild(exportNode)

  try {
    const canvas = await html2canvas(exportNode, {
      backgroundColor: '#ffffff',
      scale: 2,
      useCORS: true,
      windowWidth: 900,
    })

    const pdf = new jsPDF('p', 'mm', 'a4')
    const margin = 10
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const imageWidth = pageWidth - margin * 2
    const usablePageHeight = pageHeight - margin * 2
    const pageCanvasHeight = Math.floor((usablePageHeight * canvas.width) / imageWidth)
    const breaks = collectPageBreaks(exportNode, canvas.height)

    let sourceY = 0
    let pageIndex = 0
    while (sourceY < canvas.height) {
      const hardEnd = Math.min(sourceY + pageCanvasHeight, canvas.height)
      const sliceEnd = findSafeSliceEnd(breaks, sourceY, hardEnd, canvas.height)
      const sliceHeight = sliceEnd - sourceY
      const pageCanvas = cropCanvas(canvas, sourceY, sliceHeight)
      const pageImage = pageCanvas.toDataURL('image/png')
      const pageImageHeight = (sliceHeight * imageWidth) / canvas.width

      if (pageIndex > 0) {
        pdf.addPage()
      }
      pdf.addImage(pageImage, 'PNG', margin, margin, imageWidth, pageImageHeight)

      sourceY = sliceEnd
      pageIndex += 1
    }

    const safeTitle = title.replace(/[^\p{L}\p{N}-]+/gu, '-').replace(/-+/g, '-')
    pdf.save(`${safeTitle || '学习记录'}-${dayjs().format('YYYY-MM-DD')}.pdf`)
  } finally {
    exportNode.remove()
  }
}
