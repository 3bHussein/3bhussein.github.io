document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".v3-menu-toggle");
  const mobile = document.getElementById("v3MobileNav");
  const headerLinks = document.querySelectorAll(".v3-nav a, .v3-mobile-nav a");
  if (!toggle || !mobile) return;

  function closeMenu(restoreFocus = false) {
    mobile.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open menu");
    if (restoreFocus) toggle.focus();
  }
  toggle.addEventListener("click", () => {
    const shouldOpen = mobile.hidden;
    mobile.hidden = !shouldOpen;
    toggle.setAttribute("aria-expanded", String(shouldOpen));
    toggle.setAttribute("aria-label", shouldOpen ? "Close menu" : "Open menu");
  });
  mobile.querySelectorAll("a").forEach(link =>
    link.addEventListener("click", () => closeMenu())
  );
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !mobile.hidden) closeMenu(true);
  });
  document.addEventListener("click", event => {
    if (!mobile.hidden && !mobile.contains(event.target) && !toggle.contains(event.target)) closeMenu();
  });
  window.addEventListener("resize", () => {
    if (window.innerWidth > 900) closeMenu();
  });
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      headerLinks.forEach(link => {
        const active = link.getAttribute("href") === "#" + entry.target.id;
        link.classList.toggle("is-active", active);
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    });
  }, { rootMargin: "-18% 0px -65% 0px", threshold: 0 });
  document.querySelectorAll("section.resume-section[id]").forEach(section => observer.observe(section));
});
