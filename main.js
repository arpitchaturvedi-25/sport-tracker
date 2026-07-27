// SportTracker — main.js
// Shared UI behaviour: mobile nav toggle, auto-dismiss flash messages

document.addEventListener("DOMContentLoaded", () => {
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");

  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });

    // Close menu when a link is clicked (mobile)
    navLinks.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => navLinks.classList.remove("open"));
    });
  }

  // Auto-dismiss flash messages after 5 seconds
  document.querySelectorAll(".flash").forEach((flash) => {
    setTimeout(() => {
      flash.style.transition = "opacity 0.4s ease";
      flash.style.opacity = "0";
      setTimeout(() => flash.remove(), 400);
    }, 5000);
  });
});
