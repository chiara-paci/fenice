var invalidClassName = 'invalid';
var inputs = document.querySelectorAll('input, select, textarea');
inputs.forEach(function (input) {
  // Add a css class on submit when the input is invalid.
  input.addEventListener('invalid', function () {
    input.classList.add(invalidClassName)
  })

  // Remove the class when the input becomes valid.
  // 'input' will fire each time the user types
  input.addEventListener('input', function () {
    if (input.validity.valid) {
      input.classList.remove(invalidClassName)
    }
  })
})
