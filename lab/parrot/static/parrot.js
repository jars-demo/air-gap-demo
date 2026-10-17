const says = document.getElementById('says')

async function squawk(mood) {
  const response = await fetch(`/api/squawk?mood=${mood}`)
  const body = await response.json()
  says.textContent = body.says ?? `(${body.error})`
  if (response.ok && window.confetti) window.confetti()
}

for (const button of document.querySelectorAll('[data-mood]')) {
  button.addEventListener('click', () => squawk(button.dataset.mood))
}
squawk('happy')
