document.addEventListener("DOMContentLoaded", function () {
  const elements = document.querySelectorAll("[data-typed]");

  elements.forEach((el) => {
    const text = el.getAttribute("data-typed");
    const speed = parseInt(el.getAttribute("data-speed")) || 25;
    const delay = parseInt(el.getAttribute("data-delay")) || 0;
    let index = 0;

    function typeText() {
      if (index < text.length) {
        el.innerHTML = text.slice(0, index + 1);
        index++;
        setTimeout(typeText, speed);
      }
    }

    setTimeout(typeText, delay);
  });
});