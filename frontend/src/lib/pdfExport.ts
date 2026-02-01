/**
 * Session 896: PDF Export Utility
 *
 * Generates professional PDF documents from initiative stage documents.
 * Uses jsPDF for client-side PDF generation.
 */

import { jsPDF } from 'jspdf'

interface DocumentData {
  title?: string
  content: string
  stageName?: string
  initiativeName?: string
  wordCount?: number
  createdAt?: string
  status?: string
}

/**
 * Generate a professional PDF from document content
 */
export function generateDocumentPDF(doc: DocumentData): void {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  })

  const pageWidth = pdf.internal.pageSize.getWidth()
  const pageHeight = pdf.internal.pageSize.getHeight()
  const margin = 20
  const contentWidth = pageWidth - margin * 2
  let yPosition = margin

  // Colors
  const primaryColor: [number, number, number] = [99, 102, 241] // Indigo
  const textColor: [number, number, number] = [31, 41, 55] // Dark gray
  const lightGray: [number, number, number] = [107, 114, 128]

  // Header bar
  pdf.setFillColor(...primaryColor)
  pdf.rect(0, 0, pageWidth, 25, 'F')

  // Header text
  pdf.setTextColor(255, 255, 255)
  pdf.setFontSize(10)
  pdf.setFont('helvetica', 'normal')
  pdf.text('DONKEY BETZ PLATFORM', margin, 10)

  if (doc.stageName) {
    pdf.setFontSize(8)
    pdf.text(doc.stageName.toUpperCase(), margin, 17)
  }

  // Date on right
  const dateStr = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
  pdf.setFontSize(8)
  const dateWidth = pdf.getTextWidth(dateStr)
  pdf.text(dateStr, pageWidth - margin - dateWidth, 17)

  yPosition = 40

  // Document title
  if (doc.title) {
    pdf.setTextColor(...textColor)
    pdf.setFontSize(18)
    pdf.setFont('helvetica', 'bold')

    // Word wrap title
    const titleLines = pdf.splitTextToSize(doc.title, contentWidth)
    pdf.text(titleLines, margin, yPosition)
    yPosition += titleLines.length * 8 + 5
  }

  // Initiative name if different from title
  if (doc.initiativeName && doc.initiativeName !== doc.title) {
    pdf.setTextColor(...lightGray)
    pdf.setFontSize(10)
    pdf.setFont('helvetica', 'italic')
    pdf.text(`Initiative: ${doc.initiativeName}`, margin, yPosition)
    yPosition += 8
  }

  // Metadata line
  const metadata: string[] = []
  if (doc.wordCount) metadata.push(`${doc.wordCount.toLocaleString()} words`)
  if (doc.createdAt) {
    const created = new Date(doc.createdAt).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
    metadata.push(`Created: ${created}`)
  }
  if (doc.status) metadata.push(`Status: ${doc.status}`)

  if (metadata.length > 0) {
    pdf.setTextColor(...lightGray)
    pdf.setFontSize(9)
    pdf.setFont('helvetica', 'normal')
    pdf.text(metadata.join('  |  '), margin, yPosition)
    yPosition += 10
  }

  // Divider line
  pdf.setDrawColor(...lightGray)
  pdf.setLineWidth(0.3)
  pdf.line(margin, yPosition, pageWidth - margin, yPosition)
  yPosition += 10

  // Main content
  pdf.setTextColor(...textColor)
  pdf.setFontSize(11)
  pdf.setFont('helvetica', 'normal')

  // Process content - handle markdown-like formatting
  const content = doc.content || 'No content available'
  const lines = content.split('\n')

  for (const line of lines) {
    // Check for page break
    if (yPosition > pageHeight - margin - 20) {
      pdf.addPage()
      yPosition = margin

      // Mini header on continuation pages
      pdf.setTextColor(...lightGray)
      pdf.setFontSize(8)
      pdf.text(doc.title || 'Document', margin, yPosition)
      yPosition += 10
      pdf.setTextColor(...textColor)
      pdf.setFontSize(11)
    }

    // Handle headers (# ## ###)
    if (line.startsWith('### ')) {
      yPosition += 4
      pdf.setFontSize(12)
      pdf.setFont('helvetica', 'bold')
      const headerText = line.replace(/^###\s*/, '')
      const wrappedLines = pdf.splitTextToSize(headerText, contentWidth)
      pdf.text(wrappedLines, margin, yPosition)
      yPosition += wrappedLines.length * 5 + 3
      pdf.setFontSize(11)
      pdf.setFont('helvetica', 'normal')
    } else if (line.startsWith('## ')) {
      yPosition += 6
      pdf.setFontSize(13)
      pdf.setFont('helvetica', 'bold')
      const headerText = line.replace(/^##\s*/, '')
      const wrappedLines = pdf.splitTextToSize(headerText, contentWidth)
      pdf.text(wrappedLines, margin, yPosition)
      yPosition += wrappedLines.length * 5.5 + 4
      pdf.setFontSize(11)
      pdf.setFont('helvetica', 'normal')
    } else if (line.startsWith('# ')) {
      yPosition += 8
      pdf.setFontSize(14)
      pdf.setFont('helvetica', 'bold')
      const headerText = line.replace(/^#\s*/, '')
      const wrappedLines = pdf.splitTextToSize(headerText, contentWidth)
      pdf.text(wrappedLines, margin, yPosition)
      yPosition += wrappedLines.length * 6 + 5
      pdf.setFontSize(11)
      pdf.setFont('helvetica', 'normal')
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      // Bullet points
      const bulletText = line.replace(/^[-*]\s*/, '')
      const wrappedLines = pdf.splitTextToSize(bulletText, contentWidth - 6)
      pdf.text('\u2022', margin, yPosition)
      pdf.text(wrappedLines, margin + 6, yPosition)
      yPosition += wrappedLines.length * 5 + 1
    } else if (line.match(/^\d+\.\s/)) {
      // Numbered lists
      const match = line.match(/^(\d+\.)\s*(.*)/)
      if (match) {
        const [, num, text] = match
        const wrappedLines = pdf.splitTextToSize(text, contentWidth - 8)
        pdf.text(num, margin, yPosition)
        pdf.text(wrappedLines, margin + 8, yPosition)
        yPosition += wrappedLines.length * 5 + 1
      }
    } else if (line.trim() === '') {
      // Empty line - paragraph break
      yPosition += 4
    } else if (line.startsWith('**') && line.endsWith('**')) {
      // Bold text
      pdf.setFont('helvetica', 'bold')
      const boldText = line.replace(/\*\*/g, '')
      const wrappedLines = pdf.splitTextToSize(boldText, contentWidth)
      pdf.text(wrappedLines, margin, yPosition)
      yPosition += wrappedLines.length * 5 + 1
      pdf.setFont('helvetica', 'normal')
    } else {
      // Regular paragraph
      // Remove inline markdown formatting for PDF
      const cleanLine = line
        .replace(/\*\*([^*]+)\*\*/g, '$1')  // Bold
        .replace(/\*([^*]+)\*/g, '$1')       // Italic
        .replace(/`([^`]+)`/g, '$1')         // Code
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // Links

      const wrappedLines = pdf.splitTextToSize(cleanLine, contentWidth)
      pdf.text(wrappedLines, margin, yPosition)
      yPosition += wrappedLines.length * 5 + 1
    }
  }

  // Footer
  const totalPages = pdf.getNumberOfPages()
  for (let i = 1; i <= totalPages; i++) {
    pdf.setPage(i)
    pdf.setFontSize(8)
    pdf.setTextColor(...lightGray)

    // Page number
    pdf.text(
      `Page ${i} of ${totalPages}`,
      pageWidth / 2,
      pageHeight - 10,
      { align: 'center' }
    )

    // Generated by
    pdf.text(
      'Generated by Donkey Betz Platform',
      margin,
      pageHeight - 10
    )
  }

  // Generate filename
  const filename = generateFilename(doc.title || doc.stageName || 'document')

  // Download
  pdf.save(filename)
}

/**
 * Generate a safe filename from document title
 */
function generateFilename(title: string): string {
  const safeName = title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 50)

  const date = new Date().toISOString().split('T')[0]
  return `${safeName}-${date}.pdf`
}
