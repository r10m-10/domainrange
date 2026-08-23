const TOOLS = [
  { key: 'ast-generator', label: 'Generate AST', path:'/ast-generator' },
  { key: 'ast-visualizer', label: 'Visualize AST', path:'/ast-visualizer' },
  { key: 'domain', label: 'Domain', path:'/domain' },
  { key: 'range', label: 'Range', path:'/range' },
  { key: 'differentiate', label: 'Derivative', path:'/differentiate' },
  { key: 'simplify', label: 'Simplify', path:'/simplify' }
]

function setupExpressionInput(endpoint, onSuccess, onError) {
  const input = document.getElementById('exp-input')
  const resultDiv = document.getElementById('result')
  let debounceTimer = null

  function runFetch(exp) {
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
        resultDiv.innerHTML = `<p style="color:red;>Request Failed: ${err}</p>`
      })
  }

  input.addEventListener('input', () => {
    clearTimeout(debounceTimer)
    const exp = input.value.trim()

    if (exp === '') {
      resultDiv.innerHTML = ''
      return
    }
    debounceTimer = setTimeout(() => runFetch(exp), 300)
  })

  const prefill = new URLSearchParams(window.location.search).get('exp')
  if (prefill) {
    input.value = prefill
    runFetch(prefill)
  }
}

function setupToolNav(currentToolKey) {
  const nav = document.getElementById('tool-nav')
  const input = document.getElementById('exp-input')
  if (!nav) return

  TOOLS.filter(t => t.key !== currentToolKey).forEach(t => {
    const btn = document.createElement('button')
    btn.textContent = t.label
    btn.addEventListener('click', () => {
      const exp = encodeURIComponent(input.value.trim())
      window.location.href = `${t.path}?exp=${exp}`
    })
    nav.appendChild(btn)
  })

  function toggleNav() {
    nav.style.display= input.value.trim() === '' ? 'none' : 'flex'
  }

  toggleNav()
  input.addEventListener('input', toggleNav)
}

function setupTestButton(sampleExpression) {
  const btn = document.getElementById('test-btn')
  const input = document.getElementById('exp-input')
  if (!btn) return

  btn.addEventListener('click', () => {
    input.value = sampleExpression
    input.dispatchEvent(new Event('input'))
  })
}