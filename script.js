const toggle = document.getElementById("langToggle");
let currentLang = "en";

function setLanguage(lang) {
  currentLang = lang;
  document.documentElement.lang = lang;

  document.querySelectorAll("[data-en][data-id]").forEach((element) => {
    const key = lang === "en" ? "data-en" : "data-id";
    const value = element.getAttribute(key);
    if (value !== null) {
      element.textContent = value;
    }
  });

  toggle.textContent = lang === "en" ? "ID" : "EN";
  toggle.setAttribute(
    "aria-label",
    lang === "en" ? "Ganti ke Bahasa Indonesia" : "Switch to English"
  );
}

toggle.addEventListener("click", () => {
  setLanguage(currentLang === "en" ? "id" : "en");
});

setLanguage("en");
