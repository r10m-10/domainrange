setupExpressionInput('/api/ast-visualize', (data, resultDiv) => {
  resultDiv.innerHTML = data.svg;
});