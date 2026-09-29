(function () {
  'use strict'

  function initAudioExamples() {
    document.querySelectorAll('.ae-container').forEach(function (container) {
      var toggleBtn = container.querySelector('.ae-toggle-btn')
      var translations = container.querySelectorAll('.ae-en')
      var translationsVisible = false

      if (toggleBtn) {
        toggleBtn.addEventListener('click', function () {
          translationsVisible = !translationsVisible
          translations.forEach(function (el) {
            el.classList.toggle('ae-hidden', !translationsVisible)
          })
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
