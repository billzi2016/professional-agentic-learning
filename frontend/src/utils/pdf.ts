import dayjs from 'dayjs'

export async function exportElementToPdf(element: HTMLElement, title: string): Promise<void> {
  const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
    import('html2canvas'),
    import('jspdf'),
  ])
  const canvas = await html2canvas(element, {
    backgroundColor: '#ffffff',
    scale: 2,
    useCORS: true,
  })
  const pdf = new jsPDF('p', 'mm', 'a4')
  const pageWidth = pdf.internal.pageSize.getWidth()
  const pageHeight = pdf.internal.pageSize.getHeight()
  const imageWidth = pageWidth
  const imageHeight = (canvas.height * imageWidth) / canvas.width
  const image = canvas.toDataURL('image/png')

  let remaining = imageHeight
  let position = 0
  pdf.addImage(image, 'PNG', 0, position, imageWidth, imageHeight)
  remaining -= pageHeight

  while (remaining > 0) {
    position -= pageHeight
    pdf.addPage()
    pdf.addImage(image, 'PNG', 0, position, imageWidth, imageHeight)
    remaining -= pageHeight
  }

  const safeTitle = title.replace(/[^\p{L}\p{N}-]+/gu, '-').replace(/-+/g, '-')
  pdf.save(`${safeTitle || '学习记录'}-${dayjs().format('YYYY-MM-DD')}.pdf`)
}
