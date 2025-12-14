lucide.createIcons();

const themeToggleBtns = document.querySelectorAll(".theme-toggle-handler");
const body = document.body;

const setTheme = (theme) => {
    // 1. Apply the dark-mode class to the body
    if (theme === "dark") {
        body.classList.add("dark-mode");
    } else {
        body.classList.remove("dark-mode");
    }

    // 2. Update the icon and toggle class for ALL theme buttons
    themeToggleBtns.forEach(btn => {
        if (theme === "dark") {
            btn.innerHTML = '<i data-lucide="moon"></i>';
        } else {
            btn.innerHTML = '<i data-lucide="sun"></i>';
        }
        btn.classList.toggle("toggled", theme === "dark");
    });
    
    // Re-create lucide icons for the newly set icons
    lucide.createIcons(); 
};

// Check for saved theme and apply it
const savedTheme = localStorage.getItem("theme");
if (savedTheme) {
    setTheme(savedTheme);
} else {
    setTheme("light");
}

// Add event listener to ALL theme buttons
themeToggleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        if (body.classList.contains("dark-mode")) {
            setTheme("light");
            localStorage.setItem("theme", "light");
        } else {
            setTheme("dark");
            localStorage.setItem("theme", "dark");
        }
    });
});