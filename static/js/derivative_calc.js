setupExpressionInput('/api/differentiate', (data, resultDiv) => {
  resultDiv.innerHTML = data.der;
});