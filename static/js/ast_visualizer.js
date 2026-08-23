setupExpressionInput('/api/ast-visualize', (data, resultDiv) => {
  resultDiv.innerHTML = data.svg;

  const downloadBtn = document.getElementById('download-svg-btn')
  downloadBtn.style.display = 'flex'
});
setupToolNav('ast-visualizer')
setupTestButton('3x^2 + sin(x) - 5')