setupExpressionInput('/api/differentiate', (data, resultDiv) => {
  resultDiv.innerHTML = data.der;
});
setupToolNav('differentiate')
setupTestButton('3x^2 + sin(x) - 5')