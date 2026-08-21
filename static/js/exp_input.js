function setupExpressionInput(endpoint, onSuccess, onError) {
  const input = document.getElementById('exp-input')
  const resultDiv = document.getElementById('result')
  let debounceTimer = null

  input.addEventListener('input', () => {
    clearTimeout(debounceTimer)
    const exp = input.value.trim()

    if (exp === '') {
      resultDiv.innerHTML = ''
      return
    }

    debounceTimer = setTimeout(() => {
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression: exp })
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            onSuccess(data, resultDiv)
          } else {
            if (onError) {
              onError(data.error, resultDiv)
            } else {
              resultDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`
            }
          }
        })
        .catch(err => {
          resultDiv.innerHTML = `<p style="color:red;">Request failed: ${err}</p>`
        })
    }, 300)
  })
}