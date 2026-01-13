window.addEventListener('load', function () {
  const loaderOverlay = document.getElementById('loader-overlay')
  const mainContent = document.getElementById('container-wrapper')
  const prev = document.querySelector('.prev')
  const next = document.querySelector('.next')

  loaderOverlay.classList.add('hidden')

  loaderOverlay.addEventListener(
    'transitionend',
    function () {
      if (loaderOverlay.classList.contains('hidden')) {
        loaderOverlay.remove()
        document.body.style.overflow = ''
        mainContent.classList.add('visible')
        prev.style.display = "block"
        next.style.display = "block"
      }
    },
    { once: true }
  )
})
