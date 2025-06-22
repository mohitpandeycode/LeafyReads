document.addEventListener('DOMContentLoaded', function () {
      const loaderOverlay = document.getElementById('loader-overlay')
      const mainContent = document.getElementById('container-wrapper')
      const prev = document.querySelector('.prev')
      const next = document.querySelector('.next')

      setTimeout(() => {

        loaderOverlay.classList.add('hidden')

        loaderOverlay.addEventListener(
          'transitionend',
          function () {
            if (loaderOverlay.classList.contains('hidden')) {
              loaderOverlay.remove()
              document.body.style.overflow = ''
              mainContent.classList.add('visible')
              prev.style.display="block"
              next.style.display="block"
            }
          },
          { once: true }
        )
        if (loaderOverlay.style.opacity === '0') {
          mainContent.classList.add('visible')
          loaderOverlay.remove()
          document.body.style.overflow = ''
        }
      }, 1500)
    })