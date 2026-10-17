// A small confetti burst that ships with parrot, so it works on the island too.
window.confetti = function confetti() {
  for (let i = 0; i < 24; i += 1) {
    const bit = document.createElement('span')
    bit.className = 'confetti'
    bit.textContent = ['🦜', '🌴', '🎉', '🏝️'][i % 4]
    bit.style.left = `${Math.random() * 100}vw`
    bit.style.animationDelay = `${Math.random() * 0.4}s`
    document.body.appendChild(bit)
    setTimeout(() => bit.remove(), 2200)
  }
}
