setupExpressionInput('/api/domain', (data, resultDiv) => {
  resultDiv.innerHTML = data.domain;
});
setupToolNav('domain')
setupTestButton('1 / (x^2 - 4) + sqrt(x - 1)')