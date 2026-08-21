setupExpressionInput('/api/range', (data, resultDiv) => {
  resultDiv.innerHTML = data.range;
});
setupToolNav('range')
setupTestButton('1 / (x^2 - 4) + sqrt(x - 1)')