setupExpressionInput('/api/calculate-range', (data, resultDiv) => {
  resultDiv.innerHTML = data.range;
});