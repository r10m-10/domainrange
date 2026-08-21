setupExpressionInput('/api/ast-generate', (data, resultDiv) => {
  resultDiv.textContent = data.node;
});
setupToolNav('ast-generator')
setupTestButton('3x^2 + sin(x) - 5')