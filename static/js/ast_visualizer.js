setupExpressionInput('/api/ast-visualize', (data, resultDiv) => {
  resultDiv.innerHTML = data.svg;
});
setupToolNav('ast-visualizer')
setupTestButton('3x^2 + sin(x) - 5')