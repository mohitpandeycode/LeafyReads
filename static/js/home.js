lucide.createIcons();
const themeToggleBtn = document.getElementById("theme-toggle");
const body = document.body;
const setTheme = (theme) => {
  if (theme === "dark") {
    body.classList.add("dark-mode");
    themeToggleBtn.innerHTML = '<i data-lucide="moon"></i>';
  } else {
    body.classList.remove("dark-mode");
    themeToggleBtn.innerHTML = '<i data-lucide="sun"></i>';
  }
  themeToggleBtn.classList.toggle("toggled", theme === "dark");
  lucide.createIcons();
};
const savedTheme = localStorage.getItem("theme");
if (savedTheme) {
  setTheme(savedTheme);
} else {
  setTheme("light");
}
themeToggleBtn.addEventListener("click", () => {
  if (body.classList.contains("dark-mode")) {
    setTheme("light");
    localStorage.setItem("theme", "light");
  } else {
    setTheme("dark");
    localStorage.setItem("theme", "dark");
  }
});
