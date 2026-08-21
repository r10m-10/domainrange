setupExpressionInput('/api/calculate-domain', (data, resultDiv) => {
  resultDiv.innerHTML = data.domain;
});