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

const navSearch = document.getElementById("navSearch");
const navSearchBtn = document.getElementById("navSearchBtn");
const navSearchInput = document.getElementById("navSearchInput");

const expandedStyles = {
  background: "rgba(255, 255, 255, 0.3)",
  backdropFilter: "blur(8px)",
  borderRadius: "30px",
  padding: "6px 12px",
  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)"
};

const collapsedStyles = {
  background: "none",
  backdropFilter: "none",
  borderRadius: "0",
  padding: "0",
  boxShadow: "none"
};

function expandSearch() {
  navSearch.classList.add("expanded");
  Object.assign(navSearch.style, expandedStyles);
  navSearchInput.focus();
}

function collapseSearch() {
  navSearch.classList.remove("expanded");
  navSearchInput.value = "";
  Object.assign(navSearch.style, collapsedStyles);
}

// Toggle on icon click
navSearchBtn.addEventListener("click", () => {
  if (navSearch.classList.contains("expanded")) {
    collapseSearch();
  } else {
    expandSearch();
  }
});

// Collapse if clicked outside
document.addEventListener("click", (e) => {
  if (!navSearch.contains(e.target) && !navSearchBtn.contains(e.target)) {
    collapseSearch();
  }
});

