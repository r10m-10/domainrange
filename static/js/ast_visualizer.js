setupExpressionInput('/api/ast-visualize', (data, resultDiv) => {
  resultDiv.innerHTML = data.svg;

  const downloadBtn = document.getElementById('download-svg-btn')
  downloadBtn.style.display = 'flex'
  downloadBtn.onclick = () => {
    const svgEl = resultDiv.querySelector('svg')
    if (!svgEl) return
    const blob = new Blob([svgEl.outerHTML], { type : 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'ast-tree.svg'
    a.click()
    URL.revokeObjectURL(url)
  }
});
setupToolNav('ast-visualizer')
setupTestButton('3x^2 + sin(x) - 5')