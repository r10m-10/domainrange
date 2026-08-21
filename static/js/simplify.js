setupExpressionInput('/api/simplify', (data, resultDiv) => {
  resultDiv.innerHTML = data.sim;
});
setupToolNav('simplify')
setupTestButton('2x + 3x - x^0 + 0')