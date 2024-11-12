document.addEventListener("DOMContentLoaded", function() {
  // Split text into parts, with the styled part wrapped in a <span>
  const text = `Track the latest recent price movements across major <span class="as-h1">asset classes</span>.`;
  const textContainer = document.querySelector(".page-introduction");

  let index = 0;
  function typeText() {
    if (index < text.length) {
      textContainer.innerHTML = text.slice(0, index + 1); // Add one character at a time
      index++;
      setTimeout(typeText, 20); // Adjust speed here
    }
  }

  typeText(); // Start the typing animation
});
