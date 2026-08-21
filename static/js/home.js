const input = document.getElementById('exp-input');
const buttonsDiv = document.getElementById('tool-buttons');
let debounceTimer = null;

TOOLS.forEach(t => {
  const btn = document.createElement('button');
  btn.textContent = t.label;
  btn.disabled = true;
  btn.addEventListener('click', () => {
    const exp = encodeURIComponent(input.value.trim());
    window.location.href = `${t.path}?exp=${exp}`;
  });
  buttonsDiv.appendChild(btn);
});

input.addEventListener('input', () => {
  clearTimeout(debounceTimer);
  const expression = input.value.trim();
  if (!expression) {
    buttonsDiv.querySelectorAll('button').forEach(b => b.disabled = true);
    return;
  }
  debounceTimer = setTimeout(() => {
    fetch('/api/ast-generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expression })
    })
      .then(res => res.json())
      .then(data => {
        buttonsDiv.querySelectorAll('button').forEach(b => b.disabled = !data.success);
      });
  }, 300);
});