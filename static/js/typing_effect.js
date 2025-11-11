document.addEventListener("DOMContentLoaded", function() {
  // Split text into parts, with the styled part wrapped in a <span>
  const text = `Real-time insight. One glance. All major asset classes.`;
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
