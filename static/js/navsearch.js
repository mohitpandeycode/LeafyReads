
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
    sctive.style.display="none";
  } else {
    expandSearch();
    sctive.style.display="block";
  }
});


