document.addEventListener('DOMContentLoaded', () => {
  document.querySelector('#show-ingredient-form').addEventListener('click', event => {
    event.preventDefault()
    document.querySelector('#ingredient-form').classList.remove('dn')
    document.querySelector('#id_amount').focus()
  })

  document.querySelector('#show-step-form').addEventListener('click', event => {
    event.preventDefault()
    document.querySelector('#step-form').classList.remove('dn')
    document.querySelector('#id_text').focus()
  })
})
