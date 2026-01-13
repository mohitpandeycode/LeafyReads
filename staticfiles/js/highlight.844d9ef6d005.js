let isHighlightMode = false;
const highlightBtn = document.getElementById("highlightBtn");
const click = new Audio("/static/sounds/click.mp3");

function toggleSelectionMode() {
  if (isHighlightMode) {
    document.body.classList.add("allow-selection");
  } else {
    document.body.classList.remove("allow-selection");
  }
}

// Toggle highlight mode on button click
highlightBtn.addEventListener("click", () => {
  click.currentTime = 0;
  click.play();

  isHighlightMode = !isHighlightMode;
  highlightBtn.style.backgroundColor = isHighlightMode ? "#f1c40f" : "#2c3e50";

  toggleSelectionMode();
});

// Toggle highlight mode with 'H' key
document.addEventListener("keydown", (e) => {
  if (e.key === "h" || e.key === "H") {
    click.currentTime = 0;
    click.play();

    isHighlightMode = !isHighlightMode;
    highlightBtn.style.backgroundColor = isHighlightMode ? "#f1c40f" : "#2c3e50";

    toggleSelectionMode();
  }
});

// Apply highlight on selected text
document.addEventListener("mouseup", () => {
  if (!isHighlightMode) return;

  const selection = window.getSelection();
  if (!selection.toString()) return;

  const range = selection.getRangeAt(0);
  const span = document.createElement("span");
  span.className = "highlighted";
  range.surroundContents(span);
  selection.removeAllRanges();
});