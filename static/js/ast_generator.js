setupExpressionInput('/api/ast-generate', (data, resultDiv) => {
  resultDiv.textContent = data.node;
});