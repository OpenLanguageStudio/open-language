(function () {
  'use strict'

  function initAudioExamples() {
    document.querySelectorAll('.ae-container').forEach(function (container) {
      var toggleBtn = container.querySelector('.ae-toggle-btn')
      var list = container.querySelector('.ae-list')
      var translationsVisible = false

      if (toggleBtn && list) {
        toggleBtn.addEventListener('click', function () {
          translationsVisible = !translationsVisible
          list.classList.toggle('ae-hidden', !translationsVisible)
          toggleBtn.textContent = translationsVisible
            ? 'Hide Translations'
            : 'Show Translations'
        })
      }
    })
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAudioExamples)
  } else {
    initAudioExamples()
  }
})()
